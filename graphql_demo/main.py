from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from .database import Base, engine
from .schema import get_context, schema

Base.metadata.create_all(bind=engine)

graphql_app = GraphQLRouter(schema, context_getter=get_context)

app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")
