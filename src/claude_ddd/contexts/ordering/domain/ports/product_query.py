from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True)
class ProductInfo:
    """Ordering context's read model of a product — defined in ordering's language."""
    id: UUID
    name: str
    price: Decimal
    currency: str
    stock: int

    def is_available(self, quantity: int) -> bool:
        return self.stock >= quantity


class IProductQuery(ABC):

    @abstractmethod
    def find_by_id(self, product_id: UUID) -> ProductInfo | None: ...

    @abstractmethod
    def reserve_stock(self, product_id: UUID, quantity: int) -> None:
        """Decrements stock. Raises ValueError if product missing or insufficient stock."""
        ...
