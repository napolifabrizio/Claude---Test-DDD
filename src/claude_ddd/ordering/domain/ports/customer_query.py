from __future__ import annotations
from abc import ABC, abstractmethod
from uuid import UUID


class ICustomerQuery(ABC):

    @abstractmethod
    def exists(self, customer_id: UUID) -> bool: ...
