from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    profile_created_at = db.Column(db.DateTime, default=datetime.utcnow() + timedelta(hours=5, minutes=30))
    loyalty_points = db.Column(db.Integer, default=0)
    role = db.Column(db.String(10), default='user') 
    reservations = db.relationship('Reservation', backref='user', lazy=True)
    def chckpwd(self, password):
        from .encdec import decpwd
        return decpwd(self.password_hash) == password
 
    def setpwd(self, password):
        from .encdec import encpwd
        self.password_hash = encpwd(password)

class ParkingLot(db.Model):
    __tablename__ = 'parking_lots'

    id = db.Column(db.Integer, primary_key=True)
    prime_location_name = db.Column(db.String(100), nullable=False)
    price_per_hour = db.Column(db.Float, nullable=False)
    address = db.Column(db.String(255), nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)
    total_number_of_spots = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow() + timedelta(hours=5, minutes=30))
    updated_at = db.Column(db.DateTime, default= datetime.utcnow() + timedelta(hours=5, minutes=30), onupdate=datetime.utcnow() + timedelta(hours=5, minutes=30))

    spots = db.relationship('ParkingSpot', backref='lot', lazy=True)


class ParkingSpot(db.Model):
    __tablename__ = 'parking_spots'

    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lots.id'), nullable=False)
    spot_number = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(1), default='A')  
    vehicle_type_supported = db.Column(db.String(10), default='non-EV')  
    is_under_maintenance = db.Column(db.Boolean, default=False)  
    maintenance_reason = db.Column(db.Text)  
    maintenance_started_at = db.Column(db.DateTime) 

    reservations = db.relationship('Reservation', backref='spot', lazy=True)
    maintenance_requests = db.relationship('MaintenanceRequest', backref='spot', lazy=True)


class Reservation(db.Model):
    __tablename__ = 'reservations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user_name = db.Column(db.String(100), nullable=False)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spots.id'), nullable=False)
    prime_location_name = db.Column(db.String(100), nullable=False)
    vehicle_number = db.Column(db.String(20), nullable=False)
    booking_timestamp = db.Column(db.DateTime, default= datetime.utcnow() + timedelta(hours=5, minutes=30)) 
    occupancy_timestamp = db.Column(db.DateTime)
    leaving_timestamp = db.Column(db.DateTime)  
    parking_cost = db.Column(db.Float)
    booking_status = db.Column(db.String(20), default='booked')
    cancellation_reason = db.Column(db.String(100))
    parking_timestamp = db.Column(db.DateTime)
    loyalty_points_redeemed = db.Column(db.Integer, default=0)  # Track redeemed points for discount calculation


class MaintenanceRequest(db.Model):
    __tablename__ = 'maintenance_requests'

    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spots.id'), nullable=False)
    prime_location_name = db.Column(db.String(100), nullable=False)
    issue_description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='Open')  
    reported_by = db.Column(db.String(100), nullable=False)  
    reported_at = db.Column(db.DateTime, default=datetime.utcnow() + timedelta(hours=5, minutes=30))


class UserFeedback(db.Model):
    __tablename__ = 'user_feedback'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user_name = db.Column(db.String(100), nullable=False)
    user_email = db.Column(db.String(120), nullable=False)
    user_phone = db.Column(db.String(15), nullable=False)
    parking_lot_id = db.Column(db.Integer, db.ForeignKey('parking_lots.id'))
    parking_lot_name = db.Column(db.String(100))
    spot_number = db.Column(db.String(20))  
    issue_category = db.Column(db.String(50), nullable=False)  
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='Open')  
    admin_response = db.Column(db.Text)  
    submitted_at = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(hours=5, minutes=30))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(hours=5, minutes=30), onupdate=lambda: datetime.utcnow() + timedelta(hours=5, minutes=30))

    user = db.relationship('User', backref='feedback', lazy=True)
    parking_lot = db.relationship('ParkingLot', backref='feedback', lazy=True)