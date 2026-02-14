from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.product import Product
from app.models.store import Store
from app.schemas.product import ProductCreate, ProductResponse
from app.utils.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/product", tags=["Product"])


@router.post("/create", response_model=ProductResponse)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get store owned by current user
    store = db.query(Store).filter(Store.owner_id == current_user.id).first()

    if not store:
        raise HTTPException(status_code=400, detail="No store found for this user")

    new_product = Product(
        name=product.name,
        description=product.description,
        price=product.price,
        stock_quantity=product.stock_quantity,
        store_id=store.id
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product

@router.get("/my-products", response_model=list[ProductResponse])
def list_my_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    store = db.query(Store).filter(Store.owner_id == current_user.id).first()

    if not store:
        raise HTTPException(status_code=400, detail="No store found for this user")

    products = db.query(Product).filter(Product.store_id == store.id).all()

    return products

