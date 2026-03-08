# Claude DDD — Order Management System

A Domain-Driven Design (DDD) implementation of an order management system in Python, demonstrating clean architecture principles with a clear separation between domain logic, application, and infrastructure layers.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Layers & Files](#layers--files)
  - [Domain Layer](#domain-layer)
  - [Application Layer](#application-layer)
  - [Infrastructure Layer](#infrastructure-layer)
  - [Interface Layer](#interface-layer)
  - [Tests](#tests)
- [Key Patterns & Design Decisions](#key-patterns--design-decisions)
- [Getting Started](#getting-started)
- [Running Tests](#running-tests)

---

## Project Overview

| Field       | Value                      |
|-------------|----------------------------|
| Package     | `claude_ddd`               |
| Version     | `0.1.0`                    |
| Python      | `3.11.9`                   |
| Author      | `napolifabrizio`           |
| Build Tool  | Poetry                     |
| Runtime Deps| None (pure Python)         |
| Dev Deps    | `pytest >= 8.0`            |

The system models a simplified e-commerce order flow: creating customers and products, building orders with items, placing orders (with bulk discounts), and cancelling orders — all with domain events emitted throughout.

---

## Architecture

```
┌──────────────────────────────────────────────┐
│         Interfaces  (CLI, Web, etc.)         │
├──────────────────────────────────────────────┤
│         Application (Use Cases, DTOs)        │
├──────────────────────────────────────────────┤
│  Domain (Entities, Value Objects, Events,    │
│          Repository Interfaces, Services)    │
├──────────────────────────────────────────────┤
│  Infrastructure (Persistence, Event Bus)     │
└──────────────────────────────────────────────┘
```

**Dependency rule:** inner layers never depend on outer layers. Infrastructure implements domain interfaces; use cases depend only on abstractions.

---

## Project Structure

```
ftclaude/
├── src/
│   ├── domain/
│   │   ├── entities/               # Aggregate roots
│   │   │   ├── customer.py
│   │   │   ├── order.py
│   │   │   └── product.py
│   │   ├── value_objects/          # Immutable domain primitives
│   │   │   ├── address.py
│   │   │   ├── email.py
│   │   │   └── money.py
│   │   ├── events/                 # Domain events
│   │   │   └── domain_event.py
│   │   ├── repositories/           # Repository interfaces (abstractions)
│   │   │   ├── customer_repository.py
│   │   │   ├── order_repository.py
│   │   │   └── product_repository.py
│   │   └── services/               # Domain services
│   │       └── pricing_service.py
│   ├── application/
│   │   ├── dtos/                   # Data Transfer Objects
│   │   │   ├── customer_dto.py
│   │   │   ├── order_dto.py
│   │   │   └── product_dto.py
│   │   └── use_cases/              # Application use cases
│   │       ├── create_customer.py
│   │       ├── create_product.py
│   │       ├── create_order.py
│   │       ├── add_item_to_order.py
│   │       ├── place_order.py
│   │       └── cancel_order.py
│   ├── infrastructure/
│   │   ├── persistence/            # In-memory repository implementations
│   │   │   ├── in_memory_customer_repository.py
│   │   │   ├── in_memory_order_repository.py
│   │   │   └── in_memory_product_repository.py
│   │   └── event_bus/              # Event publisher
│   │       └── simple_event_bus.py
│   └── interfaces/
│       └── cli/
│           └── main.py             # CLI demo + dependency injection container
├── tests/
│   ├── domain/
│   │   ├── test_entities.py        # Unit tests for entities
│   │   └── test_value_objects.py   # Unit tests for value objects
│   └── application/
│       └── test_use_cases.py       # Integration tests for use cases
├── pyproject.toml
├── poetry.lock
└── .gitignore
```

---

## Layers & Files

### Domain Layer

The domain layer is the heart of the system. It contains the business rules and has **no external dependencies**.

#### Entities

Entities are aggregate roots identified by a UUID. Equality is based on identity, not content.

| File | Class | Description |
|------|-------|-------------|
| `entities/customer.py` | `Customer` | Customer aggregate. Holds `name`, `Email`, and `Address`. Supports `change_address()` and `change_email()`. |
| `entities/order.py` | `Order`, `OrderItem`, `OrderStatus` | Order aggregate. Manages a collection of `OrderItem`s through a state machine (`DRAFT → PLACED / CANCELLED`). Emits domain events on transitions. |
| `entities/product.py` | `Product` | Product aggregate. Manages `name`, `Money` price, and `stock`. Supports `is_available()`, `decrease_stock()`, and `increase_stock()`. |

**Order state machine:**

```
DRAFT ──► PLACED
  │
  └──────► CANCELLED
```

Items can only be added/removed in `DRAFT` state.

#### Value Objects

Value objects are **immutable** (frozen dataclasses) and compared by content, not identity.

| File | Class | Description |
|------|-------|-------------|
| `value_objects/money.py` | `Money` | Financial value with `amount` (Decimal) and `currency`. Supports `+`, `-`, `*`. Uses `Decimal` for precision. Prevents mixing currencies. |
| `value_objects/email.py` | `Email` | Validated email address using regex. Raises `ValueError` on invalid format. |
| `value_objects/address.py` | `Address` | Street address with `street`, `number`, `city`, `state`, `zip_code`, `country`. All fields required (except country, which defaults to `"BR"`). |

#### Domain Events

All events extend `DomainEvent` (abstract frozen dataclass) which provides auto-generated `event_id` (UUID) and `occurred_at` (datetime).

| Event | Emitted When |
|-------|-------------|
| `OrderCreated` | A new order is created |
| `OrderItemAdded` | An item is added to an order |
| `OrderPlaced` | An order transitions to PLACED |
| `OrderCancelled` | An order is cancelled |

Events are stored internally in the `Order._events` list and retrieved via `pull_events()`, which also clears the list.

#### Repository Interfaces

Abstract base classes defining the persistence contract. Located in the domain layer so the domain doesn't depend on infrastructure.

| File | Interface | Methods |
|------|-----------|---------|
| `repositories/customer_repository.py` | `CustomerRepository` | `save`, `find_by_id`, `find_by_email`, `delete` |
| `repositories/order_repository.py` | `OrderRepository` | `save`, `find_by_id`, `find_by_customer`, `delete` |
| `repositories/product_repository.py` | `ProductRepository` | `save`, `find_by_id`, `find_all`, `delete` |

#### Domain Services

| File | Class | Description |
|------|-------|-------------|
| `services/pricing_service.py` | `PricingService` | Cross-entity logic for pricing. Applies a **10% bulk discount** when an order has 5 or more items. Methods: `calculate_discount(order)` and `calculate_final_total(order)`. |

---

### Application Layer

The application layer orchestrates domain objects and infrastructure via **use cases**. It communicates with the outside world through **DTOs**.

#### Use Cases

| File | Class | Input → Output | Description |
|------|-------|----------------|-------------|
| `use_cases/create_customer.py` | `CreateCustomerUseCase` | `CreateCustomerInput → CustomerOutput` | Validates email uniqueness, creates `Customer` with value objects, persists. |
| `use_cases/create_product.py` | `CreateProductUseCase` | `CreateProductInput → ProductOutput` | Creates a `Product` with a `Money` price, persists. |
| `use_cases/create_order.py` | `CreateOrderUseCase` | `CreateOrderInput → OrderOutput` | Validates customer exists, creates a `DRAFT` order, publishes `OrderCreated`. |
| `use_cases/add_item_to_order.py` | `AddItemToOrderUseCase` | `AddItemInput → OrderOutput` | Validates order/product/stock, adds item to order, publishes `OrderItemAdded`. |
| `use_cases/place_order.py` | `PlaceOrderUseCase` | `PlaceOrderInput → OrderOutput` | Places order, decreases stock for all items, applies pricing discount, publishes `OrderPlaced`. |
| `use_cases/cancel_order.py` | `CancelOrderUseCase` | `CancelOrderInput → OrderOutput` | Cancels order, publishes `OrderCancelled`. |

#### DTOs

DTOs decouple the interface/API layer from domain models.

| File | Input DTOs | Output DTOs |
|------|-----------|-------------|
| `dtos/customer_dto.py` | `CreateCustomerInput` | `CustomerOutput` |
| `dtos/order_dto.py` | `CreateOrderInput`, `AddItemInput`, `PlaceOrderInput`, `CancelOrderInput` | `OrderOutput`, `OrderItemOutput` |
| `dtos/product_dto.py` | `CreateProductInput` | `ProductOutput` |

---

### Infrastructure Layer

Concrete implementations of domain abstractions. Can be swapped without touching the domain or use cases.

#### Persistence

All repositories are **in-memory** implementations backed by a Python dict. They use `copy.deepcopy()` on retrieval to prevent external mutation of stored aggregates.

| File | Implements |
|------|-----------|
| `persistence/in_memory_customer_repository.py` | `CustomerRepository` |
| `persistence/in_memory_order_repository.py` | `OrderRepository` |
| `persistence/in_memory_product_repository.py` | `ProductRepository` |

#### Event Bus

| File | Class | Description |
|------|-------|-------------|
| `event_bus/simple_event_bus.py` | `EventBus` | In-memory Pub/Sub dispatcher. `subscribe(event_type, handler)` registers a callable; `publish(event)` dispatches to all registered handlers. |

---

### Interface Layer

#### CLI (`interfaces/cli/main.py`)

| Function | Description |
|----------|-------------|
| `build_container()` | Manual dependency injection: wires repositories, event bus, services, and use cases. Returns a dict of use cases. |
| `log_event(event)` | Simple stdout logger subscribed to all order events. |
| `main()` | End-to-end demo: creates a customer, 3 products, an order, adds items (triggering bulk discount), places it, then creates and cancels a second order. |

---

### Tests

Tests are split by layer, following the same directory structure as `src/`.

#### Domain Tests (`tests/domain/`)

| File | Suite | What is tested |
|------|-------|---------------|
| `test_entities.py` | `TestProduct` | Stock availability, stock decrease/increase, negative stock validation |
| `test_entities.py` | `TestOrder` | State machine transitions, item management, total calculation, event emission |
| `test_value_objects.py` | `TestMoney` | Arithmetic operations, currency validation, immutability |
| `test_value_objects.py` | `TestEmail` | Valid/invalid email formats, immutability |
| `test_value_objects.py` | `TestAddress` | Required fields, immutability |

#### Application Tests (`tests/application/`)

| File | Suite | What is tested |
|------|-------|---------------|
| `test_use_cases.py` | `TestCreateCustomer` | Happy path, duplicate email, invalid email |
| `test_use_cases.py` | `TestCreateOrder` | Existing customer, unknown customer |
| `test_use_cases.py` | `TestAddItemToOrder` | Happy path, insufficient stock |
| `test_use_cases.py` | `TestPlaceOrder` | Stock decrease, bulk discount (6 items → 10% off) |
| `test_use_cases.py` | `TestCancelOrder` | Happy path, unknown order |

---

## Key Patterns & Design Decisions

### Domain-Driven Design (DDD)

- **Aggregates:** `Customer`, `Order`, `Product` are aggregate roots with UUID identity.
- **Value Objects:** `Money`, `Email`, `Address` are immutable and compared by value.
- **Domain Events:** Emitted by aggregates on state changes and published via `EventBus`.
- **Repository Pattern:** Interfaces defined in the domain; implementations in infrastructure.
- **Domain Services:** `PricingService` encapsulates cross-aggregate business logic.

### Event Flow

```
Order.place()
    └─► appends OrderPlaced to Order._events
Use case calls order.pull_events()
    └─► retrieves and clears _events
Use case calls event_bus.publish(event)
    └─► dispatches to all subscribers (e.g., log_event)
```

### Bulk Discount

Applied at place-order time via `PricingService`:
- **Threshold:** 5 or more total items
- **Discount:** 10%
- **Example:** 6 items × BRL 100 = BRL 600 → BRL 540 after discount

### Money Precision

`Money` uses `decimal.Decimal` (not `float`) to avoid floating-point rounding errors in financial calculations.

### Immutability in Repositories

In-memory repositories use `copy.deepcopy()` on every read, simulating the isolation that a real database connection would provide and preventing callers from accidentally mutating stored state.

---

## Getting Started

**Prerequisites:** Python 3.11.9, [Poetry](https://python-poetry.org/)

```bash
# Install dependencies
poetry install

# Run the CLI demo
poetry run python -m claude_ddd.interfaces.cli.main
```

---

## Running Tests

```bash
poetry run pytest
```

Run with verbose output:

```bash
poetry run pytest -v
```
