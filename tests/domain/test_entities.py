import pytest
from uuid import uuid4

from src.domain.entities.order import Order, OrderStatus
from src.domain.entities.product import Product
from src.domain.value_objects.money import Money


class TestProduct:
    def _make_product(self, stock=10):
        return Product(name="Widget", price=Money.of(50), stock=stock)

    def test_available_when_enough_stock(self):
        p = self._make_product(stock=5)
        assert p.is_available(5) is True

    def test_not_available_when_insufficient_stock(self):
        p = self._make_product(stock=2)
        assert p.is_available(3) is False

    def test_decrease_stock(self):
        p = self._make_product(stock=10)
        p.decrease_stock(4)
        assert p.stock == 6

    def test_decrease_stock_insufficient_raises(self):
        p = self._make_product(stock=2)
        with pytest.raises(ValueError, match="Insufficient stock"):
            p.decrease_stock(5)

    def test_increase_stock(self):
        p = self._make_product(stock=5)
        p.increase_stock(3)
        assert p.stock == 8

    def test_increase_stock_zero_raises(self):
        p = self._make_product()
        with pytest.raises(ValueError):
            p.increase_stock(0)

    def test_negative_stock_raises(self):
        with pytest.raises(ValueError):
            Product(name="X", price=Money.of(10), stock=-1)


class TestOrder:
    def _make_order(self):
        return Order(customer_id=uuid4())

    def test_initial_status_is_draft(self):
        order = self._make_order()
        assert order.status == OrderStatus.DRAFT

    def test_add_item(self):
        order = self._make_order()
        pid = uuid4()
        order.add_item(pid, "Widget", Money.of(10), 2)
        assert len(order.items) == 1
        assert order.items[0].quantity == 2

    def test_add_same_item_increments_quantity(self):
        order = self._make_order()
        pid = uuid4()
        order.add_item(pid, "Widget", Money.of(10), 2)
        order.add_item(pid, "Widget", Money.of(10), 3)
        assert len(order.items) == 1
        assert order.items[0].quantity == 5

    def test_total_calculation(self):
        order = self._make_order()
        order.add_item(uuid4(), "A", Money.of(10), 2)
        order.add_item(uuid4(), "B", Money.of(5), 3)
        assert order.total == Money.of(35)

    def test_place_order(self):
        order = self._make_order()
        order.add_item(uuid4(), "Widget", Money.of(10), 1)
        order.place()
        assert order.status == OrderStatus.PLACED

    def test_place_empty_order_raises(self):
        order = self._make_order()
        with pytest.raises(ValueError, match="empty"):
            order.place()

    def test_cannot_add_item_to_placed_order(self):
        order = self._make_order()
        order.add_item(uuid4(), "Widget", Money.of(10), 1)
        order.place()
        with pytest.raises(ValueError):
            order.add_item(uuid4(), "Another", Money.of(5), 1)

    def test_cancel_order(self):
        order = self._make_order()
        order.cancel(reason="Test")
        assert order.status == OrderStatus.CANCELLED

    def test_cancel_already_cancelled_raises(self):
        order = self._make_order()
        order.cancel()
        with pytest.raises(ValueError, match="already cancelled"):
            order.cancel()

    def test_domain_events_emitted_on_add_item(self):
        from src.domain.events.domain_event import OrderItemAdded
        order = self._make_order()
        order.add_item(uuid4(), "Widget", Money.of(10), 1)
        events = order.pull_events()
        assert any(isinstance(e, OrderItemAdded) for e in events)

    def test_pull_events_clears_list(self):
        order = self._make_order()
        order.add_item(uuid4(), "Widget", Money.of(10), 1)
        order.pull_events()
        assert order.pull_events() == []
