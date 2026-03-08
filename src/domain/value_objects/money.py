from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "BRL"

    def __post_init__(self):
        if self.amount < Decimal("0"):
            raise ValueError("Amount cannot be negative")
        if not self.currency:
            raise ValueError("Currency is required")

    def __add__(self, other: Money) -> Money:
        if self.currency != other.currency:
            raise ValueError(f"Cannot add {self.currency} and {other.currency}")
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: Money) -> Money:
        if self.currency != other.currency:
            raise ValueError(f"Cannot subtract {self.currency} from {other.currency}")
        result = self.amount - other.amount
        if result < Decimal("0"):
            raise ValueError("Result cannot be negative")
        return Money(result, self.currency)

    def __mul__(self, factor: int | Decimal) -> Money:
        return Money(self.amount * Decimal(str(factor)), self.currency)

    def __str__(self) -> str:
        return f"{self.currency} {self.amount:.2f}"

    @staticmethod
    def of(amount: float | str | Decimal, currency: str = "BRL") -> Money:
        return Money(Decimal(str(amount)), currency)

    @staticmethod
    def zero(currency: str = "BRL") -> Money:
        return Money(Decimal("0"), currency)
