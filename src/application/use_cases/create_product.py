from src.application.dtos.product_dto import CreateProductInput, ProductOutput
from src.domain.entities.product import Product
from src.domain.repositories.product_repository import ProductRepository
from src.domain.value_objects.money import Money


class CreateProductUseCase:

    def __init__(self, product_repo: ProductRepository):
        self._product_repo = product_repo

    def execute(self, input_data: CreateProductInput) -> ProductOutput:
        price = Money.of(input_data.price, input_data.currency)
        product = Product(name=input_data.name, price=price, stock=input_data.stock)
        self._product_repo.save(product)

        return ProductOutput(
            product_id=product.id,
            name=product.name,
            price=product.price.amount,
            currency=product.price.currency,
            stock=product.stock,
        )
