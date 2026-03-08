import copy
from uuid import UUID

from claude_ddd.domain.entities.customer import Customer
from claude_ddd.domain.repositories.customer_repository import CustomerRepository


class InMemoryCustomerRepository(CustomerRepository):

    def __init__(self):
        self._store: dict[UUID, Customer] = {}

    def save(self, customer: Customer) -> None:
        self._store[customer.id] = copy.deepcopy(customer)

    def find_by_id(self, customer_id: UUID) -> Customer | None:
        customer = self._store.get(customer_id)
        return copy.deepcopy(customer) if customer else None

    def find_by_email(self, email: str) -> Customer | None:
        result = next((c for c in self._store.values() if str(c.email) == email), None)
        return copy.deepcopy(result) if result else None

    def delete(self, customer_id: UUID) -> None:
        self._store.pop(customer_id, None)
