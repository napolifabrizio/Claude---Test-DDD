from src.application.dtos.customer_dto import CreateCustomerInput, CustomerOutput
from src.domain.entities.customer import Customer
from src.domain.repositories.customer_repository import CustomerRepository
from src.domain.value_objects.address import Address
from src.domain.value_objects.email import Email


class CreateCustomerUseCase:

    def __init__(self, customer_repo: CustomerRepository):
        self._customer_repo = customer_repo

    def execute(self, input_data: CreateCustomerInput) -> CustomerOutput:
        email = Email(input_data.email)

        existing = self._customer_repo.find_by_email(input_data.email)
        if existing:
            raise ValueError(f"Customer with email '{input_data.email}' already exists")

        address = Address(
            street=input_data.street,
            number=input_data.number,
            city=input_data.city,
            state=input_data.state,
            zip_code=input_data.zip_code,
            country=input_data.country,
        )
        customer = Customer(name=input_data.name, email=email, address=address)
        self._customer_repo.save(customer)

        return CustomerOutput(
            customer_id=customer.id,
            name=customer.name,
            email=str(customer.email),
            address=str(customer.address),
        )
