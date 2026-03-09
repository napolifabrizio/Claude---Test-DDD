from __future__ import annotations
from uuid import UUID

from claude_ddd.contexts.customers.domain.repositories.customer_repository import CustomerRepository
from claude_ddd.contexts.ordering.domain.ports.customer_query import ICustomerQuery


class CustomerQueryAdapter(ICustomerQuery):
    """Anti-corruption layer: bridges ordering's ICustomerQuery to the customers context."""

    def __init__(self, customer_repo: CustomerRepository):
        self._repo = customer_repo

    def exists(self, customer_id: UUID) -> bool:
        return self._repo.find_by_id(customer_id) is not None
