from ariadne import load_schema_from_path, snake_case_fallback_resolvers
from ariadne.asgi import GraphQL
from ariadne.contrib.federation import make_federated_schema
from graphql import GraphQLSchema

from .resolvers import mutation, query, user

type_defs: str = load_schema_from_path("app")

schema: GraphQLSchema = make_federated_schema(
    type_defs,
    query,
    mutation,
    user,
    snake_case_fallback_resolvers,
)

app = GraphQL(schema=schema, debug=True)
