from contextlib import asynccontextmanager
from decimal import Decimal

from fastapi import FastAPI

from claude_ddd.shared.domain.events.domain_event import DomainEvent
from claude_ddd.shared.infrastructure.event_bus.simple_event_bus import EventBus

from claude_ddd.customers.application.use_cases.create_customer import CreateCustomerUseCase
from claude_ddd.customers.infrastructure.persistence.in_memory_customer_repository import InMemoryCustomerRepository

from claude_ddd.catalog.application.use_cases.create_product import CreateProductUseCase
from claude_ddd.catalog.infrastructure.persistence.in_memory_product_repository import InMemoryProductRepository

from claude_ddd.ordering.application.use_cases.add_item_to_order import AddItemToOrderUseCase
from claude_ddd.ordering.application.use_cases.cancel_order import CancelOrderUseCase
from claude_ddd.ordering.application.use_cases.create_order import CreateOrderUseCase
from claude_ddd.ordering.application.use_cases.place_order import PlaceOrderUseCase
from claude_ddd.ordering.domain.events.order_events import OrderCancelled, OrderCreated, OrderItemAdded, OrderPlaced
from claude_ddd.ordering.domain.services.pricing_service import PricingService
from claude_ddd.ordering.infrastructure.adapters.catalog_product_query_adapter import CatalogProductQueryAdapter
from claude_ddd.ordering.infrastructure.adapters.customer_query_adapter import CustomerQueryAdapter
from claude_ddd.ordering.infrastructure.persistence.in_memory_order_repository import InMemoryOrderRepository

from claude_ddd.interfaces.api.routers import customers, products, orders


def _log_event(event: DomainEvent) -> None:
    print(f"  [EVENT] {type(event).__name__}: {event}")


def build_container() -> dict:
    event_bus = EventBus()
    for event_type in (OrderCreated, OrderItemAdded, OrderPlaced, OrderCancelled):
        event_bus.subscribe(event_type, _log_event)

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
        # Repos exposed for read endpoints
        "customer_repo": customer_repo,
        "product_repo": product_repo,
        "order_repo": order_repo,
    }


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.container = build_container()
    yield


app = FastAPI(
    title="Claude DDD API",
    description="Domain-Driven Design Order Management System",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(customers.router)
app.include_router(products.router)
app.include_router(orders.router)
