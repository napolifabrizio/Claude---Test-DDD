from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel

from claude_ddd.customers.application.dtos.customer_dto import CreateCustomerInput

router = APIRouter(prefix="/customers", tags=["customers"])


def get_container(request: Request) -> dict:
    return request.app.state.container


class CreateCustomerRequest(BaseModel):
    name: str
    email: str
    street: str
    number: str
    city: str
    state: str
    zip_code: str
    country: str = "BR"


@router.post("", status_code=status.HTTP_201_CREATED)
def create_customer(body: CreateCustomerRequest, container: dict = Depends(get_container)):
    try:
        output = container["create_customer"].execute(
            CreateCustomerInput(
                name=body.name,
                email=body.email,
                street=body.street,
                number=body.number,
                city=body.city,
                state=body.state,
                zip_code=body.zip_code,
                country=body.country,
            )
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

    return {
        "customer_id": str(output.customer_id),
        "name": output.name,
        "email": output.email,
        "address": output.address,
    }


@router.get("/{customer_id}")
def get_customer(customer_id: UUID, container: dict = Depends(get_container)):
    customer = container["customer_repo"].find_by_id(customer_id)
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Customer {customer_id} not found")

    return {
        "customer_id": str(customer.id),
        "name": customer.name,
        "email": str(customer.email),
        "address": str(customer.address),
    }
