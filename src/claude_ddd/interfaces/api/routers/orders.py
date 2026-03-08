from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel

from claude_ddd.ordering.application.dtos.order_dto import (
    AddItemInput,
    CancelOrderInput,
    CreateOrderInput,
    OrderOutput,
    PlaceOrderInput,
)

router = APIRouter(prefix="/orders", tags=["orders"])


def get_container(request: Request) -> dict:
    return request.app.state.container


def _serialize_order(output: OrderOutput) -> dict:
    return {
        "order_id": str(output.order_id),
        "customer_id": str(output.customer_id),
        "status": output.status,
        "items": [
            {
                "product_id": str(item.product_id),
                "product_name": item.product_name,
                "unit_price": str(item.unit_price),
                "quantity": item.quantity,
                "subtotal": str(item.subtotal),
            }
            for item in output.items
        ],
        "total": str(output.total),
        "currency": output.currency,
    }


class CreateOrderRequest(BaseModel):
    customer_id: UUID


class AddItemRequest(BaseModel):
    product_id: UUID
    quantity: int


class CancelOrderRequest(BaseModel):
    reason: str = ""


@router.post("", status_code=status.HTTP_201_CREATED)
def create_order(body: CreateOrderRequest, container: dict = Depends(get_container)):
    try:
        output = container["create_order"].execute(CreateOrderInput(customer_id=body.customer_id))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    return _serialize_order(output)


@router.get("/{order_id}")
def get_order(order_id: UUID, container: dict = Depends(get_container)):
    from claude_ddd.ordering.application.dtos.order_dto import OrderItemOutput

    order = container["order_repo"].find_by_id(order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Order {order_id} not found")

    output = OrderOutput(
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
    return _serialize_order(output)


@router.post("/{order_id}/items")
def add_item(order_id: UUID, body: AddItemRequest, container: dict = Depends(get_container)):
    try:
        output = container["add_item"].execute(
            AddItemInput(order_id=order_id, product_id=body.product_id, quantity=body.quantity)
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    return _serialize_order(output)


@router.post("/{order_id}/place")
def place_order(order_id: UUID, container: dict = Depends(get_container)):
    try:
        output = container["place_order"].execute(PlaceOrderInput(order_id=order_id))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    return _serialize_order(output)


@router.post("/{order_id}/cancel")
def cancel_order(order_id: UUID, body: CancelOrderRequest, container: dict = Depends(get_container)):
    try:
        output = container["cancel_order"].execute(CancelOrderInput(order_id=order_id, reason=body.reason))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    return _serialize_order(output)
