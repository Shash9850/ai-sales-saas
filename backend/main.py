from fastapi import FastAPI
from sqlalchemy import text
from app.db.database import engine, Base
from app.models import user
from app.routes.auth import router as auth_router
from app.routes.store import router as store_router
from app.routes.product import router as product_router
from app.routes.chat import router as chat_router
from fastapi.middleware.cors import CORSMiddleware

from app.routes.analytics import router as analytics_router

from app.routes.whatsapp import router as whatsapp_router

from app.routes.admin import router as admin_router
from app.routes.plan import router as plan_router





app = FastAPI(title="Hindi AI Salesman SaaS")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(store_router)
app.include_router(product_router)
app.include_router(chat_router)
app.include_router(analytics_router)
app.include_router(whatsapp_router)
app.include_router(admin_router)
app.include_router(plan_router)

@app.get("/")
def root():
    return {"message": "Hindi AI Salesman Backend Running 🚀"}

@app.get("/db-test")
def test_db():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            return {"database": "Connected Successfully ✅"}

    except Exception as e:
        return {"error": str(e)}

@app.get("/check-users-table")
def check_users_table():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT * FROM users"))
        return {"message": "Users table exists ✅"}


from fastapi.responses import HTMLResponse

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
        <head>
            <title>Hindi AI Salesman</title>
        </head>
        <body>
            <h1>Hindi AI Salesman SaaS</h1>
            <p>This is a live AI-powered sales automation platform.</p>
        </body>
    </html>
    """
