import pytest
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import Customer
from config import Config
from datetime import date, datetime

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:' # Use in-memory SQLite for tests
    WTF_CSRF_ENABLED = False # Disable CSRF for testing forms if you have them

@pytest.fixture(scope='session')
def app():
    """Session-wide test `Flask` application."""
    app = create_app(TestConfig)
    return app

@pytest.fixture(scope='function')
def test_client(app):
    """A test client for the app."""
    with app.test_client() as client:
        with app.app_context():
            db.create_all() # Create tables for each test function
            yield client
            db.session.remove()
            db.drop_all() # Drop tables after each test function

@pytest.fixture(scope='function')
def init_database(test_client): # Relies on test_client to ensure app_context and db setup
    """Populate the database with sample data for each test function."""
    # Add sample customers
    customer1 = Customer(
        full_name="John Doe",
        preferred_name="John",
        zip_code="12345",
        birth_date=date(1990, 1, 15),
        email="john.doe@example.com",
        created_at=datetime(2023, 1, 1, 10, 0, 0)
    )
    customer2 = Customer(
        full_name="Jane Smith",
        preferred_name="Jane",
        zip_code="67890",
        birth_date=date(1985, 5, 20),
        email="jane.smith@example.com",
        created_at=datetime(2023, 1, 2, 11, 0, 0)
    )
    db.session.add_all([customer1, customer2])
    db.session.commit()

    yield db # provide the fixture value

    # Teardown is handled by test_client's db.drop_all()
    # If specific cleanup for this fixture is needed, it would go here.
    # For example, if we weren't dropping all tables:
    # Customer.query.delete()
    # db.session.commit()

@pytest.fixture(scope='function')
def new_customer_payload():
    return {
        "full_name": "Alice Wonderland",
        "preferred_name": "Alice",
        "zip_code": "90210",
        "birth_date": "2000-07-04", # Assuming YYYY-MM-DD for form/API
        "email": "alice.wonder@example.com"
    }
