from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class Address:
    street: str
    number: str
    city: str
    state: str
    zip_code: str
    country: str = "BR"

    def __post_init__(self):
        for field_name, value in [
            ("street", self.street),
            ("number", self.number),
            ("city", self.city),
            ("state", self.state),
            ("zip_code", self.zip_code),
        ]:
            if not value or not value.strip():
                raise ValueError(f"Address field '{field_name}' is required")

    def __str__(self) -> str:
        return f"{self.street}, {self.number} - {self.city}/{self.state} - {self.zip_code}"
