import os
os.environ["REDIS_URL"] = ""  # Force in-memory slowapi for test isolation

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from app import models, security

# Use a clean test sqlite DB
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(name="db")
def db_fixture():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(name="client")
def client_fixture(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

@pytest.fixture(name="test_user")
def test_user_fixture(db):
    hashed_password = security.hash_password("password123")
    user = models.User(email="test@example.com", hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture(name="token")
def token_fixture(test_user):
    return security.create_access_token(data={"sub": test_user.email})

@pytest.fixture(name="auth_client")
def auth_client_fixture(client, token):
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client
