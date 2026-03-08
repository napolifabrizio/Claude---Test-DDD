from abc import ABC, abstractmethod
from uuid import UUID

from claude_ddd.domain.entities.order import Order


class OrderRepository(ABC):

    @abstractmethod
    def save(self, order: Order) -> None: ...

    @abstractmethod
    def find_by_id(self, order_id: UUID) -> Order | None: ...

    @abstractmethod
    def find_by_customer(self, customer_id: UUID) -> list[Order]: ...

    @abstractmethod
    def delete(self, order_id: UUID) -> None: ...
