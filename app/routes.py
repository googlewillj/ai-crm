from flask import Blueprint, render_template
from app.models import Customer

bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/customers')
def customers():
    all_customers = Customer.query.all()
    return render_template('customers.html', title='Customer List', customers=all_customers)

from app import db

@bp.route('/customer/<int:customer_id>')
def customer_detail(customer_id):
    # customer = Customer.query.get_or_404(customer_id) # Old way
    customer = db.session.get(Customer, customer_id)
    if customer is None:
        from werkzeug.exceptions import NotFound
        raise NotFound()
    return render_template('customer_detail.html', title=customer.full_name, customer=customer)

from flask import jsonify # Import jsonify at the module level

@bp.route('/api/customer/<int:customer_id>', methods=['GET'])
def api_customer_detail(customer_id):
    customer = db.session.get(Customer, customer_id)
    if customer is None:
        # from flask import jsonify # No longer needed here
        return jsonify({'error': 'Customer not found'}), 404
    return jsonify(customer.to_dict())
