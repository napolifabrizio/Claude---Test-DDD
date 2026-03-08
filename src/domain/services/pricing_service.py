from decimal import Decimal

from src.domain.entities.order import Order
from src.domain.value_objects.money import Money


class PricingService:
    """Domain service: encapsulates pricing logic that doesn't belong to a single entity."""

    BULK_DISCOUNT_THRESHOLD = 5
    BULK_DISCOUNT_RATE = Decimal("0.10")

    def calculate_discount(self, order: Order) -> Money:
        total_items = sum(item.quantity for item in order.items)
        if total_items >= self.BULK_DISCOUNT_THRESHOLD:
            currency = order.items[0].unit_price.currency if order.items else "BRL"
            return Money.of(order.total.amount * self.BULK_DISCOUNT_RATE, currency)
        return Money.zero()

    def calculate_final_total(self, order: Order) -> Money:
        total = order.total
        total_items = sum(item.quantity for item in order.items)
        if total_items >= self.BULK_DISCOUNT_THRESHOLD:
            discounted = (total.amount * (1 - self.BULK_DISCOUNT_RATE)).quantize(Decimal("0.01"))
            return Money.of(discounted, total.currency)
        return total
