# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
poetry install

# Run all tests
poetry run pytest

# Run tests with verbose output
poetry run pytest -v

# Run a single test file
poetry run pytest tests/domain/test_entities.py

# Run a single test by name
poetry run pytest -k "test_order_place"

# Run the CLI demo
poetry run python -m claude_ddd.interfaces.cli.main
```

## Architecture

This is a **Domain-Driven Design (DDD)** implementation with explicit **Bounded Contexts**. The two axes of organization are:

1. **Horizontal:** Bounded Contexts (`customers/`, `catalog/`, `ordering/`, `shared/`)
2. **Vertical:** Layers within each context (`domain/`, `application/`, `infrastructure/`)

The dependency rule applies both ways — inner layers never depend on outer layers, and bounded contexts never import each other's internals directly.

```
Interfaces → Application → Domain ← Infrastructure
                 ↑
         (via Ports/ABCs)
```

### Bounded Contexts

**`src/claude_ddd/shared/`** — Shared Kernel: concepts reused across all contexts.
- `domain/value_objects/money.py` — `Money` (Decimal-based, immutable)
- `domain/events/domain_event.py` — `DomainEvent` abstract base class
- `infrastructure/event_bus/simple_event_bus.py` — In-memory Pub/Sub `EventBus`

**`src/claude_ddd/customers/`** — Customer management context.
- `domain/entities/customer.py` — `Customer` aggregate (name, Email, Address)
- `domain/value_objects/` — `Email`, `Address` (customers-specific value objects)
- `domain/repositories/customer_repository.py` — Abstract `CustomerRepository`
- `application/use_cases/create_customer.py` — `CreateCustomerUseCase`
- `infrastructure/persistence/` — `InMemoryCustomerRepository`

**`src/claude_ddd/catalog/`** — Product catalog context.
- `domain/entities/product.py` — `Product` aggregate (name, Money price, stock)
- `domain/repositories/product_repository.py` — Abstract `ProductRepository`
- `application/use_cases/create_product.py` — `CreateProductUseCase`
- `infrastructure/persistence/` — `InMemoryProductRepository`

**`src/claude_ddd/ordering/`** — Order management context.
- `domain/entities/order.py` — `Order` aggregate with state machine: `DRAFT → PLACED` or `DRAFT → CANCELLED`. Items can only be added/removed in `DRAFT`.
- `domain/events/order_events.py` — `OrderCreated`, `OrderItemAdded`, `OrderPlaced`, `OrderCancelled`; stored in `Order._events` and drained via `order.pull_events()`.
- `domain/repositories/order_repository.py` — Abstract `OrderRepository`
- `domain/services/pricing_service.py` — `PricingService`: 10% bulk discount when order has ≥5 items.
- `domain/ports/` — **Cross-context interfaces** (the boundary):
  - `product_query.py` — `IProductQuery` ABC + `ProductInfo` read model (ordering's view of a product)
  - `customer_query.py` — `ICustomerQuery` ABC (`exists(UUID) -> bool`)
- `application/use_cases/` — `CreateOrderUseCase`, `AddItemToOrderUseCase`, `PlaceOrderUseCase`, `CancelOrderUseCase`
- `application/dtos/order_dto.py` — Input/output dataclasses
- `infrastructure/persistence/` — `InMemoryOrderRepository`
- `infrastructure/adapters/` — **Anti-corruption layer** (ACL):
  - `CatalogProductQueryAdapter` — implements `IProductQuery` using catalog's `ProductRepository`
  - `CustomerQueryAdapter` — implements `ICustomerQuery` using customers' `CustomerRepository`

**`src/claude_ddd/interfaces/cli/main.py`** — Composition root. The **only** file allowed to import across bounded contexts. `build_container()` wires all repositories, adapters, and use cases manually.

## Key Patterns

- **Bounded Contexts:** Each context owns its domain model. `ordering` never imports `catalog.Product` directly — it uses `IProductQuery` (a port) and receives `ProductInfo` (its own read model).
- **Ports & Adapters (Hexagonal):** `ordering/domain/ports/` defines what the context needs from the outside world as ABCs. `ordering/infrastructure/adapters/` provides the concrete bridge to other contexts.
- **Anti-Corruption Layer:** `CatalogProductQueryAdapter` translates catalog's `Product` entity into ordering's `ProductInfo`, preventing catalog concepts from leaking into ordering's domain model.
- **Dependency injection:** Use cases receive all dependencies via constructor; `build_container()` is the composition root.
- **Event flow:** aggregate appends to `_events` → use case calls `pull_events()` → publishes to `EventBus` → subscribers handle.
- **Repository isolation:** In-memory repos deepcopy on every read — callers cannot mutate stored state.
