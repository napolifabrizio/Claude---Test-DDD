from claude_ddd.application.dtos.order_dto import PlaceOrderInput, OrderItemOutput, OrderOutput
from claude_ddd.domain.repositories.order_repository import OrderRepository
from claude_ddd.domain.repositories.product_repository import ProductRepository
from claude_ddd.domain.services.pricing_service import PricingService
from claude_ddd.infrastructure.event_bus.simple_event_bus import EventBus


class PlaceOrderUseCase:

    def __init__(
        self,
        order_repo: OrderRepository,
        product_repo: ProductRepository,
        pricing_service: PricingService,
        event_bus: EventBus,
    ):
        self._order_repo = order_repo
        self._product_repo = product_repo
        self._pricing_service = pricing_service
        self._event_bus = event_bus

    def execute(self, input_data: PlaceOrderInput) -> OrderOutput:
        order = self._order_repo.find_by_id(input_data.order_id)
        if not order:
            raise ValueError(f"Order {input_data.order_id} not found")

        for item in order.items:
            product = self._product_repo.find_by_id(item.product_id)
            if not product:
                raise ValueError(f"Product {item.product_id} no longer exists")
            product.decrease_stock(item.quantity)
            self._product_repo.save(product)

        order.place()
        events = order.pull_events()
        self._order_repo.save(order)

        for event in events:
            self._event_bus.publish(event)

        final_total = self._pricing_service.calculate_final_total(order)

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
            total=final_total.amount,
            currency=final_total.currency,
        )
