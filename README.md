# Claude DDD — Order Management System

A Domain-Driven Design (DDD) implementation of an order management system in Python, demonstrating clean architecture with explicit **Bounded Contexts**, **Ports & Adapters**, and an **Anti-Corruption Layer**.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Bounded Contexts](#bounded-contexts)
  - [Shared Kernel](#shared-kernel)
  - [Customers](#customers-context)
  - [Catalog](#catalog-context)
  - [Ordering](#ordering-context)
  - [Interfaces](#interfaces)
- [Cross-Context Communication](#cross-context-communication)
- [Key Patterns](#key-patterns)
- [Getting Started](#getting-started)
- [API Reference](#api-reference)
- [Running Tests](#running-tests)

---

## Project Overview

| Field        | Value                  |
|--------------|------------------------|
| Package      | `claude_ddd`           |
| Version      | `0.1.0`                |
| Python       | `3.11.9`               |
| Author       | `napolifabrizio`       |
| Build Tool   | Poetry                 |
| Runtime Deps | `fastapi`, `uvicorn`   |
| Dev Deps     | `pytest >= 8.0`        |

The system models a simplified e-commerce order flow: creating customers and products, building orders with items, placing orders (with bulk discounts), and cancelling orders — all with domain events emitted throughout.

---

## Architecture

The codebase has two axes of organization:

1. **Horizontal axis — Bounded Contexts:** each business subdomain is a self-contained module with its own domain model, use cases, and infrastructure.
2. **Vertical axis — Layers within each context:** each context follows the same layered structure.

```
┌─────────────────────────────────────────────────────────────┐
│                  interfaces/cli/main.py                     │
│               (only file that crosses contexts)             │
├──────────────┬──────────────┬──────────────┬────────────────┤
│  customers/  │   catalog/   │  ordering/   │    shared/     │
│              │              │              │                │
│  domain/     │  domain/     │  domain/     │  domain/       │
│  application/│  application/│  application/│  infrastructure│
│  infra/      │  infra/      │  infra/      │                │
└──────────────┴──────────────┴──────────────┴────────────────┘
```

**Dependency rule:** inner layers never depend on outer layers. Bounded contexts never import each other's domain internals — they communicate through **ports** (ABCs) implemented by **adapters**.

---

## Project Structure

```
ftclaude/
├── src/claude_ddd/
│   ├── shared/
│   │   ├── domain/
│   │   │   ├── events/domain_event.py        # DomainEvent base class
│   │   │   └── value_objects/money.py        # Money (shared across contexts)
│   │   └── infrastructure/
│   │       └── event_bus/simple_event_bus.py # In-memory EventBus
│   │
│   ├── customers/
│   │   ├── domain/
│   │   │   ├── entities/customer.py
│   │   │   ├── value_objects/email.py
│   │   │   ├── value_objects/address.py
│   │   │   └── repositories/customer_repository.py
│   │   ├── application/
│   │   │   ├── dtos/customer_dto.py
│   │   │   └── use_cases/create_customer.py
│   │   └── infrastructure/
│   │       └── persistence/in_memory_customer_repository.py
│   │
│   ├── catalog/
│   │   ├── domain/
│   │   │   ├── entities/product.py
│   │   │   └── repositories/product_repository.py
│   │   ├── application/
│   │   │   ├── dtos/product_dto.py
│   │   │   └── use_cases/create_product.py
│   │   └── infrastructure/
│   │       └── persistence/in_memory_product_repository.py
│   │
│   ├── ordering/
│   │   ├── domain/
│   │   │   ├── entities/order.py
│   │   │   ├── events/order_events.py
│   │   │   ├── repositories/order_repository.py
│   │   │   ├── services/pricing_service.py
│   │   │   └── ports/                        # Cross-context interfaces
│   │   │       ├── product_query.py          # IProductQuery + ProductInfo
│   │   │       └── customer_query.py         # ICustomerQuery
│   │   ├── application/
│   │   │   ├── dtos/order_dto.py
│   │   │   └── use_cases/
│   │   │       ├── create_order.py
│   │   │       ├── add_item_to_order.py
│   │   │       ├── place_order.py
│   │   │       └── cancel_order.py
│   │   └── infrastructure/
│   │       ├── persistence/in_memory_order_repository.py
│   │       └── adapters/                     # Anti-corruption layer
│   │           ├── catalog_product_query_adapter.py
│   │           └── customer_query_adapter.py
│   │
│   └── interfaces/
│       ├── cli/main.py                       # CLI composition root
│       └── api/
│           ├── app.py                        # FastAPI composition root
│           └── routers/
│               ├── customers.py
│               ├── products.py
│               └── orders.py
│
├── tests/
│   ├── domain/
│   │   ├── test_entities.py
│   │   └── test_value_objects.py
│   └── application/
│       └── test_use_cases.py
├── pyproject.toml
└── .gitignore
```

---

## Bounded Contexts

### Shared Kernel

Contains concepts genuinely shared across all contexts. Changes here affect everyone — keep it minimal.

| Module | Class | Description |
|--------|-------|-------------|
| `shared/domain/value_objects/money.py` | `Money` | Financial value with `amount` (Decimal) and `currency`. Supports `+`, `-`, `*`. Prevents mixing currencies. |
| `shared/domain/events/domain_event.py` | `DomainEvent` | Abstract frozen dataclass with `event_id` (UUID) and `occurred_at` (datetime). |
| `shared/infrastructure/event_bus/simple_event_bus.py` | `EventBus` | In-memory Pub/Sub: `subscribe(event_type, handler)` / `publish(event)`. |

### Customers Context

Manages customer identity and contact data.

| Module | Class | Description |
|--------|-------|-------------|
| `customers/domain/entities/customer.py` | `Customer` | Aggregate root. Holds `name`, `Email`, `Address`. |
| `customers/domain/value_objects/email.py` | `Email` | Validated email via regex. Immutable. |
| `customers/domain/value_objects/address.py` | `Address` | Street address. All fields required except `country` (defaults to `"BR"`). |
| `customers/domain/repositories/customer_repository.py` | `CustomerRepository` | Abstract: `save`, `find_by_id`, `find_by_email`, `delete`. |
| `customers/application/use_cases/create_customer.py` | `CreateCustomerUseCase` | Validates email uniqueness, creates `Customer`, persists. |

### Catalog Context

Manages the product catalog and stock levels.

| Module | Class | Description |
|--------|-------|-------------|
| `catalog/domain/entities/product.py` | `Product` | Aggregate root. Holds `name`, `Money` price, `stock`. Methods: `is_available()`, `decrease_stock()`, `increase_stock()`. |
| `catalog/domain/repositories/product_repository.py` | `ProductRepository` | Abstract: `save`, `find_by_id`, `find_all`, `delete`. |
| `catalog/application/use_cases/create_product.py` | `CreateProductUseCase` | Creates a `Product` with a `Money` price, persists. |

### Ordering Context

The core context: manages order lifecycle and pricing.

#### Domain

| Module | Class | Description |
|--------|-------|-------------|
| `ordering/domain/entities/order.py` | `Order`, `OrderItem`, `OrderStatus` | Aggregate root. State machine: `DRAFT → PLACED` or `DRAFT → CANCELLED`. Items can only be added/removed in `DRAFT`. |
| `ordering/domain/events/order_events.py` | `OrderCreated`, `OrderItemAdded`, `OrderPlaced`, `OrderCancelled` | Emitted by `Order` on state changes. Stored in `Order._events`, drained via `pull_events()`. |
| `ordering/domain/services/pricing_service.py` | `PricingService` | Applies **10% bulk discount** when an order has ≥5 total items. |

**Order state machine:**
```
DRAFT ──► PLACED
  │
  └──────► CANCELLED
```

#### Ports (Cross-Context Interfaces)

Ports define what the ordering context **needs** from the outside world, expressed in ordering's own language. They are ABCs — the domain has no idea how they are implemented.

| Port | Description |
|------|-------------|
| `ordering/domain/ports/product_query.py` | `IProductQuery` — `find_by_id(UUID) → ProductInfo \| None` and `reserve_stock(UUID, int)`. `ProductInfo` is ordering's own read model of a product (id, name, price, currency, stock). |
| `ordering/domain/ports/customer_query.py` | `ICustomerQuery` — `exists(UUID) → bool`. |

#### Use Cases

| Class | Input → Output | Description |
|-------|----------------|-------------|
| `CreateOrderUseCase` | `CreateOrderInput → OrderOutput` | Validates customer exists (via `ICustomerQuery`), creates a `DRAFT` order, publishes `OrderCreated`. |
| `AddItemToOrderUseCase` | `AddItemInput → OrderOutput` | Validates order/product/stock (via `IProductQuery`), adds item to order, publishes `OrderItemAdded`. |
| `PlaceOrderUseCase` | `PlaceOrderInput → OrderOutput` | Reserves stock for all items (via `IProductQuery.reserve_stock`), places order, applies pricing discount, publishes `OrderPlaced`. |
| `CancelOrderUseCase` | `CancelOrderInput → OrderOutput` | Cancels order, publishes `OrderCancelled`. |

#### Adapters (Anti-Corruption Layer)

Adapters are the concrete bridge between the ordering context and other contexts. They live in `ordering/infrastructure/adapters/` — inside ordering's infrastructure, because it is ordering's responsibility to translate.

| Adapter | Implements | Delegates to |
|---------|-----------|--------------|
| `CatalogProductQueryAdapter` | `IProductQuery` | `catalog`'s `ProductRepository`. Translates `Product → ProductInfo`. |
| `CustomerQueryAdapter` | `ICustomerQuery` | `customers`'s `CustomerRepository`. |

### Interfaces

Two composition roots are provided, each wiring the full DI container independently.

**`interfaces/cli/main.py`** — CLI composition root. `build_container()` instantiates repositories, builds adapters, injects them into use cases, and runs a demo flow.

**`interfaces/api/app.py`** — FastAPI composition root. Builds the same container once on startup (via `lifespan`) and exposes it to all route handlers. Routers are organized by bounded context under `interfaces/api/routers/`.

---

## Cross-Context Communication

```
ordering/application/use_cases/create_order.py
    │
    │  depends on (interface)
    ▼
ordering/domain/ports/customer_query.py  ◄── ICustomerQuery (ABC)
    ▲
    │  implemented by
    │
ordering/infrastructure/adapters/customer_query_adapter.py
    │
    │  delegates to
    ▼
customers/infrastructure/persistence/in_memory_customer_repository.py
```

The same pattern applies for `IProductQuery` ↔ `CatalogProductQueryAdapter` ↔ catalog's `ProductRepository`.

**Rule:** `ordering/domain/` and `ordering/application/` never import from `catalog/` or `customers/`. Only the adapters (infrastructure layer) cross that boundary, and only at the composition root are they wired together.

---

## Key Patterns

- **Bounded Contexts:** Each subdomain owns its model. `ordering` has its own `ProductInfo` (not `catalog.Product`).
- **Ports & Adapters (Hexagonal Architecture):** Ports are ABCs in the domain; adapters are concrete implementations in infrastructure.
- **Anti-Corruption Layer:** Adapters translate foreign models into the consuming context's language, preventing concept leakage.
- **Dependency Injection:** Use cases receive all dependencies via constructor. `build_container()` is the single composition root.
- **Event Flow:**
  ```
  Order.place()
      └─► appends OrderPlaced to Order._events
  Use case calls order.pull_events()
      └─► retrieves and clears _events
  Use case calls event_bus.publish(event)
      └─► dispatches to all subscribers
  ```
- **Repository Isolation:** In-memory repos `deepcopy` on every read — callers cannot mutate stored aggregates.
- **Money Precision:** `Money` uses `decimal.Decimal` (not `float`) to avoid floating-point rounding errors.

---

## Getting Started

**Prerequisites:** Python 3.11.9, [Poetry](https://python-poetry.org/)

```bash
# Install dependencies
poetry install

# Run the CLI demo
poetry run python -m claude_ddd.interfaces.cli.main

# Run the FastAPI server
poetry run uvicorn claude_ddd.interfaces.api.app:app --reload
```

Interactive API docs available at `http://localhost:8000/docs` once the server is running.

---

## API Reference

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/customers` | Create a customer |
| `GET` | `/customers/{id}` | Get a customer by ID |
| `POST` | `/products` | Create a product |
| `GET` | `/products` | List all products |
| `GET` | `/products/{id}` | Get a product by ID |
| `POST` | `/orders` | Create a draft order |
| `GET` | `/orders/{id}` | Get an order by ID |
| `POST` | `/orders/{id}/items` | Add an item to a draft order |
| `POST` | `/orders/{id}/place` | Place the order (applies bulk discount if ≥5 items) |
| `POST` | `/orders/{id}/cancel` | Cancel the order |

Domain rule violations (e.g. insufficient stock, duplicate email, invalid state transition) are returned as `422 Unprocessable Entity` with a descriptive `detail` message.

---

## Running Tests

```bash
# Run all tests
poetry run pytest

# Verbose output
poetry run pytest -v

# Single file
poetry run pytest tests/domain/test_entities.py

# Single test by name
poetry run pytest -k "test_order_place"
```
