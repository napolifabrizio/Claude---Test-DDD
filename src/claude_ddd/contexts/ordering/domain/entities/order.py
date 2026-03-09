from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from uuid import UUID, uuid4

from claude_ddd.contexts.shared.domain.value_objects.money import Money


class OrderStatus(Enum):
    DRAFT = "draft"
    PLACED = "placed"
    CANCELLED = "cancelled"


@dataclass
class OrderItem:
    product_id: UUID
    product_name: str
    unit_price: Money
    quantity: int

    def __post_init__(self):
        if self.quantity <= 0:
            raise ValueError("Quantity must be greater than zero")

    @property
    def subtotal(self) -> Money:
        return self.unit_price * self.quantity


@dataclass
class Order:
    customer_id: UUID
    id: UUID = field(default_factory=uuid4)
    status: OrderStatus = field(default=OrderStatus.DRAFT)
    items: list[OrderItem] = field(default_factory=list)
    _events: list = field(default_factory=list, repr=False)

    def add_item(self, product_id: UUID, product_name: str, unit_price: Money, quantity: int) -> None:
        if self.status != OrderStatus.DRAFT:
            raise ValueError(f"Cannot add items to an order with status '{self.status.value}'")

        existing = self._find_item(product_id)
        if existing:
            existing.quantity += quantity
        else:
            self.items.append(OrderItem(product_id, product_name, unit_price, quantity))

        from claude_ddd.contexts.ordering.domain.events.order_events import OrderItemAdded
        self._events.append(OrderItemAdded(order_id=self.id, product_id=product_id, quantity=quantity))

    def remove_item(self, product_id: UUID) -> None:
        if self.status != OrderStatus.DRAFT:
            raise ValueError(f"Cannot remove items from an order with status '{self.status.value}'")
        item = self._find_item(product_id)
        if not item:
            raise ValueError(f"Product {product_id} not found in order")
        self.items.remove(item)

    def place(self) -> None:
        if self.status != OrderStatus.DRAFT:
            raise ValueError(f"Order cannot be placed from status '{self.status.value}'")
        if not self.items:
            raise ValueError("Cannot place an empty order")
        self.status = OrderStatus.PLACED

        from claude_ddd.contexts.ordering.domain.events.order_events import OrderPlaced
        self._events.append(
            OrderPlaced(order_id=self.id, customer_id=self.customer_id, total_amount=str(self.total))
        )

    def cancel(self, reason: str = "") -> None:
        if self.status == OrderStatus.CANCELLED:
            raise ValueError("Order is already cancelled")
        self.status = OrderStatus.CANCELLED

        from claude_ddd.contexts.ordering.domain.events.order_events import OrderCancelled
        self._events.append(OrderCancelled(order_id=self.id, reason=reason))

    @property
    def total(self) -> Money:
        if not self.items:
            return Money.zero()
        result = Money.zero(self.items[0].unit_price.currency)
        for item in self.items:
            result = result + item.subtotal
        return result

    def pull_events(self) -> list:
        events = list(self._events)
        self._events.clear()
        return events

    def _find_item(self, product_id: UUID) -> OrderItem | None:
        return next((i for i in self.items if i.product_id == product_id), None)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Order):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
