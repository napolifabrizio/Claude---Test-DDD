from decimal import Decimal

from claude_ddd.contexts.shared.domain.events.domain_event import DomainEvent
from claude_ddd.contexts.shared.infrastructure.event_bus.simple_event_bus import EventBus

from claude_ddd.contexts.customers.application.dtos.customer_dto import CreateCustomerInput
from claude_ddd.contexts.customers.application.use_cases.create_customer import CreateCustomerUseCase
from claude_ddd.contexts.customers.infrastructure.persistence.in_memory_customer_repository import InMemoryCustomerRepository

from claude_ddd.contexts.catalog.application.dtos.product_dto import CreateProductInput
from claude_ddd.contexts.catalog.application.use_cases.create_product import CreateProductUseCase
from claude_ddd.contexts.catalog.infrastructure.persistence.in_memory_product_repository import InMemoryProductRepository

from claude_ddd.contexts.ordering.application.dtos.order_dto import AddItemInput, CancelOrderInput, CreateOrderInput, PlaceOrderInput
from claude_ddd.contexts.ordering.application.use_cases.add_item_to_order import AddItemToOrderUseCase
from claude_ddd.contexts.ordering.application.use_cases.cancel_order import CancelOrderUseCase
from claude_ddd.contexts.ordering.application.use_cases.create_order import CreateOrderUseCase
from claude_ddd.contexts.ordering.application.use_cases.place_order import PlaceOrderUseCase
from claude_ddd.contexts.ordering.domain.events.order_events import OrderCancelled, OrderCreated, OrderItemAdded, OrderPlaced
from claude_ddd.contexts.ordering.domain.services.pricing_service import PricingService
from claude_ddd.contexts.ordering.infrastructure.adapters.catalog_product_query_adapter import CatalogProductQueryAdapter
from claude_ddd.contexts.ordering.infrastructure.adapters.customer_query_adapter import CustomerQueryAdapter
from claude_ddd.contexts.ordering.infrastructure.persistence.in_memory_order_repository import InMemoryOrderRepository


def log_event(event: DomainEvent) -> None:
    print(f"  [EVENT] {type(event).__name__}: {event}")


def build_container():
    event_bus = EventBus()

    for event_type in (OrderCreated, OrderItemAdded, OrderPlaced, OrderCancelled):
        event_bus.subscribe(event_type, log_event)

    customer_repo = InMemoryCustomerRepository()
    product_repo = InMemoryProductRepository()
    order_repo = InMemoryOrderRepository()
    pricing_service = PricingService()

    customer_query = CustomerQueryAdapter(customer_repo)
    product_query = CatalogProductQueryAdapter(product_repo)

    return {
        "create_customer": CreateCustomerUseCase(customer_repo),
        "create_product": CreateProductUseCase(product_repo),
        "create_order": CreateOrderUseCase(order_repo, customer_query, event_bus),
        "add_item": AddItemToOrderUseCase(order_repo, product_query, event_bus),
        "place_order": PlaceOrderUseCase(order_repo, product_query, pricing_service, event_bus),
        "cancel_order": CancelOrderUseCase(order_repo, event_bus),
    }


def main():
    container = build_container()

    print("=" * 60)
    print("DDD Order Management System - Demo")
    print("=" * 60)

    print("\n--- Creating customer ---")
    customer_out = container["create_customer"].execute(
        CreateCustomerInput(
            name="Ana Lima",
            email="ana@example.com",
            street="Rua das Flores",
            number="42",
            city="Sao Paulo",
            state="SP",
            zip_code="01310-100",
        )
    )
    print(f"Customer created: {customer_out.name} ({customer_out.customer_id})")
    print(f"  Address: {customer_out.address}")

    print("\n--- Creating products ---")
    notebook = container["create_product"].execute(
        CreateProductInput(name="Notebook Pro", price=Decimal("4999.99"), stock=10)
    )
    mouse = container["create_product"].execute(
        CreateProductInput(name="Mouse Gamer", price=Decimal("249.90"), stock=50)
    )
    headset = container["create_product"].execute(
        CreateProductInput(name="Headset RGB", price=Decimal("399.00"), stock=30)
    )
    print(f"Product: {notebook.name} | Price: BRL {notebook.price} | Stock: {notebook.stock}")
    print(f"Product: {mouse.name}    | Price: BRL {mouse.price}  | Stock: {mouse.stock}")
    print(f"Product: {headset.name}  | Price: BRL {headset.price} | Stock: {headset.stock}")

    print("\n--- Creating order ---")
    order_out = container["create_order"].execute(CreateOrderInput(customer_id=customer_out.customer_id))
    print(f"Order created: {order_out.order_id} | Status: {order_out.status}")

    print("\n--- Adding items to order ---")
    order_out = container["add_item"].execute(
        AddItemInput(order_id=order_out.order_id, product_id=notebook.product_id, quantity=1)
    )
    order_out = container["add_item"].execute(
        AddItemInput(order_id=order_out.order_id, product_id=mouse.product_id, quantity=2)
    )
    order_out = container["add_item"].execute(
        AddItemInput(order_id=order_out.order_id, product_id=headset.product_id, quantity=3)
    )
    print(f"Items in order:")
    for item in order_out.items:
        print(f"  - {item.product_name} x{item.quantity} @ {item.unit_price} = {item.subtotal}")
    print(f"  Subtotal: {order_out.currency} {order_out.total}")

    print("\n--- Placing order (6 items -> 10% bulk discount applies) ---")
    placed_out = container["place_order"].execute(PlaceOrderInput(order_id=order_out.order_id))
    print(f"Order placed! Status: {placed_out.status}")
    print(f"  Final total (after discount): {placed_out.currency} {placed_out.total}")

    print("\n--- Creating a second order to cancel ---")
    order2 = container["create_order"].execute(CreateOrderInput(customer_id=customer_out.customer_id))
    container["add_item"].execute(
        AddItemInput(order_id=order2.order_id, product_id=mouse.product_id, quantity=1)
    )
    cancelled = container["cancel_order"].execute(
        CancelOrderInput(order_id=order2.order_id, reason="Customer changed mind")
    )
    print(f"Order cancelled. Status: {cancelled.status}")

    print("\n" + "=" * 60)
    print("Demo complete.")


if __name__ == "__main__":
    main()
