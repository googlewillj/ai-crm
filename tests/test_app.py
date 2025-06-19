import pytest
from app.models import Customer
from datetime import date

def test_index_serves_customers_page(test_client):
    """Test that the index route serves the customers page directly."""
    response = test_client.get('/')
    assert response.status_code == 200
    assert b"Customer List" in response.data
    # We can also check for content specific to an empty customer list,
    # or use init_database fixture if we expect data.
    # For this test, just checking "Customer List" is probably fine
    # as a basic check that the correct template is rendered.

def test_customers_page_empty(test_client):
    """Test the customers page when no customers are in the database."""
    response = test_client.get('/customers')
    assert response.status_code == 200
    assert b"Customer List" in response.data
    assert b"No customers found." in response.data

def test_customers_page_with_data(test_client, init_database):
    """Test the customers page with data."""
    response = test_client.get('/customers')
    assert response.status_code == 200
    assert b"Customer List" in response.data
    assert b"John Doe" in response.data
    assert b"jane.smith@example.com" in response.data
    assert b"No customers found." not in response.data

from app import db # Required for db.session and db.select

def test_customer_detail_page(test_client, init_database):
    """Test the customer detail page."""
    # Get the first customer added by init_database
    customer = db.session.scalars(db.select(Customer)).first()
    assert customer is not None

    response = test_client.get(f'/customer/{customer.id}')
    assert response.status_code == 200
    assert bytes(customer.full_name, 'utf-8') in response.data
    assert bytes(customer.email, 'utf-8') in response.data
    assert bytes(customer.zip_code, 'utf-8') in response.data
    assert bytes(customer.birth_date.strftime('%Y-%m-%d'), 'utf-8') in response.data

def test_customer_detail_not_found(test_client):
    """Test the customer detail page for a non-existent customer."""
    response = test_client.get('/customer/999')
    assert response.status_code == 404

def test_api_customer_detail(test_client, init_database):
    """Test the API endpoint for a single customer."""
    customer = db.session.scalars(db.select(Customer)).first()
    assert customer is not None

    response = test_client.get(f'/api/customer/{customer.id}')
    assert response.status_code == 200
    json_data = response.get_json()

    assert json_data['id'] == customer.id
    assert json_data['full_name'] == customer.full_name
    assert json_data['email'] == customer.email
    assert json_data['zip_code'] == customer.zip_code
    assert json_data['birth_date'] == customer.birth_date.strftime('%Y-%m-%d')
    assert 'created_at' in json_data # Check presence and basic format
    assert json_data['created_at'].endswith('Z')


def test_api_customer_detail_not_found(test_client):
    """Test the API endpoint for a non-existent customer."""
    response = test_client.get('/api/customer/9999')
    assert response.status_code == 404
    json_data = response.get_json()
    assert json_data['error'] == 'Customer not found'

# Example test for creating a customer (if you add such functionality)
# def test_create_customer(test_client, new_customer_payload):
# """Test creating a new customer (assuming a POST endpoint at /customers/new)."""
# response = test_client.post('/customers/new', data=new_customer_payload, follow_redirects=True)
# assert response.status_code == 200
# assert b"Alice Wonderland" in response.data # Check if new customer is displayed
#
#     newly_added_customer = Customer.query.filter_by(email="alice.wonder@example.com").first()
# assert newly_added_customer is not None
# assert newly_added_customer.full_name == "Alice Wonderland"
# assert newly_added_customer.birth_date == date(2000, 7, 4)


# from flask import request # No longer needed for the index test
