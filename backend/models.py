from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#Admin model
class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)  

# Customer Model
class Customer(db.Model):
    __tablename__ = 'customer'
    id = db.Column(db.String, primary_key=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    fullname = db.Column(db.String, nullable=False)
    phone = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)
    pincode = db.Column(db.String, nullable=False)
    is_blocked = db.Column(db.Boolean, nullable=False, default=False)
    # Relationships
    service_requests = db.relationship('ServiceRequest', backref='customer', cascade='all, delete')

# a = approved, r = rejected

# Professional Model
class Professional(db.Model):
    __tablename__ = 'professional'
    id = db.Column(db.String, primary_key=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    fullname = db.Column(db.String, nullable=False)
    service_name = db.Column(db.String, nullable=False) 
    specification = db.Column(db.String, nullable=False)
    phone = db.Column(db.String, nullable=False)
    experience = db.Column(db.String, nullable=False)
    documents = db.Column(db.String, nullable=True)  
    address = db.Column(db.String, nullable=False)
    pincode = db.Column(db.String, nullable=False)
    avg_rating = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String, nullable=False, default='Pending')
    is_approved = db.Column(db.Boolean, nullable=False, default=False)
    is_blocked = db.Column(db.Boolean, nullable=False, default=False)
    
    # Relationships
    service_requests = db.relationship('ServiceRequest', backref='professional', cascade='all, delete-orphan')

        

    def __repr__(self):
        return f'<Professional {self.fullname}, Approved: {self.is_approved}>'

# Service Model
class Service(db.Model):
    __tablename__ = 'service'
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    time_required = db.Column(db.String, nullable=False)  
    service_requests = db.relationship('ServiceRequest', backref='service', cascade='all, delete')


# req = requested, as = assigned, cl = closed

# Service Request Model
class ServiceRequest(db.Model):
    __tablename__ = 'service_request'
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.String, db.ForeignKey('service.id'), nullable=False)
    customer_id = db.Column(db.String, db.ForeignKey('customer.id'), nullable=False)
    professional_id = db.Column(db.String, db.ForeignKey('professional.id'), nullable=False)
    date_of_request = db.Column(db.String, nullable=False)
    date_of_completion = db.Column(db.String, nullable=True) 
    status = db.Column(db.String, nullable=False)
    rating = db.Column(db.Integer, nullable=True)
    remarks = db.Column(db.String, nullable=True)
