from claude_ddd.contexts.ordering.application.dtos.order_dto import CreateOrderInput, OrderOutput
from claude_ddd.contexts.ordering.domain.entities.order import Order
from claude_ddd.contexts.ordering.domain.events.order_events import OrderCreated
from claude_ddd.contexts.ordering.domain.ports.customer_query import ICustomerQuery
from claude_ddd.contexts.ordering.domain.repositories.order_repository import OrderRepository
from claude_ddd.contexts.shared.infrastructure.event_bus.simple_event_bus import EventBus


class CreateOrderUseCase:

    def __init__(self, order_repo: OrderRepository, customer_query: ICustomerQuery, event_bus: EventBus):
        self._order_repo = order_repo
        self._customer_query = customer_query
        self._event_bus = event_bus

    def execute(self, input_data: CreateOrderInput) -> OrderOutput:
        if not self._customer_query.exists(input_data.customer_id):
            raise ValueError(f"Customer {input_data.customer_id} not found")

        order = Order(customer_id=input_data.customer_id)
        self._order_repo.save(order)

        self._event_bus.publish(OrderCreated(order_id=order.id, customer_id=order.customer_id))

        return OrderOutput(
            order_id=order.id,
            customer_id=order.customer_id,
            status=order.status.value,
            items=[],
            total=order.total.amount,
            currency=order.total.currency,
        )
