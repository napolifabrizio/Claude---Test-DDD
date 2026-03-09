from collections import defaultdict
from typing import Callable, Type

from claude_ddd.contexts.shared.domain.events.domain_event import DomainEvent


Handler = Callable[[DomainEvent], None]


class EventBus:

    def __init__(self):
        self._handlers: dict[Type[DomainEvent], list[Handler]] = defaultdict(list)

    def subscribe(self, event_type: Type[DomainEvent], handler: Handler) -> None:
        self._handlers[event_type].append(handler)

    def publish(self, event: DomainEvent) -> None:
        for handler in self._handlers[type(event)]:
            handler(event)
