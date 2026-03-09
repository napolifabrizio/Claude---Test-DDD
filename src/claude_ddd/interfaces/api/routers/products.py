from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel

from claude_ddd.contexts.catalog.application.dtos.product_dto import CreateProductInput

router = APIRouter(prefix="/products", tags=["products"])


def get_container(request: Request) -> dict:
    return request.app.state.container


class CreateProductRequest(BaseModel):
    name: str
    price: Decimal
    stock: int
    currency: str = "BRL"


@router.post("", status_code=status.HTTP_201_CREATED)
def create_product(body: CreateProductRequest, container: dict = Depends(get_container)):
    try:
        output = container["create_product"].execute(
            CreateProductInput(
                name=body.name,
                price=body.price,
                stock=body.stock,
                currency=body.currency,
            )
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

    return {
        "product_id": str(output.product_id),
        "name": output.name,
        "price": str(output.price),
        "currency": output.currency,
        "stock": output.stock,
    }


@router.get("")
def list_products(container: dict = Depends(get_container)):
    products = container["product_repo"].find_all()
    return [
        {
            "product_id": str(p.id),
            "name": p.name,
            "price": str(p.price.amount),
            "currency": p.price.currency,
            "stock": p.stock,
        }
        for p in products
    ]


@router.get("/{product_id}")
def get_product(product_id: UUID, container: dict = Depends(get_container)):
    product = container["product_repo"].find_by_id(product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product {product_id} not found")

    return {
        "product_id": str(product.id),
        "name": product.name,
        "price": str(product.price.amount),
        "currency": product.price.currency,
        "stock": product.stock,
    }
