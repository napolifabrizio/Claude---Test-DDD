from dataclasses import dataclass
from uuid import UUID


@dataclass
class CreateCustomerInput:
    name: str
    email: str
    street: str
    number: str
    city: str
    state: str
    zip_code: str
    country: str = "BR"


@dataclass
class CustomerOutput:
    customer_id: UUID
    name: str
    email: str
    address: str
