from __future__ import annotations
from dataclasses import dataclass, field
from uuid import UUID, uuid4

from claude_ddd.contexts.customers.domain.value_objects.address import Address
from claude_ddd.contexts.customers.domain.value_objects.email import Email


@dataclass
class Customer:
    name: str
    email: Email
    address: Address
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self):
        if not self.name or not self.name.strip():
            raise ValueError("Customer name is required")

    def change_address(self, new_address: Address) -> None:
        self.address = new_address

    def change_email(self, new_email: Email) -> None:
        self.email = new_email

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Customer):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
