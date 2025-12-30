from .encdec import encpwd
from .models import db, User

def create_admin():
    existing_admin = User.query.filter_by(role='admin').first()
    if not existing_admin:
        admin = User(
            username='Super_admin',phone_number='7842591367',
            email='admin@gmail.com',
            password_hash=encpwd('admin123'),role='admin')
        db.session.add(admin)
        db.session.commit()
        print('Admin created.')
    else:
        print('Admin already exists.') 