"""
Application Service — same-context orchestration.

Coordinates multiple ordering use cases in a single call.
Use this when a single HTTP request needs more than one use-case step
but all steps belong to the ordering context.
"""
from dataclasses import dataclass
from uuid import UUID

from claude_ddd.contexts.ordering.application.dtos.order_dto import (
    AddItemInput,
    CreateOrderInput,
    OrderOutput,
    PlaceOrderInput,
)
from claude_ddd.contexts.ordering.application.use_cases.add_item_to_order import AddItemToOrderUseCase
from claude_ddd.contexts.ordering.application.use_cases.create_order import CreateOrderUseCase
from claude_ddd.contexts.ordering.application.use_cases.place_order import PlaceOrderUseCase


@dataclass
class OrderItem:
    product_id: UUID
    quantity: int


class OrderOrchestrationService:
    """
    Composes ordering use cases for multi-step workflows.

    Example workflow: create a draft order, populate it with items,
    and optionally place it — all in one service call.
    """

    def __init__(
        self,
        create_order: CreateOrderUseCase,
        add_item: AddItemToOrderUseCase,
        place_order: PlaceOrderUseCase,
    ) -> None:
        self._create_order = create_order
        self._add_item = add_item
        self._place_order = place_order

    def create_draft_with_items(
        self,
        customer_id: UUID,
        items: list[OrderItem],
    ) -> OrderOutput:
        """Create an order and add all items in a single call. Returns a DRAFT order."""
        order = self._create_order.execute(CreateOrderInput(customer_id=customer_id))
        for item in items:
            order = self._add_item.execute(
                AddItemInput(order_id=order.order_id, product_id=item.product_id, quantity=item.quantity)
            )
        return order

    def create_and_place(
        self,
        customer_id: UUID,
        items: list[OrderItem],
    ) -> OrderOutput:
        """Create an order, add all items, and place it — returns a PLACED order."""
        order = self.create_draft_with_items(customer_id, items)
        return self._place_order.execute(PlaceOrderInput(order_id=order.order_id))
