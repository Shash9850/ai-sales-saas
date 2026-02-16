from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
import os
from dotenv import load_dotenv

load_dotenv()

from pydantic import EmailStr

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)


async def send_hot_lead_email(to_email: str, message: str, product: str, score: int):

    html = f"""
    <h2>🔥 Hot Lead Alert!</h2>
    <p><b>Lead Score:</b> {score}</p>
    <p><b>Interested Product:</b> {product}</p>
    <p><b>Customer Message:</b></p>
    <p>{message}</p>
    """

    message = MessageSchema(
        subject="🔥 New Hot Lead Detected!",
        recipients=[to_email],
        body=html,
        subtype="html"
    )

    fm = FastMail(conf)
    await fm.send_message(message)
