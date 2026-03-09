import copy
from uuid import UUID

from claude_ddd.contexts.catalog.domain.entities.product import Product
from claude_ddd.contexts.catalog.domain.repositories.product_repository import ProductRepository


class InMemoryProductRepository(ProductRepository):

    def __init__(self):
        self._store: dict[UUID, Product] = {}

    def save(self, product: Product) -> None:
        self._store[product.id] = copy.deepcopy(product)

    def find_by_id(self, product_id: UUID) -> Product | None:
        product = self._store.get(product_id)
        return copy.deepcopy(product) if product else None

    def find_all(self) -> list[Product]:
        return [copy.deepcopy(p) for p in self._store.values()]

    def delete(self, product_id: UUID) -> None:
        self._store.pop(product_id, None)
