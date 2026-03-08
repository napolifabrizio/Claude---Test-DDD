import pytest
from decimal import Decimal
from uuid import uuid4

from src.application.dtos.customer_dto import CreateCustomerInput
from src.application.dtos.order_dto import AddItemInput, CancelOrderInput, CreateOrderInput, PlaceOrderInput
from src.application.dtos.product_dto import CreateProductInput
from src.application.use_cases.add_item_to_order import AddItemToOrderUseCase
from src.application.use_cases.cancel_order import CancelOrderUseCase
from src.application.use_cases.create_customer import CreateCustomerUseCase
from src.application.use_cases.create_order import CreateOrderUseCase
from src.application.use_cases.create_product import CreateProductUseCase
from src.application.use_cases.place_order import PlaceOrderUseCase
from src.domain.services.pricing_service import PricingService
from src.infrastructure.event_bus.simple_event_bus import EventBus
from src.infrastructure.persistence.in_memory_customer_repository import InMemoryCustomerRepository
from src.infrastructure.persistence.in_memory_order_repository import InMemoryOrderRepository
from src.infrastructure.persistence.in_memory_product_repository import InMemoryProductRepository


@pytest.fixture
def repos():
    return {
        "customers": InMemoryCustomerRepository(),
        "products": InMemoryProductRepository(),
        "orders": InMemoryOrderRepository(),
    }


@pytest.fixture
def event_bus():
    return EventBus()


@pytest.fixture
def use_cases(repos, event_bus):
    return {
        "create_customer": CreateCustomerUseCase(repos["customers"]),
        "create_product": CreateProductUseCase(repos["products"]),
        "create_order": CreateOrderUseCase(repos["orders"], repos["customers"], event_bus),
        "add_item": AddItemToOrderUseCase(repos["orders"], repos["products"], event_bus),
        "place_order": PlaceOrderUseCase(repos["orders"], repos["products"], PricingService(), event_bus),
        "cancel_order": CancelOrderUseCase(repos["orders"], event_bus),
    }


def create_customer(use_cases):
    return use_cases["create_customer"].execute(
        CreateCustomerInput(
            name="Test User",
            email="test@test.com",
            street="Rua X",
            number="10",
            city="SP",
            state="SP",
            zip_code="00000-000",
        )
    )


def create_product(use_cases, name="Widget", price="50.00", stock=20):
    return use_cases["create_product"].execute(
        CreateProductInput(name=name, price=Decimal(price), stock=stock)
    )


class TestCreateCustomer:
    def test_creates_successfully(self, use_cases):
        out = create_customer(use_cases)
        assert out.name == "Test User"
        assert out.email == "test@test.com"

    def test_duplicate_email_raises(self, use_cases):
        create_customer(use_cases)
        with pytest.raises(ValueError, match="already exists"):
            create_customer(use_cases)

    def test_invalid_email_raises(self, use_cases):
        with pytest.raises(ValueError):
            use_cases["create_customer"].execute(
                CreateCustomerInput(
                    name="X", email="bad-email",
                    street="R", number="1", city="C", state="S", zip_code="0"
                )
            )


class TestCreateOrder:
    def test_creates_for_existing_customer(self, use_cases):
        customer = create_customer(use_cases)
        order = use_cases["create_order"].execute(CreateOrderInput(customer_id=customer.customer_id))
        assert order.status == "draft"
        assert order.customer_id == customer.customer_id

    def test_unknown_customer_raises(self, use_cases):
        with pytest.raises(ValueError, match="not found"):
            use_cases["create_order"].execute(CreateOrderInput(customer_id=uuid4()))


class TestAddItemToOrder:
    def test_adds_item_successfully(self, use_cases):
        customer = create_customer(use_cases)
        product = create_product(use_cases)
        order = use_cases["create_order"].execute(CreateOrderInput(customer_id=customer.customer_id))

        result = use_cases["add_item"].execute(
            AddItemInput(order_id=order.order_id, product_id=product.product_id, quantity=2)
        )
        assert len(result.items) == 1
        assert result.items[0].quantity == 2

    def test_insufficient_stock_raises(self, use_cases):
        customer = create_customer(use_cases)
        product = create_product(use_cases, stock=1)
        order = use_cases["create_order"].execute(CreateOrderInput(customer_id=customer.customer_id))

        with pytest.raises(ValueError, match="Insufficient stock"):
            use_cases["add_item"].execute(
                AddItemInput(order_id=order.order_id, product_id=product.product_id, quantity=5)
            )


class TestPlaceOrder:
    def test_places_order_and_decreases_stock(self, use_cases, repos):
        customer = create_customer(use_cases)
        product = create_product(use_cases, stock=10)
        order = use_cases["create_order"].execute(CreateOrderInput(customer_id=customer.customer_id))
        use_cases["add_item"].execute(
            AddItemInput(order_id=order.order_id, product_id=product.product_id, quantity=3)
        )

        result = use_cases["place_order"].execute(PlaceOrderInput(order_id=order.order_id))
        assert result.status == "placed"

        updated_product = repos["products"].find_by_id(product.product_id)
        assert updated_product.stock == 7

    def test_bulk_discount_applied(self, use_cases):
        customer = create_customer(use_cases)
        product = create_product(use_cases, price="100.00", stock=20)
        order = use_cases["create_order"].execute(CreateOrderInput(customer_id=customer.customer_id))
        use_cases["add_item"].execute(
            AddItemInput(order_id=order.order_id, product_id=product.product_id, quantity=6)
        )

        result = use_cases["place_order"].execute(PlaceOrderInput(order_id=order.order_id))
        assert result.total == Decimal("540.00")


class TestCancelOrder:
    def test_cancels_draft_order(self, use_cases):
        customer = create_customer(use_cases)
        order = use_cases["create_order"].execute(CreateOrderInput(customer_id=customer.customer_id))

        result = use_cases["cancel_order"].execute(
            CancelOrderInput(order_id=order.order_id, reason="Changed mind")
        )
        assert result.status == "cancelled"

    def test_cancel_unknown_order_raises(self, use_cases):
        with pytest.raises(ValueError, match="not found"):
            use_cases["cancel_order"].execute(CancelOrderInput(order_id=uuid4()))
