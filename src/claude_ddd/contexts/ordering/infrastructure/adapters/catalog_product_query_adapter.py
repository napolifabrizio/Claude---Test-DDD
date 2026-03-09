from __future__ import annotations
from uuid import UUID

from claude_ddd.contexts.catalog.domain.repositories.product_repository import ProductRepository
from claude_ddd.contexts.ordering.domain.ports.product_query import IProductQuery, ProductInfo


class CatalogProductQueryAdapter(IProductQuery):
    """Anti-corruption layer: translates catalog's Product into ordering's ProductInfo."""

    def __init__(self, product_repo: ProductRepository):
        self._repo = product_repo

    def find_by_id(self, product_id: UUID) -> ProductInfo | None:
        product = self._repo.find_by_id(product_id)
        if not product:
            return None
        return ProductInfo(
            id=product.id,
            name=product.name,
            price=product.price.amount,
            currency=product.price.currency,
            stock=product.stock,
        )

    def reserve_stock(self, product_id: UUID, quantity: int) -> None:
        product = self._repo.find_by_id(product_id)
        if not product:
            raise ValueError(f"Product {product_id} no longer exists")
        product.decrease_stock(quantity)
        self._repo.save(product)
