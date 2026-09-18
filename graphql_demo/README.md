# GraphQL Tutorial (FastAPI + Strawberry)

A from-zero, one-step-at-a-time GraphQL tutorial that rebuilds the
**Product** part of the domain used in `product_app` (the REST API
elsewhere in this repo), but through GraphQL instead.

No prior GraphQL knowledge is assumed. Every step below adds **exactly one
new thing** — one field, one file, one concept — on top of the previous
step, and every step is runnable. By the end you'll have rebuilt the same
small project one piece at a time.

Stack: **FastAPI** + **Strawberry** (`strawberry-graphql`) + **SQLAlchemy** +
**SQLite** — the same stack as `product_app`, just with a GraphQL layer
instead of REST routes.

**Libraries at a glance:**

| Library | Role | Where it's used |
|---|---|---|
| `strawberry-graphql` (`strawberry`) | Builds the GraphQL schema from Python type hints — `@strawberry.type`, `@strawberry.field`, `@strawberry.mutation`, `strawberry.Schema(...)` | `schema.py` |
| `strawberry.fastapi.GraphQLRouter` | Mounts the schema as a FastAPI route and serves the GraphiQL IDE at `/graphql` for free | `main.py` |
| `fastapi` | The web server/app itself (`FastAPI()`, `app.include_router(...)`) | `main.py` |
| `sqlalchemy` | ORM — `create_engine`, `sessionmaker`, `declarative_base`, `Column`/`Integer`/`String`/`Float` | `database.py`, `models.py` |
| SQLite (via SQLAlchemy) | Actual storage — `graphql_database.db`, kept separate from `product_app`'s `product_database.db` | `database.py` |

The code in this folder (`__init__.py`, `database.py`, `models.py`,
`schema.py`, `main.py`) is the finished result of every step below.

## Table of Contents

- [GraphQL Tutorial (FastAPI + Strawberry)](#graphql-tutorial-fastapi--strawberry)
  - [Table of Contents](#table-of-contents)
  - [1. What is GraphQL?](#1-what-is-graphql)
  - [2. REST vs GraphQL, side by side](#2-rest-vs-graphql-side-by-side)
  - [3. Setup](#3-setup)
  - [4. Step 1 — A bare FastAPI app (no GraphQL yet)](#4-step-1--a-bare-fastapi-app-no-graphql-yet)
  - [5. Step 2 — Your first schema: one hardcoded field](#5-step-2--your-first-schema-one-hardcoded-field)
  - [6. Step 3 — A second field on the same schema](#6-step-3--a-second-field-on-the-same-schema)
  - [7. Step 4 — Your first object type](#7-step-4--your-first-object-type)
  - [8. Step 5 — Returning a list](#8-step-5--returning-a-list)
  - [9. Step 6 — A field with an argument](#9-step-6--a-field-with-an-argument)
  - [10. Step 7 — A real database engine](#10-step-7--a-real-database-engine)
  - [11. Step 8 — Your first SQLAlchemy model](#11-step-8--your-first-sqlalchemy-model)
  - [12. Step 9 — Giving resolvers a DB session](#12-step-9--giving-resolvers-a-db-session)
  - [13. Step 10 — `products` reads from the database](#13-step-10--products-reads-from-the-database)
  - [14. Step 11 — `product(id)` reads from the database](#14-step-11--productid-reads-from-the-database)
  - [15. Step 12 — Your first mutation: create](#15-step-12--your-first-mutation-create)
  - [16. Step 13 — A second mutation: update](#16-step-13--a-second-mutation-update)
  - [17. Step 14 — A third mutation: delete](#17-step-14--a-third-mutation-delete)
  - [18. Testing your API](#18-testing-your-api)
  - [19. Final project structure](#19-final-project-structure)
  - [20. Where to go next](#20-where-to-go-next)

---

## 1. What is GraphQL?

GraphQL is a **query language for APIs** (and a runtime for executing those
queries). Instead of many fixed endpoints that each return a fixed shape of
data — like `product_app`'s `GET /products`, `GET /products/{id}` — you
expose **one endpoint** (usually `/graphql`) and the client describes
exactly what data it wants in the request itself.

Two core building blocks used in this tutorial:

| Concept | Purpose |
|---|---|
| **Query** | Read data (like `GET`) |
| **Mutation** | Write data (like `POST` / `PUT` / `DELETE`) |

The server exposes a **schema** — a typed contract of everything that can be
queried or mutated. The client can never ask for a field that doesn't exist
in the schema, and the server can never return more (or less) than what the
client asked for.

## 2. REST vs GraphQL, side by side

`product_app/main.py` already implements this domain as REST. Keep it open
in another tab — the steps below re-implement one piece of it in GraphQL at
a time.

| REST (`product_app`) | GraphQL equivalent |
|---|---|
| `GET /products` | `query { products { id name price } }` |
| `GET /products/{id}` | `query { product(id: 1) { name price } }` |
| `POST /products` | `mutation { createProduct(...) { id } }` |
| `PUT /products/{id}` | `mutation { updateProduct(id: 1, ...) { id } }` |
| `DELETE /products/{id}` | `mutation { deleteProduct(id: 1) }` |

The biggest practical difference: in REST, `ProductResponse` always returns
the same fixed shape. In GraphQL, the client picks exactly which fields it
wants back, and nothing else changes shape.

## 3. Setup

From the repo root, with your virtual environment active:

```bash
pip install "strawberry-graphql[fastapi]" "fastapi[standard]" sqlalchemy
```

`fastapi[standard]` pulls in `fastapi-cli`, which is what gives you the
`fastapi dev` command used to run the app throughout this tutorial.

Create the package folder once, up front — files are added to it one at a
time as you work through the steps:

```bash
graphql_demo/
└── __init__.py   # empty — just makes the folder importable, like product_app/__init__.py
```

## 4. Step 1 — A bare FastAPI app (no GraphQL yet)

Before adding GraphQL, confirm FastAPI itself runs. This has nothing
GraphQL-specific in it yet — it's just a sanity check.

```python
# graphql_demo/main.py
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    return {"status": "ok"}
```

Run it:

```bash
fastapi dev graphql_demo/main.py
```

Visit **http://127.0.0.1:8000/** and confirm you see `{"status": "ok"}`.
Once that works, every step from here only ever touches `main.py` (and
later, new files) — never anything outside `graphql_demo/`.

## 5. Step 2 — Your first schema: one hardcoded field

Add Strawberry. A GraphQL schema needs at least one `Query` type with at
least one field. Start with a single field that returns a hardcoded string —
no database, no arguments, nothing else.

```python
# graphql_demo/main.py
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

Restart `fastapi dev` and open **http://127.0.0.1:8000/graphql** — Strawberry
ships GraphiQL, an in-browser IDE for GraphQL, similar to how `/docs` gives
you Swagger UI for REST. Try:

```graphql
query {
  hello
}
```

`@strawberry.type` marks a Python class as a GraphQL **object type**.
`@strawberry.field` marks a method (or attribute) as queryable. Strawberry
reads the return type hint (`-> str`) to build the schema — the same
type-hint-driven style Pydantic uses in `product_app/schemas.py`.

## 6. Step 3 — A second field on the same schema

Add one more hardcoded field next to `hello`, to see that a `Query` type is
just a normal Python class — you add fields to it the same way you'd add
methods to any class.

```python
# graphql_demo/main.py  (Query class only — rest unchanged)
@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Hello, GraphQL!"

    @strawberry.field
    def version(self) -> str:
        return "1.0"
```

Now a single request can ask for both:

```graphql
query {
  hello
  version
}
```

This is the first look at GraphQL's defining trait: the client picks any
combination of fields it wants, in one round trip.

## 7. Step 4 — Your first object type

So far every field returned a plain scalar (`str`). Now define a GraphQL
type that mirrors `product_app/models.py`'s `ProductDB` — but without a
database yet, just a Python object, so you can focus on schema shape before
adding persistence.

```python
# graphql_demo/main.py  (add above Query, replace hello/version with this)
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

Try it — notice you must now ask for at least one field *inside* `product`,
since it's an object type, not a scalar:

```graphql
query {
  product {
    name
    price
  }
}
```

No `response_model` needed per-request like in FastAPI REST routes — the
schema itself is the contract.

## 8. Step 5 — Returning a list

Real data is a collection, not a single hardcoded row. Change the field to
return `list[Product]` instead of a single `Product`.

```python
# graphql_demo/main.py  (replace FIRST_PRODUCT / product field)
FAKE_PRODUCTS = [
    Product(id=1, name="Keyboard", description="Mechanical", price=59.99),
    Product(id=2, name="Mouse", description="Wireless", price=19.99),
]


@strawberry.type
class Query:
    @strawberry.field
    def products(self) -> list[Product]:
        return FAKE_PRODUCTS
```

```graphql
query {
  products {
    id
    name
  }
}
```

Any method decorated with `@strawberry.field` automatically becomes a
queryable field, and its Python parameters become GraphQL arguments — for
example, adding this to `Query`:

```python
@strawberry.field
def greet(self, name: str) -> str:
    return f"Hello, {name}!"
```

lets a client call it with an argument, just like `product(id: 1)`:

```graphql
query {
  greet(name: "komen")
}
```

Ask for just names, or everything — the resolver code doesn't change either
way; Strawberry only serializes the fields the client actually requested.

## 9. Step 6 — A field with an argument

Add a second field that takes an argument, the GraphQL equivalent of
`GET /products/{id}`'s path parameter.

```python
# graphql_demo/main.py  (add next to products)
@strawberry.field
def product(self, id: int) -> Product | None:
    return next((p for p in FAKE_PRODUCTS if p.id == id), None)
```

```graphql
query {
  product(id: 1) {
    name
    price
  }
}
```

Returning `Product | None` tells the schema this field is nullable — asking
for an `id` that doesn't exist returns `null` instead of an error. This
in-memory version is a stepping stone; the next steps replace
`FAKE_PRODUCTS` with a real database, split across dedicated files the same
way `product_app` separates `database.py`, `models.py`, and `main.py`.

## 10. Step 7 — A real database engine

Create `database.py` on its own, reusing the exact SQLAlchemy setup
`product_app/database.py` already uses — just pointed at its own SQLite
file (`graphql_database.db`, kept separate from `product_database.db`).
Nothing queries it yet; this step only wires up the engine and session.

```python
# graphql_demo/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

sqlite_file_name = "graphql_database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

## 11. Step 8 — Your first SQLAlchemy model

Add `models.py` with one table, mirroring `product_app/models.py`'s
`ProductDB` (minus the category relationship, to keep this demo small).

```python
# graphql_demo/models.py
from sqlalchemy import Column, Float, Integer, String

from .database import Base


class ProductDB(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    price = Column(Float)
```

Nothing runs this yet — the table only gets created once `main.py` calls
`Base.metadata.create_all(bind=engine)` in a later step.

## 12. Step 9 — Giving resolvers a DB session

A GraphQL resolver needs a DB session the same way a FastAPI route needs
`Depends(get_db)`. Strawberry's `Info` object carries a **context** — set it
up once per request via `GraphQLRouter(schema, context_getter=...)`. Create
`schema.py` and move the `Product` type there, but keep the resolvers
returning `FAKE_PRODUCTS` for now — this step only wires up *access* to a DB
session, it doesn't use it yet.

```python
# graphql_demo/schema.py
import strawberry
from typing import AsyncGenerator, Optional

from .database import SessionLocal


async def get_context() -> AsyncGenerator[dict, None]:
    db = SessionLocal()
    try:
        yield {"db": db}
    finally:
        db.close()


@strawberry.type
class Product:
    id: int
    name: str
    description: str
    price: float


FAKE_PRODUCTS = [
    Product(id=1, name="Keyboard", description="Mechanical", price=59.99),
    Product(id=2, name="Mouse", description="Wireless", price=19.99),
]


@strawberry.type
class Query:
    @strawberry.field
    def products(self, info: strawberry.types.Info) -> list[Product]:
        return FAKE_PRODUCTS

    @strawberry.field
    def product(self, info: strawberry.types.Info, id: int) -> Optional[Product]:
        return next((p for p in FAKE_PRODUCTS if p.id == id), None)


schema = strawberry.Schema(query=Query)
```

```python
# graphql_demo/main.py
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from .schema import get_context, schema

graphql_app = GraphQLRouter(schema, context_getter=get_context)

app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")
```

Every resolver now accepts `info: strawberry.types.Info`, which is how it
will reach `info.context["db"]` starting in the next step.

## 13. Step 10 — `products` reads from the database

Swap `FAKE_PRODUCTS` for a real query, one field at a time — start with
`products`. Add a small `from_db` helper to convert a `ProductDB` row into
the GraphQL `Product` type.

```python
# graphql_demo/schema.py  (changes only)
from .models import ProductDB


@strawberry.type
class Product:
    id: int
    name: str
    description: str
    price: float

    @classmethod
    def from_db(cls, product: ProductDB) -> "Product":
        return cls(
            id=product.id,
            name=product.name,
            description=product.description,
            price=product.price,
        )


@strawberry.type
class Query:
    @strawberry.field
    def products(self, info: strawberry.types.Info) -> list[Product]:
        db = info.context["db"]
        return [Product.from_db(p) for p in db.query(ProductDB).all()]
```

`from_db` is the one custom method added on top of an otherwise
auto-generated GraphQL type. `Product` (the `@strawberry.type`) is the
**GraphQL-facing** shape returned to clients; `ProductDB` (in `models.py`)
is the **SQLAlchemy** row fetched from the database — two different
classes. Every resolver needs to turn one into the other, so `from_db` is a
plain `classmethod` bolted onto `Product` purely for that conversion. It is
**not** itself a GraphQL field (Strawberry only exposes methods decorated
with `@strawberry.field` / `@strawberry.mutation`) — it's ordinary Python,
called directly by resolver code so the DB→GraphQL mapping is written once
instead of repeated in every resolver (see `products`, `product`,
`create_product`, and `update_product` in `schema.py`).

`main.py` also needs to actually create the table on startup:

```python
# graphql_demo/main.py  (add)
from .database import Base, engine

Base.metadata.create_all(bind=engine)
```

Run the app and query `products` — it now returns an empty list (`[]`)
since the table is empty. That's expected; the create mutation in step 12
is what populates it.

query{
  products {
    id
  }
}

## 14. Step 11 — `product(id)` reads from the database

Repeat the same swap for the second field.

```python
# graphql_demo/schema.py  (Query.product only)
@strawberry.field
def product(self, info: strawberry.types.Info, id: int) -> Optional[Product]:
    db = info.context["db"]
    product = db.query(ProductDB).filter(ProductDB.id == id).first()
    return Product.from_db(product) if product else None
```


`FAKE_PRODUCTS` is no longer referenced anywhere and can be deleted. Both
queries now hit the real database — this is the resolver-per-field model:
every field in `Query` is a small function that knows how to fetch its own
data, exactly like every route in `product_app/main.py` is a small function
that knows how to handle its own endpoint.

## 15. Step 12 — Your first mutation: create

Mutations are the GraphQL equivalent of `POST` / `PUT` / `DELETE`. Add a
`Mutation` type with a single field, `createProduct` — the only way so far
to get data into the (currently empty) table.

```python
# graphql_demo/schema.py  (add)
@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_product(
        self,
        info: strawberry.types.Info,
        name: str,
        description: str,
        price: float,
    ) -> Product:
        db = info.context["db"]
        db_product = ProductDB(name=name, description=description, price=price)
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return Product.from_db(db_product)


schema = strawberry.Schema(query=Query, mutation=Mutation)
```

Try it in GraphiQL:

```graphql
mutation {
  createProduct(name: "Monitor", description: "27-inch 4K", price: 299.99) {
    id
    name
  }
}
```

Then list it back:

query{
  product(id:1){
    id
    name
    price
  }
}

```graphql
query {
  products {
    id
    name
    price
  }
}
```

Notice a query and a mutation can be sent together in a single HTTP
request/response if you want — that's the round-trip savings GraphQL is
known for.

## 16. Step 13 — A second mutation: update

Add `updateProduct` next to `createProduct`, following the same shape.

```python
# graphql_demo/schema.py  (inside Mutation)
@strawberry.mutation
def update_product(
    self,
    info: strawberry.types.Info,
    id: int,
    name: str,
    description: str,
    price: float,
) -> Optional[Product]:
    db = info.context["db"]
    db_product = db.query(ProductDB).filter(ProductDB.id == id).first()
    if db_product is None:
        return None
    db_product.name = name
    db_product.description = description
    db_product.price = price
    db.commit()
    db.refresh(db_product)
    return Product.from_db(db_product)
```

```graphql
mutation {
  updateProduct(id: 1, name: "Monitor 27\"", description: "27-inch 4K", price: 279.99) {
    id
    name
    price
  }
}
```

## 17. Step 14 — A third mutation: delete

Add `deleteProduct`, returning a plain `bool` instead of a `Product` — there's
nothing left to return once the row is gone.

```python
# graphql_demo/schema.py  (inside Mutation)
@strawberry.mutation
def delete_product(self, info: strawberry.types.Info, id: int) -> bool:
    db = info.context["db"]
    db_product = db.query(ProductDB).filter(ProductDB.id == id).first()
    if db_product is None:
        return False
    db.delete(db_product)
    db.commit()
    return True
```

```graphql
mutation {
  deleteProduct(id: 1)
}
```

That completes CRUD: `products` / `product` (read), `createProduct`
(create), `updateProduct` (update), `deleteProduct` (delete) — the full set
of operations `product_app/main.py` exposes as REST routes, now as one
GraphQL schema.

## 18. Testing your API

- **GraphiQL** at `/graphql` (built into `strawberry.fastapi.GraphQLRouter`) —
  autocomplete, schema docs, and a query history, the GraphQL analog of
  `/docs` Swagger UI.
- **curl**, for scripting:

  ```bash
  curl -X POST http://127.0.0.1:8000/graphql \
    -H "Content-Type: application/json" \
    -d '{"query": "{ products { id name } }"}'
  ```

## 19. Final project structure

```
graphql_demo/
├── __init__.py
├── database.py   # engine, SessionLocal, Base                    (Step 7)
├── models.py      # ProductDB                                     (Step 8)
├── schema.py       # Product, Query, Mutation, get_context         (Steps 9-14)
└── main.py          # FastAPI app + GraphQLRouter mount             (Steps 1-2, 10)
```

## 20. Where to go next

This tutorial stops at a working Product CRUD API on purpose. Once this
feels comfortable, natural next steps to explore on your own (not covered
here):

- **Categories & relationships** — add a `CategoryDB` model and a
  `categories` field resolver on `Product`, the same many-to-many
  relationship `product_app/models.py` already has.
- **Authentication** — reuse `jwt/auth.py`'s `get_current_user` inside the
  GraphQL `context` to protect mutations, the same way `product_app/main.py`
  protects its `POST`/`PUT`/`DELETE` routes with `Depends(get_current_user)`.
- **Input types** — replace loose scalar arguments (`name`, `description`,
  `price`) with a single `@strawberry.input` type, GraphQL's equivalent of
  `ProductCreate(BaseModel)`.
- **DataLoader, pagination, structured errors, subscriptions** — see
  https://strawberry.rocks for guides on each once you're past the basics.
