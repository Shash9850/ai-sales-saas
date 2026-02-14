from fastapi import FastAPI
from sqlalchemy import text
from app.db.database import engine, Base
from app.models import user
from app.routes.auth import router as auth_router
from app.routes.store import router as store_router
from app.routes.product import router as product_router
from app.routes.chat import router as chat_router


app = FastAPI(title="Hindi AI Salesman SaaS")

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(store_router)
app.include_router(product_router)
app.include_router(chat_router)



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
