from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.store import Store
from app.models.product import Product
from app.utils.dependencies import get_current_user
from app.models.user import User
from app.services.ai_service import generate_sales_response
from app.models.conversation import Conversation
from app.services.tts_service import generate_tts_audio
from app.utils.subscription import is_store_active


router = APIRouter(prefix="/chat", tags=["AI Salesman"])


@router.post("/")
def chat_with_salesman(
    message: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    store = db.query(Store).filter(Store.owner_id == current_user.id).first()

    if not store:
        raise HTTPException(status_code=400, detail="No store found")

    products = db.query(Product).filter(Product.store_id == store.id).all()

    product_info = "\n".join([
        f"- {p.name} – ₹{p.price} – {p.description}"
        for p in products
    ])

    prompt = f"""
Store Name: {store.name}

Available Products:
{product_info}

Customer says:
{message}

Respond in persuasive Hindi and suggest relevant products.
"""

    ai_response = generate_sales_response(prompt)

    return {"response": ai_response}


from app.schemas.chat import ChatRequest

@router.post("/public/{store_id}")
async def public_chat(
    store_id: int,
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    message = request.message

    # 🔎 Find store first
    store = db.query(Store).filter(Store.id == store_id).first()

    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    # 🔐 Check subscription AFTER confirming store exists
    if not is_store_active(store):
        raise HTTPException(
            status_code=403,
            detail="Store subscription expired. Service unavailable."
        )

    # 📦 Get products
    products = db.query(Product).filter(Product.store_id == store.id).all()

    if not products:
        return {
            "response": "इस समय कोई उत्पाद उपलब्ध नहीं है। कृपया बाद में पुनः प्रयास करें।"
        }

    product_info = "\n".join([
        f"- {p.name} – ₹{p.price} – {p.description}"
        for p in products if p.is_available
    ])

    prompt = f"""
Store Name: {store.name}

Available Products:
{product_info}

Customer says:
{message}

Respond in persuasive Hindi and suggest relevant products.
"""

    ai_response = generate_sales_response(prompt)

    # 🔥 Intent Detection
    intent = "BROWSING"
    lead_score = 20
    mentioned_product = None
    lower_msg = message.lower()

    if "खरीद" in lower_msg or "लेना" in lower_msg or "बुक" in lower_msg:
        intent = "BUYING"
        lead_score = 85

    elif "सस्ता" in lower_msg or "कम" in lower_msg or "डिस्काउंट" in lower_msg:
        intent = "PRICE_SENSITIVE"
        lead_score = 60

    elif "देख" in lower_msg or "जानकारी" in lower_msg:
        intent = "EXPLORING"
        lead_score = 40

    for p in products:
        if p.name.lower() in lower_msg:
            mentioned_product = p.name

    # 💾 Save conversation
    conversation = Conversation(
        store_id=store.id,
        customer_message=message,
        ai_response=ai_response,
        intent=intent,
        mentioned_product=mentioned_product,
        lead_score=lead_score
    )

    db.add(conversation)
    db.commit()

    # 📧 Hot Lead Email Trigger
    from app.services.email_service import send_hot_lead_email
    import asyncio

    if lead_score >= 80 and store.email:
        asyncio.create_task(
            send_hot_lead_email(
                store.email,
                message,
                mentioned_product or "Not specified",
                lead_score
            )
        )

    # 🔊 TTS
    audio_base64 = generate_tts_audio(ai_response)

    return {
        "response": ai_response,
        "audio": audio_base64
    }
