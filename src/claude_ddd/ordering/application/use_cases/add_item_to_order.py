from claude_ddd.ordering.application.dtos.order_dto import AddItemInput, OrderItemOutput, OrderOutput
from claude_ddd.ordering.domain.ports.product_query import IProductQuery
from claude_ddd.ordering.domain.repositories.order_repository import OrderRepository
from claude_ddd.shared.domain.value_objects.money import Money
from claude_ddd.shared.infrastructure.event_bus.simple_event_bus import EventBus


class AddItemToOrderUseCase:

    def __init__(self, order_repo: OrderRepository, product_query: IProductQuery, event_bus: EventBus):
        self._order_repo = order_repo
        self._product_query = product_query
        self._event_bus = event_bus

    def execute(self, input_data: AddItemInput) -> OrderOutput:
        order = self._order_repo.find_by_id(input_data.order_id)
        if not order:
            raise ValueError(f"Order {input_data.order_id} not found")

        product_info = self._product_query.find_by_id(input_data.product_id)
        if not product_info:
            raise ValueError(f"Product {input_data.product_id} not found")

        if not product_info.is_available(input_data.quantity):
            raise ValueError(
                f"Insufficient stock for '{product_info.name}'. "
                f"Requested: {input_data.quantity}, available: {product_info.stock}"
            )

        order.add_item(
            product_id=product_info.id,
            product_name=product_info.name,
            unit_price=Money.of(product_info.price, product_info.currency),
            quantity=input_data.quantity,
        )

        events = order.pull_events()
        self._order_repo.save(order)

        for event in events:
            self._event_bus.publish(event)

        return OrderOutput(
            order_id=order.id,
            customer_id=order.customer_id,
            status=order.status.value,
            items=[
                OrderItemOutput(
                    product_id=item.product_id,
                    product_name=item.product_name,
                    unit_price=item.unit_price.amount,
                    quantity=item.quantity,
                    subtotal=item.subtotal.amount,
                )
                for item in order.items
            ],
            total=order.total.amount,
            currency=order.total.currency,
        )
