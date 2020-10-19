import pytest
from pymongo import MongoClient
from starlette.testclient import TestClient

from app.main import app
from app.settings import settings


@pytest.fixture()
def test_db():
    client = MongoClient(settings.mongo_url)
    db_name = settings.mongo_db_name
    db = client[db_name]
    client.drop_database(db)
    yield db
    client.drop_database(db)


@pytest.fixture()
def test_collection(test_db):
    collection_name = settings.mongo_collection_name
    collection = test_db[collection_name]
    collection.drop()
    collection.create_index("email", unique=True)
    yield collection
    collection.drop()


@pytest.fixture()
def test_client():
    return TestClient(app)
