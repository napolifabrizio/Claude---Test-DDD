from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass
class CreateOrderInput:
    customer_id: UUID


@dataclass
class AddItemInput:
    order_id: UUID
    product_id: UUID
    quantity: int


@dataclass
class PlaceOrderInput:
    order_id: UUID


@dataclass
class CancelOrderInput:
    order_id: UUID
    reason: str = ""


@dataclass
class OrderItemOutput:
    product_id: UUID
    product_name: str
    unit_price: Decimal
    quantity: int
    subtotal: Decimal


@dataclass
class OrderOutput:
    order_id: UUID
    customer_id: UUID
    status: str
    items: list[OrderItemOutput]
    total: Decimal
    currency: str
