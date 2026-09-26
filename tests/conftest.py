"""
tests/conftest.py -- Pytest configuration & shared fixtures for PromptArmor
Provides in-memory SQLite isolation and deterministic mocks for sub-second test execution.
"""
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.models.database import Base
from app.services.audit import get_db

# ---------------------------------------------------------------------------
# 1. In-Memory SQLite Isolation with StaticPool
# ---------------------------------------------------------------------------
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_test_db():
    """Create all tables fresh before each test and drop them afterward."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    """Provide a clean, isolated in-memory database session per test."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def client(db_session):
    """
    TestClient with get_db overridden to use the fast in-memory SQLite database.
    """
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# 2. Deterministic Mocks for External Groq LLM Calls
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_clean_semantic_judge():
    """Mock Layer 3 Semantic Judge to approve clean prompts instantly."""
    with patch("app.main.evaluate_prompt_semantic", new_callable=AsyncMock) as mock:
        mock.return_value = {
            "is_jailbreak": False,
            "risk_category": "NONE",
            "risk_score": 0.0,
            "reasoning": "Benign prompt approved by mock judge.",
        }
        yield mock


@pytest.fixture
def mock_attack_semantic_judge():
    """Mock Layer 3 Semantic Judge to flag adversarial prompts."""
    with patch("app.main.evaluate_prompt_semantic", new_callable=AsyncMock) as mock:
        mock.return_value = {
            "is_jailbreak": True,
            "risk_category": "OWASP_LLM08_CONTEXT_EXTRACTION",
            "risk_score": 0.95,
            "reasoning": "Adversarial prompt injection detected by mock judge.",
        }
        yield mock


@pytest.fixture
def mock_downstream_llm():
    """Mock downstream LLM forwarder to return instant text without network latency."""
    with patch("app.main.forward_to_llm", new_callable=AsyncMock) as mock:
        mock.return_value = "This is a deterministic mocked LLM answer."
        yield mock
