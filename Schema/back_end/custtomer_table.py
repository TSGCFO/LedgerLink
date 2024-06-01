from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/your_database'
db = SQLAlchemy(app)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, nullable=False, default=db.func.nextval('customers_customer_id_seq'))
    company_name = db.Column(db.String(100), nullable=False)
    legal_business_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    zip = db.Column(db.String(20))
    country = db.Column(db.String(50))
    business_type = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

@app.route('/api/customers', methods=['POST'])
def add_customer():
    data = request.get_json()
    new_customer = Customer(
        company_name=data['company_name'],
        legal_business_name=data['legal_business_name'],
        email=data.get('email'),
        phone=data.get('phone'),
        address=data.get('address'),
        city=data.get('city'),
        state=data.get('state'),
        zip=data.get('zip'),
        country=data.get('country'),
        business_type=data.get('business_type')
    )
    db.session.add(new_customer)
    db.session.commit()
    return jsonify({
        'id': new_customer.id,
        'customer_id': new_customer.customer_id,
        'company_name': new_customer.company_name,
        'legal_business_name': new_customer.legal_business_name,
        'email': new_customer.email,
        'phone': new_customer.phone,
        'address': new_customer.address,
        'city': new_customer.city,
        'state': new_customer.state,
        'zip': new_customer.zip,
        'country': new_customer.country,
        'business_type': new_customer.business_type,
        'created_at': new_customer.created_at,
        'updated_at': new_customer.updated_at
    })

if __name__ == '__main__':
    app.run(debug=True)
