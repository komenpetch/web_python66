# GraphQL Tutorial (FastAPI + Strawberry) — No-Database Version

This is a companion to [`README.md`](./README.md) with the **database part
removed**. It rebuilds the same **Product** CRUD API, but keeps everything
in an in-memory Python list instead of SQLAlchemy + SQLite. Use this when
you only want to learn the GraphQL layer (schema, queries, mutations)
without also learning an ORM at the same time — or as a quick prototype
before wiring up real persistence.

Everything through Step 6 of the original tutorial is **identical** here —
this doc only diverges starting where the original introduces the database
(`database.py`, `models.py`, `context`). Read `README.md` sections 1-2 first
if you haven't already; they aren't repeated below.

Stack: **FastAPI** + **Strawberry** (`strawberry-graphql`) — no SQLAlchemy,
no SQLite, no `database.py` / `models.py` at all. Everything lives in one
file, `main.py`.

## Table of Contents

- [1. Setup](#1-setup)
- [2. Step 1 — A bare FastAPI app](#2-step-1--a-bare-fastapi-app)
- [3. Step 2 — Your first schema field](#3-step-2--your-first-schema-field)
- [4. Step 3 — A second field](#4-step-3--a-second-field)
- [5. Step 4 — Your first object type](#5-step-4--your-first-object-type)
- [6. Step 5 — Returning a list](#6-step-5--returning-a-list)
- [7. Step 6 — A field with an argument](#7-step-6--a-field-with-an-argument)
- [8. Step 7 — Your first mutation: create](#8-step-7--your-first-mutation-create)
- [9. Step 8 — A second mutation: update](#9-step-8--a-second-mutation-update)
- [10. Step 9 — A third mutation: delete](#10-step-9--a-third-mutation-delete)
- [11. Testing your API](#11-testing-your-api)
- [12. Final project structure](#12-final-project-structure)
- [13. Trade-offs of skipping the database](#13-trade-offs-of-skipping-the-database)

---

## 1. Setup

```bash
pip install "strawberry-graphql[fastapi]" "fastapi[standard]"
```

No `sqlalchemy` — there's no ORM or database engine in this version.

## 2. Step 1 — A bare FastAPI app

Same as the database version's Step 1 — confirm FastAPI runs before adding
any GraphQL.

```python
# main.py
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    return {"status": "ok"}
```

```bash
fastapi dev main.py
```

## 3. Step 2 — Your first schema field

```python
# main.py
import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter


@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Hello, GraphQL!"


schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)

app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")
```

```graphql
query {
  hello
}
```

## 4. Step 3 — A second field

```python
@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Hello, GraphQL!"

    @strawberry.field
    def version(self) -> str:
        return "1.0"
```

## 5. Step 4 — Your first object type

```python
@strawberry.type
class Product:
    id: int
    name: str
    description: str
    price: float


FIRST_PRODUCT = Product(id=1, name="Keyboard", description="Mechanical", price=59.99)


@strawberry.type
class Query:
    @strawberry.field
    def product(self) -> Product:
        return FIRST_PRODUCT
```

```graphql
query {
  product {
    name
    price
  }
}
```

## 6. Step 5 — Returning a list

This is the key departure point: instead of a database table, `PRODUCTS` is
just a mutable module-level Python list that every resolver reads from and
writes to directly. There's no session, no commit, no `Depends(get_db)` —
the list itself *is* the storage.

```python
# main.py
PRODUCTS: list[Product] = [
    Product(id=1, name="Keyboard", description="Mechanical", price=59.99),
    Product(id=2, name="Mouse", description="Wireless", price=19.99),
]
_next_id = 3  # simple auto-increment counter, replaces the DB's autoincrement PK


@strawberry.type
class Query:
    @strawberry.field
    def products(self) -> list[Product]:
        return PRODUCTS
```

```graphql
query {
  products {
    id
    name
  }
}
```

## 7. Step 6 — A field with an argument

```python
@strawberry.field
def product(self, id: int) -> Product | None:
    return next((p for p in PRODUCTS if p.id == id), None)
```

```graphql
query {
  product(id: 1) {
    name
    price
  }
}
```

Same nullable-return behavior as the database version: an unknown `id`
returns `null`, not an error.

## 8. Step 7 — Your first mutation: create

Where the database version does `db.add()` / `db.commit()` / `db.refresh()`,
the in-memory version just appends to the list and hands out the next id
from the module-level counter.

```python
@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_product(self, name: str, description: str, price: float) -> Product:
        global _next_id
        new_product = Product(id=_next_id, name=name, description=description, price=price)
        PRODUCTS.append(new_product)
        _next_id += 1
        return new_product


schema = strawberry.Schema(query=Query, mutation=Mutation)
```

```graphql
mutation {
  createProduct(name: "Monitor", description: "27-inch 4K", price: 299.99) {
    id
    name
  }
}
```

## 9. Step 8 — A second mutation: update

```python
@strawberry.mutation
def update_product(self, id: int, name: str, description: str, price: float) -> Product | None:
    product = next((p for p in PRODUCTS if p.id == id), None)
    if product is None:
        return None
    product.name = name
    product.description = description
    product.price = price
    return product
```

Because `Product` is a plain Python object living in `PRODUCTS`, mutating
its attributes in place is enough — there's no `db.commit()` step to
persist the change, it's already "saved" since it's the same object the
list holds.

```graphql
mutation {
  updateProduct(id: 1, name: "Monitor 27\"", description: "27-inch 4K", price: 279.99) {
    id
    name
    price
  }
}
```

## 10. Step 9 — A third mutation: delete

```python
@strawberry.mutation
def delete_product(self, id: int) -> bool:
    product = next((p for p in PRODUCTS if p.id == id), None)
    if product is None:
        return False
    PRODUCTS.remove(product)
    return True
```

```graphql
mutation {
  deleteProduct(id: 1)
}
```

That's full CRUD again — `products` / `product` (read), `createProduct`
(create), `updateProduct` (update), `deleteProduct` (delete) — with zero
database code.

## 11. Testing your API

Same as the database version:

- **GraphiQL** at `/graphql`.
- **curl**:

  ```bash
  curl -X POST http://127.0.0.1:8000/graphql \
    -H "Content-Type: application/json" \
    -d '{"query": "{ products { id name } }"}'
  ```

## 12. Final project structure

```
graphql_demo_no_db/
└── main.py   # everything: Product, Query, Mutation, PRODUCTS list, FastAPI app
```

One file is enough here — `database.py`, `models.py`, and the separate
`schema.py` from the full tutorial exist only to organize database-related
concerns (engine/session, ORM model, context). Remove the database and
those concerns disappear, so the whole app can live in `main.py`. You can
still split `Product`/`Query`/`Mutation` into a `schema.py` for
organization once the file grows, exactly like the database version does —
that split is about file size, not about the database.

## 13. Trade-offs of skipping the database

| | In-memory (this doc) | Database (`README.md`) |
|---|---|---|
| Data survives server restart | ❌ (list resets on every reload) | ✅ (SQLite file on disk) |
| Multiple server processes share data | ❌ | ✅ |
| Setup complexity | Lower — no engine/session/model | Higher — engine, session, ORM model |
| Good for | Learning the GraphQL layer in isolation, quick prototypes | Anything you actually want to keep |

When you're ready to add persistence back, `README.md` sections 10-14 (Steps
7-14) show exactly how — swap the module-level list for `ProductDB` +
SQLAlchemy, and give each resolver access to `info.context["db"]`.
