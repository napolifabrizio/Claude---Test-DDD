from __future__ import annotations
import re
from dataclasses import dataclass

_EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self):
        if not _EMAIL_PATTERN.match(self.value):
            raise ValueError(f"Invalid email address: {self.value}")

    def __str__(self) -> str:
        return self.value
