import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database.models import User, Organization, UserCreate
from app.database.database import get_session


# Create in-memory SQLite database for testing
@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        yield session

    app.dependency_overrides[get_session] = get_session_override
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


class TestSignup:
    def test_signup_success(self, client: TestClient, session: Session):
        """Test successful user signup with organization"""
        signup_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "first_name": "John",
            "last_name": "Doe",
            "organization_name": "Test Corp",
            "organization_slug": "test-corp"
        }
        
        response = client.post("/api/signup", json=signup_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "test@example.com"
        assert data["user"]["first_name"] == "John"
        assert data["user"]["last_name"] == "Doe"
        assert data["user"]["role"] == "admin"
        assert data["user"]["organization_id"] is not None
        
        # Verify user was created in database
        user = session.exec(
            "SELECT * FROM user WHERE email = 'test@example.com'"
        ).first()
        assert user is not None
        
        # Verify organization was created
        org = session.exec(
            "SELECT * FROM organization WHERE slug = 'test-corp'"
        ).first()
        assert org is not None

    def test_signup_duplicate_email(self, client: TestClient, session: Session):
        """Test signup with existing email"""
        # Create existing user
        user = User(
            email="existing@example.com",
            hashed_password="hashed_password",
            first_name="Existing",
            last_name="User"
        )
        session.add(user)
        session.commit()
        
        signup_data = {
            "email": "existing@example.com",
            "password": "testpassword123",
            "first_name": "John",
            "last_name": "Doe",
            "organization_name": "Test Corp",
            "organization_slug": "test-corp"
        }
        
        response = client.post("/api/signup", json=signup_data)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_signup_duplicate_organization_slug(self, client: TestClient, session: Session):
        """Test signup with existing organization slug"""
        # Create existing organization
        org = Organization(
            name="Existing Corp",
            slug="existing-corp"
        )
        session.add(org)
        session.commit()
        
        signup_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "first_name": "John",
            "last_name": "Doe",
            "organization_name": "Test Corp",
            "organization_slug": "existing-corp"
        }
        
        response = client.post("/api/signup", json=signup_data)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_signup_weak_password(self, client: TestClient):
        """Test signup with weak password"""
        signup_data = {
            "email": "test@example.com",
            "password": "123",  # Too short
            "first_name": "John",
            "last_name": "Doe",
            "organization_name": "Test Corp",
            "organization_slug": "test-corp"
        }
        
        response = client.post("/api/signup", json=signup_data)
        assert response.status_code == 422  # Validation error


class TestUserModel:
    def test_password_hashing(self):
        """Test password hashing and verification"""
        password = "testpassword123"
        hashed = User.hash_password(password)
        
        # Verify hash is different from original
        assert hashed != password
        
        # Create user and verify password
        user = User(
            email="test@example.com",
            hashed_password=hashed,
            first_name="John",
            last_name="Doe"
        )
        
        assert user.verify_password(password) is True
        assert user.verify_password("wrongpassword") is False

    def test_full_name_property(self):
        """Test full_name property"""
        user = User(
            email="test@example.com",
            hashed_password="hashed",
            first_name="John",
            last_name="Doe"
        )
        
        assert user.full_name == "John Doe"


class TestOrganizationModel:
    def test_organization_creation(self, session: Session):
        """Test organization creation"""
        org = Organization(
            name="Test Corp",
            slug="test-corp"
        )
        session.add(org)
        session.commit()
        session.refresh(org)
        
        assert org.id is not None
        assert org.name == "Test Corp"
        assert org.slug == "test-corp"
        assert org.is_active is True 