import copy
from uuid import UUID

from claude_ddd.contexts.ordering.domain.entities.order import Order
from claude_ddd.contexts.ordering.domain.repositories.order_repository import OrderRepository


class InMemoryOrderRepository(OrderRepository):

    def __init__(self):
        self._store: dict[UUID, Order] = {}

    def save(self, order: Order) -> None:
        self._store[order.id] = copy.deepcopy(order)

    def find_by_id(self, order_id: UUID) -> Order | None:
        order = self._store.get(order_id)
        return copy.deepcopy(order) if order else None

    def find_by_customer(self, customer_id: UUID) -> list[Order]:
        return [copy.deepcopy(o) for o in self._store.values() if o.customer_id == customer_id]

    def delete(self, order_id: UUID) -> None:
        self._store.pop(order_id, None)
