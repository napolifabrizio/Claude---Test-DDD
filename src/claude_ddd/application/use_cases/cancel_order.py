from claude_ddd.application.dtos.order_dto import CancelOrderInput, OrderOutput
from claude_ddd.domain.repositories.order_repository import OrderRepository
from claude_ddd.infrastructure.event_bus.simple_event_bus import EventBus


class CancelOrderUseCase:

    def __init__(self, order_repo: OrderRepository, event_bus: EventBus):
        self._order_repo = order_repo
        self._event_bus = event_bus

    def execute(self, input_data: CancelOrderInput) -> OrderOutput:
        order = self._order_repo.find_by_id(input_data.order_id)
        if not order:
            raise ValueError(f"Order {input_data.order_id} not found")

        order.cancel(reason=input_data.reason)
        events = order.pull_events()
        self._order_repo.save(order)

        for event in events:
            self._event_bus.publish(event)

        return OrderOutput(
            order_id=order.id,
            customer_id=order.customer_id,
            status=order.status.value,
            items=[],
            total=order.total.amount,
            currency=order.total.currency,
        )
