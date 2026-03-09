from __future__ import annotations
from dataclasses import dataclass, field
from uuid import UUID, uuid4

from claude_ddd.contexts.shared.domain.value_objects.money import Money


@dataclass
class Product:
    name: str
    price: Money
    stock: int
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self):
        if not self.name or not self.name.strip():
            raise ValueError("Product name is required")
        if self.stock < 0:
            raise ValueError("Stock cannot be negative")

    def is_available(self, quantity: int = 1) -> bool:
        return self.stock >= quantity

    def decrease_stock(self, quantity: int) -> None:
        if not self.is_available(quantity):
            raise ValueError(
                f"Insufficient stock for '{self.name}'. "
                f"Requested: {quantity}, available: {self.stock}"
            )
        self.stock -= quantity

    def increase_stock(self, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        self.stock += quantity

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Product):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
