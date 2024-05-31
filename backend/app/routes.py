from flask import request, jsonify
from app import app, db
import sys
sys.path.append('/path/to/app')  # Replace '/path/to/app' with the actual path to the 'app' package

from BillingAppV2.models import Customer, CustomerPricing

def init_routes(app):
    @app.route('/customers', methods=['POST'])
    def add_customer():
        data = request.get_json()
        app.logger.info(f'Received customer data: {data}')
        if not data:
            return jsonify({'error': 'Invalid data'}), 400
        try:
            new_customer = Customer(
                customerId=data['customerId'],
                companyName=data['companyName'],
                legalBusinessName=data['legalBusinessName'],
                email=data['email'],
                phone=data['phone'],
                address=data['address'],
                city=data['city'],
                state=data['state'],
                zip=data['zip'],
                country=data['country'],
                businessType=data['businessType']
            )
            db.session.add(new_customer)
            db.session.commit()
            return jsonify({'message': 'Customer added successfully'}), 201
        except Exception as e:
            app.logger.error(f'Error adding customer: {e}')
            return jsonify({'error': str(e)}), 500

    @app.route('/customers', methods=['GET'])
    def get_customers():
        customers = Customer.query.all()
        return jsonify([{
            'customerId': customer.customerId,
            'companyName': customer.companyName,
            'legalBusinessName': customer.legalBusinessName,
            'email': customer.email,
            'phone': customer.phone,
            'address': customer.address,
            'city': customer.city,
            'state': customer.state,
            'zip': customer.zip,
            'country': customer.country,
            'businessType': customer.businessType
        } for customer in customers])

    @app.route('/api/pricing', methods=['POST'])
    def add_pricing():
        data = request.get_json()
        app.logger.info(f'Received pricing data: {data}')
        if not data or 'customerId' not in data or 'pricingDetails' not in data:
            return jsonify({'error': 'Invalid data'}), 400
        try:
            new_pricing = CustomerPricing(
                customerId=data['customerId'],
                pricingDetails=data['pricingDetails']
            )
            db.session.add(new_pricing)
            db.session.commit()
            return jsonify({'message': 'Pricing added successfully'}), 201
        except Exception as e:
            app.logger.error(f'Error adding pricing: {e}')
            return jsonify({'error': str(e)}), 500

    @app.route('/api/pricing-options', methods=['GET'])
    def get_pricing_options():
        customer_id = request.args.get('customerId')
        # Implement your logic to fetch pricing options based on the customer ID.
        # This is a placeholder; replace with actual logic.
        pricing_options = [
            {"key": "option1", "label": "Option 1"},
            {"key": "option2", "label": "Option 2"}
        ]
        return jsonify(pricing_options)
