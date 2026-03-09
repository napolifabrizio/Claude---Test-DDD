"""
Saga — cross-context orchestration.

Coordinates use cases from multiple bounded contexts in a single workflow.
This is the only layer (besides the composition root in app.py) allowed
to import from more than one bounded context.

Each saga method is a transaction script: if a step fails, earlier steps
are NOT automatically rolled back — add compensating actions explicitly
when your infrastructure requires it.
"""
from dataclasses import dataclass
from uuid import UUID

from claude_ddd.contexts.customers.application.dtos.customer_dto import CreateCustomerInput, CustomerOutput
from claude_ddd.contexts.customers.application.use_cases.create_customer import CreateCustomerUseCase
from claude_ddd.contexts.ordering.application.dtos.order_dto import OrderOutput
from claude_ddd.interfaces.api.services.order_service import OrderItem, OrderOrchestrationService


@dataclass
class CheckoutInput:
    """Everything needed to register a new customer and place their first order."""
    name: str
    email: str
    street: str
    number: str
    city: str
    state: str
    zip_code: str
    country: str
    items: list[OrderItem]


@dataclass
class CheckoutResult:
    customer: CustomerOutput
    order: OrderOutput


class CheckoutSaga:
    """
    Orchestrates a full checkout flow across the customers and ordering contexts:
      1. Create customer  (customers context)
      2. Create order and add items  (ordering context)
      3. Place order  (ordering context)

    Add compensating logic here if you later introduce persistent storage
    and need rollback semantics (e.g. mark customer inactive on order failure).
    """

    def __init__(
        self,
        create_customer: CreateCustomerUseCase,
        order_service: OrderOrchestrationService,
    ) -> None:
        self._create_customer = create_customer
        self._order_service = order_service

    def execute(self, data: CheckoutInput) -> CheckoutResult:
        customer = self._create_customer.execute(
            CreateCustomerInput(
                name=data.name,
                email=data.email,
                street=data.street,
                number=data.number,
                city=data.city,
                state=data.state,
                zip_code=data.zip_code,
                country=data.country,
            )
        )

        order = self._order_service.create_and_place(
            customer_id=customer.customer_id,
            items=data.items,
        )

        return CheckoutResult(customer=customer, order=order)
