from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import logging

# Load configuration
app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')
CORS(app)  # Enable CORS

# Configure logging
logging.basicConfig(level=logging.INFO)

db = SQLAlchemy(app)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customerId = db.Column(db.Integer, unique=True, nullable=False)
    companyName = db.Column(db.String(120), nullable=False)
    legalBusinessName = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    zip = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    businessType = db.Column(db.String(100), nullable=False)

    def __init__(self, customerId, companyName, legalBusinessName, email, phone, address, city, state, zip, country, businessType):
        self.customerId = customerId
        self.companyName = companyName
        self.legalBusinessName = legalBusinessName
        self.email = email
        self.phone = phone
        self.address = address
        self.city = city
        self.state = state
        self.zip = zip
        self.country = country
        self.businessType = businessType

# Initialize the database tables
@app.before_request
def create_tables():
    if not hasattr(create_tables, 'initialized'):
        db.create_all()
        create_tables.initialized = True

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

@app.route('/api/customers', methods=['GET'])
def get_all_customers():
    customers = Customer.query.all()
    return jsonify([{'id': customer.customerId, 'name': customer.companyName} for customer in customers])

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

@app.route('/')
def home():
    return jsonify({'message': 'Hello, World!'})

if __name__ == '__main__':
    app.run(debug=True)
