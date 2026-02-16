from fastapi import APIRouter, Form
from fastapi.responses import PlainTextResponse
from app.db.database import SessionLocal
from app.models.store import Store
from app.models.product import Product
from app.models.conversation import Conversation
from app.services.ai_service import generate_sales_response
from app.services.email_service import send_hot_lead_email
from app.utils.subscription import is_store_active
from twilio.twiml.messaging_response import MessagingResponse
from datetime import datetime
import asyncio

router = APIRouter()

@router.post("/whatsapp")
async def whatsapp_webhook(
    Body: str = Form(...),
    From: str = Form(...),
    To: str = Form(...)
):
    db = SessionLocal()

    try:
        # 🔥 Multi-store routing
        store = db.query(Store).filter(Store.whatsapp_number == To).first()

        if not store:
            return PlainTextResponse("Store not configured for this number.")

        # 🔒 Subscription check (use your utility)
        if not is_store_active(store):
            return PlainTextResponse("Subscription expired. Please renew service.")

        products = db.query(Product).filter(Product.store_id == store.id).all()

        if not products:
            return PlainTextResponse("इस समय कोई उत्पाद उपलब्ध नहीं है।")

        product_info = "\n".join([
            f"- {p.name} – ₹{p.price} – {p.description}"
            for p in products if p.is_available
        ])

        prompt = f"""
Store Name: {store.name}

Available Products:
{product_info}

Customer says:
{Body}

Respond in persuasive Hindi and suggest relevant products.
"""

        ai_response = generate_sales_response(prompt)

        # 🔥 Lead Intelligence
        intent = "BROWSING"
        lead_score = 20
        mentioned_product = None
        lower_msg = Body.lower()

        if "खरीद" in lower_msg or "लेना" in lower_msg or "बुक" in lower_msg:
            intent = "BUYING"
            lead_score = 85
        elif "सस्ता" in lower_msg or "डिस्काउंट" in lower_msg:
            intent = "PRICE_SENSITIVE"
            lead_score = 60

        for p in products:
            if p.name.lower() in lower_msg:
                mentioned_product = p.name

        # 💾 Save WhatsApp Conversation
        conversation = Conversation(
            store_id=store.id,
            customer_message=Body,
            ai_response=ai_response,
            intent=intent,
            mentioned_product=mentioned_product,
            lead_score=lead_score
        )

        db.add(conversation)
        db.commit()

        # 🔥 Hot lead email alert
        if lead_score >= 80 and store.email:
            asyncio.create_task(
                send_hot_lead_email(
                    store.email,
                    Body,
                    mentioned_product or "Not specified",
                    lead_score
                )
            )

        # 📲 Twilio Response
        twilio_response = MessagingResponse()
        twilio_response.message(ai_response)

        return PlainTextResponse(str(twilio_response), media_type="application/xml")

    finally:
        db.close()
