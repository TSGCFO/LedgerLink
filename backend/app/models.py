from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Customer(db.Model):
    __tablename__ = 'customers'
    
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

class CustomerPricing(db.Model):
    __tablename__ = 'customer_pricing'
    
    id = db.Column(db.Integer, primary_key=True)
    customerId = db.Column(db.Integer, db.ForeignKey('customers.customerId'), nullable=False)
    pricingDetails = db.Column(db.JSON, nullable=False)

    def __init__(self, customerId, pricingDetails):
        self.customerId = customerId
        self.pricingDetails = pricingDetails
