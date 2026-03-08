from __future__ import annotations
from dataclasses import dataclass, field
from uuid import UUID, uuid4

from claude_ddd.shared.domain.events.domain_event import DomainEvent


@dataclass(frozen=True)
class OrderCreated(DomainEvent):
    order_id: UUID = field(default_factory=uuid4)
    customer_id: UUID = field(default_factory=uuid4)


@dataclass(frozen=True)
class OrderItemAdded(DomainEvent):
    order_id: UUID = field(default_factory=uuid4)
    product_id: UUID = field(default_factory=uuid4)
    quantity: int = 0


@dataclass(frozen=True)
class OrderPlaced(DomainEvent):
    order_id: UUID = field(default_factory=uuid4)
    customer_id: UUID = field(default_factory=uuid4)
    total_amount: str = ""


@dataclass(frozen=True)
class OrderCancelled(DomainEvent):
    order_id: UUID = field(default_factory=uuid4)
    reason: str = ""
