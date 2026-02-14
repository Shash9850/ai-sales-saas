from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.store import Store
from app.models.product import Product
from app.utils.dependencies import get_current_user
from app.models.user import User
from app.services.ai_service import generate_sales_response
from app.models.conversation import Conversation

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



@router.post("/public/{store_id}")
def public_chat(
    store_id: int,
    message: str,
    db: Session = Depends(get_db)
):
    # Find store
    store = db.query(Store).filter(Store.id == store_id).first()

    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    # Get products
    products = db.query(Product).filter(Product.store_id == store.id).all()

    if not products:
        return {"response": "इस समय कोई उत्पाद उपलब्ध नहीं है। कृपया बाद में पुनः प्रयास करें।"}

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

    # 🔥 SAVE CONVERSATION
    conversation = Conversation(
        store_id=store.id,
        customer_message=message,
        ai_response=ai_response
    )

    db.add(conversation)
    db.commit()

    return {"response": ai_response}
