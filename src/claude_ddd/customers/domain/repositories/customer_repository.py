from abc import ABC, abstractmethod
from uuid import UUID

from claude_ddd.customers.domain.entities.customer import Customer


class CustomerRepository(ABC):

    @abstractmethod
    def save(self, customer: Customer) -> None: ...

    @abstractmethod
    def find_by_id(self, customer_id: UUID) -> Customer | None: ...

    @abstractmethod
    def find_by_email(self, email: str) -> Customer | None: ...

    @abstractmethod
    def delete(self, customer_id: UUID) -> None: ...
