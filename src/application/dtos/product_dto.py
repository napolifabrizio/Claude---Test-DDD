from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass
class CreateProductInput:
    name: str
    price: Decimal
    stock: int
    currency: str = "BRL"


@dataclass
class ProductOutput:
    product_id: UUID
    name: str
    price: Decimal
    currency: str
    stock: int
