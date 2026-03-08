from claude_ddd.application.dtos.order_dto import CreateOrderInput, OrderOutput
from claude_ddd.domain.entities.order import Order
from claude_ddd.domain.events.domain_event import OrderCreated
from claude_ddd.domain.repositories.customer_repository import CustomerRepository
from claude_ddd.domain.repositories.order_repository import OrderRepository
from claude_ddd.infrastructure.event_bus.simple_event_bus import EventBus


class CreateOrderUseCase:

    def __init__(self, order_repo: OrderRepository, customer_repo: CustomerRepository, event_bus: EventBus):
        self._order_repo = order_repo
        self._customer_repo = customer_repo
        self._event_bus = event_bus

    def execute(self, input_data: CreateOrderInput) -> OrderOutput:
        customer = self._customer_repo.find_by_id(input_data.customer_id)
        if not customer:
            raise ValueError(f"Customer {input_data.customer_id} not found")

        order = Order(customer_id=customer.id)
        self._order_repo.save(order)

        self._event_bus.publish(OrderCreated(order_id=order.id, customer_id=customer.id))

        return OrderOutput(
            order_id=order.id,
            customer_id=order.customer_id,
            status=order.status.value,
            items=[],
            total=order.total.amount,
            currency=order.total.currency,
        )
