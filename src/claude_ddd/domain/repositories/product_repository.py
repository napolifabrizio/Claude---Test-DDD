from abc import ABC, abstractmethod
from uuid import UUID

from claude_ddd.domain.entities.product import Product


class ProductRepository(ABC):

    @abstractmethod
    def save(self, product: Product) -> None: ...

    @abstractmethod
    def find_by_id(self, product_id: UUID) -> Product | None: ...

    @abstractmethod
    def find_all(self) -> list[Product]: ...

    @abstractmethod
    def delete(self, product_id: UUID) -> None: ...
