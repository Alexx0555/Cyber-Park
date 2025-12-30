from flask import Flask, send_from_directory, jsonify, request, abort
from flask_restful import Api
from flask_cors import CORS
from .models import db
from dotenv import load_dotenv
import os
import jwt
from datetime import datetime, timedelta
from functools import wraps
from .models import ParkingLot, ParkingSpot, Reservation, User
from flask_caching import Cache
from .cache_utils import cache_manager, CacheKeys, CacheTTL

load_dotenv()

from .models import db
from .init_admin import create_admin

def make_celery(app):
    from celery import Celery

    celery = Celery(
        app.import_name,
        backend=app.config.get('CELERY_RESULT_BACKEND'),
        broker=app.config.get('CELERY_BROKER_URL'))
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

def create_app():
    app = Flask(__name__)
    CORS(app)

    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(BASE_DIR, 'parking_app.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    try:
        import redis
        redis_client = redis.Redis(host='localhost', port=6379, db=0)
        redis_client.ping()
        app.config['CACHE_TYPE'] = 'RedisCache'
        app.config['CACHE_REDIS_HOST'] = 'localhost'
        app.config['CACHE_REDIS_PORT'] = 6379
        app.config['CACHE_REDIS_DB'] = 0
        app.config['CACHE_DEFAULT_TIMEOUT'] = 30
        print(" Using Redis cache")

    except:
        app.config['CACHE_TYPE'] = 'SimpleCache'
        app.config['CACHE_DEFAULT_TIMEOUT'] = 30
        print("⚠️  Redis not available, using SimpleCache")

    app.config['result_backend'] = os.getenv('CELERY_RESULT_BACKEND')
    cache_manager.init_app(app)
    db.init_app(app)
    api = Api(app)

    from backend.routes.api_resources import (
        LoginResource, RegisterResource, ProfileResource, RefreshTokenResource, LogoutResource,
        UserFeedbackResource, UserParkingLotsResource, UserParkingLotSpotsResource,
        UserActiveReservationsResource, UserBookSpotResource, UserOccupySpotResource,
        UserBookingHistoryResource,UserUpdateProfileResource,UserCancelBookingResource,
        UserReleaseSpotResource,UserChangePasswordResource,UserReservationsResource,
        AdminExportUsersResource, AdminSendMonthlyReportsResource,
        AdminParkingLotsResource, AdminParkingLotResource, AdminFeedbackResource,
        AdminUpdateFeedbackResource,AdminParkingRecordsResource,
        AdminToggleMaintenanceResource,AdminToggleSpotTypeResource,
        AdminCreateParkingLotResource,AdminEditParkingLotResource,
        AdminDeleteParkingLotResource,AdminUsersResource,AdminGetSpotsbylotsResource
    )


    #Authentication endpoints
    api.add_resource(LoginResource, '/api/login')
    api.add_resource(RegisterResource, '/api/register')
    api.add_resource(ProfileResource, '/api/profile')
    api.add_resource(RefreshTokenResource, '/api/refresh')
    api.add_resource(LogoutResource, '/api/logout')

    #User endpoints
    api.add_resource(UserFeedbackResource, '/api/user/feedback')
    api.add_resource(UserParkingLotsResource, '/api/user/parking-lots')
    api.add_resource(UserParkingLotSpotsResource, '/api/user/parking-lots/<int:lot_id>/spots')
    api.add_resource(UserActiveReservationsResource, '/api/user/active-reservations')
    api.add_resource(UserBookSpotResource, '/api/user/book-spot')
    api.add_resource(UserOccupySpotResource, '/api/user/occupy-spot')
    api.add_resource(UserBookingHistoryResource, '/api/user/booking-history')
    api.add_resource(UserUpdateProfileResource, '/api/user/update-profile')
    api.add_resource(UserCancelBookingResource, '/api/user/cancel-booking')
    api.add_resource(UserReleaseSpotResource, '/api/user/release-spot/<int:reservation_id>')
    api.add_resource(UserChangePasswordResource, '/api/user/change-password')
    api.add_resource(UserReservationsResource, '/api/user/reservations')

    #Admin endpoints
    api.add_resource(AdminExportUsersResource, '/api/admin/export-users')
    api.add_resource(AdminSendMonthlyReportsResource, '/api/admin/send-monthly-reports')
    api.add_resource(AdminUsersResource, '/api/admin/users')
    api.add_resource(AdminParkingLotsResource, '/api/admin/parking-lots')
    api.add_resource(AdminParkingLotResource, '/api/admin/parking-lots/<int:lot_id>')
    api.add_resource(AdminGetSpotsbylotsResource, '/api/admin/parking-lots/<int:lot_id>/spots')
    api.add_resource(AdminFeedbackResource, '/api/admin/feedback')
    api.add_resource(AdminUpdateFeedbackResource, '/api/admin/feedback/<int:feedback_id>')
    api.add_resource(AdminParkingRecordsResource, '/api/admin/parking-records')
    api.add_resource(AdminToggleMaintenanceResource, '/api/admin/parking-spots/<int:spot_id>/maintenance')
    api.add_resource(AdminToggleSpotTypeResource, '/api/admin/parking-spots/<int:spot_id>/vehicle-type')
    api.add_resource(AdminCreateParkingLotResource, '/api/admin/parking-lots')
    api.add_resource(AdminEditParkingLotResource, '/api/admin/parking-lots/<int:lot_id>')
    api.add_resource(AdminDeleteParkingLotResource, '/api/admin/parking-lots/<int:lot_id>')

    return app

app = create_app()

celery = make_celery(app)

JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
blacklisted_tokens = set()

def create_access_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow()  + JWT_ACCESS_TOKEN_EXPIRES,
        'iat': datetime.utcnow() ,
        'type': 'access'
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')

def create_refresh_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow()  + JWT_REFRESH_TOKEN_EXPIRES,
        'iat': datetime.utcnow() ,
        'type': 'refresh'
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')

def decode_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return {'error': 'Token has expired'}
    except jwt.InvalidTokenError:
        return {'error': 'Invalid token'}

def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')

        if auth_header:
            try:
                token = auth_header.split(' ')[1] 
            except IndexError:
                return jsonify({'success': False, 'message': 'Invalid token format'}), 401

        if not token:
            return jsonify({'success': False, 'message': 'Authorization token is required'}), 401

        if token in blacklisted_tokens:
            return jsonify({'success': False, 'message': 'Token has been revoked'}), 401

        payload = decode_token(token)
        if 'error' in payload:
            return jsonify({'success': False, 'message': payload['error']}), 401

        if payload.get('type') != 'access':
            return jsonify({'success': False, 'message': 'Invalid token type'}), 401

        request.current_user_id = payload['user_id']
        return f(*args, **kwargs)
    
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')

        if auth_header:
            try:
                token = auth_header.split(' ')[1]  
            except IndexError:
                return jsonify({'success': False, 'message': 'Invalid token format'}), 401

        if not token:
            return jsonify({'success': False, 'message': 'Authorization token is required'}), 401

        if token in blacklisted_tokens:
            return jsonify({'success': False, 'message': 'Token has been revoked'}), 401

        payload = decode_token(token)
        if 'error' in payload:
            return jsonify({'success': False, 'message': payload['error']}), 401

        if payload.get('type') != 'access':
            return jsonify({'success': False, 'message': 'Invalid token type'}), 401

        user = db.session.get(User, payload['user_id'])
        if not user or user.role != 'admin':
            return jsonify({'success': False, 'message': 'Admin access required'}), 403

        request.current_user_id = payload['user_id']
        return f(*args, **kwargs)
    
    return decorated_function

with app.app_context():
    db.create_all()
    create_admin()

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_vue_app(path):
        project_root = os.path.dirname(os.path.abspath(__file__))
        frontend_dist = os.path.join(project_root, '..', 'frontend', 'dist')

        if path != "" and os.path.exists(os.path.join(frontend_dist, path)):
            return send_from_directory(frontend_dist, path)
        else:
            return send_from_directory(frontend_dist, 'index.html')

@app.route('/assets/<path:filename>')
def serve_vue_assets(filename):
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        frontend_assets = os.path.join(project_root, 'frontend', 'dist', 'assets')
        return send_from_directory(frontend_assets, filename)

    except Exception as e:
        print(f"ERROR in serve_vue_assets: {e}")
        return f"Error serving asset: {e}", 500

@app.route('/api/admin/cache/stats', methods=['GET'])
@admin_required
def get_cache_stats():
    stats = cache_manager.get_stats()
    return jsonify({'success': True, 'cache_stats': stats})

@app.route('/api/admin/cache/warm', methods=['POST'])
@admin_required
def warm_cache():
    try:
        user_view_parking_lots()
        get_all_parking_lots()
        get_all_reservations()
        return jsonify({'success': True, 'message': 'Cache warmed successfully'})
   
    except Exception as e:
        return jsonify({'success': False, 'message': f'Cache warming failed: {str(e)}'}), 500

@app.route('/api/admin/cache/clear', methods=['POST'])
@admin_required
def clear_cache():
    try:
        cache_manager.delete_pattern("user:*")
        cache_manager.delete_pattern("parking:*")
        cache_manager.delete_pattern("spot:*")
        cache_manager.delete_pattern("admin:*")
        return jsonify({'success': True, 'message': 'Cache cleared successfully'})

    except Exception as e:
        return jsonify({'success': False, 'message': f'Cache clearing failed: {str(e)}'}), 500

@admin_required
def get_all_parking_lots():
    cache_key = "admin:parking:lots:all"
    cached_lots = cache_manager.get(cache_key)
    if cached_lots:
        return jsonify({'success': True, 'parking_lots': cached_lots})

    lots = ParkingLot.query.all()
    data = []
    for lot in lots:
        total = len(lot.spots)
        available = sum(1 for s in lot.spots if s.status == 'A' and not s.is_under_maintenance)
        occupied = sum(1 for s in lot.spots if s.status == 'O')
        maintenance = sum(1 for s in lot.spots if s.is_under_maintenance)
        data.append({
            'id': lot.id,
            'name': lot.prime_location_name,
            'address': lot.address,
            'price_per_hour': lot.price_per_hour,
            'pin_code': lot.pin_code,
            'capacity': total,
            'available': available,
            'occupied': occupied,
            'maintenance': maintenance,
        })

    cache_manager.set(cache_key, data, CacheTTL.PARKING_AVAILABILITY)
    return jsonify({'success': True, 'parking_lots': data})

def startup_cleanup():
    try:
        from .tasks import auto_cancel_expired_bookings
        auto_cancel_expired_bookings.delay()

    except ImportError:
        from .tasks import auto_cancel_expired_bookings
        auto_cancel_expired_bookings()

    return jsonify({'message': 'Startup cleanup completed'})

@auth_required
def get_current_bookings():
    current_user_id = request.current_user_id
    try:
        current_time = datetime.utcnow() + timedelta(hours=5, minutes=30)
        bookings = Reservation.query.filter(
            Reservation.user_id == current_user_id,
            Reservation.booking_status == 'booked',
            Reservation.booking_timestamp + timedelta(hours=12) > current_time  
        ).order_by(Reservation.booking_timestamp.desc()).all()

        booking_data = []
        for booking in bookings:
            spot = db.session.get(ParkingSpot, booking.spot_id)
            spot_number = spot.spot_number if spot else 'Unknown'
            expires_at = booking.booking_timestamp + timedelta(hours=12)
            booking_data.append({
                'id': booking.id,
                'location_name': booking.prime_location_name,
                'spot_number': spot_number,
                'vehicle_number': booking.vehicle_number,
                'booking_timestamp': booking.booking_timestamp.isoformat(),
                'expires_at': expires_at.isoformat()
            })

        return jsonify({
            'success': True,
            'bookings': booking_data
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error loading current bookings: {str(e)}'
        }), 500

@admin_required
def get_all_reservations():
    cache_key = CacheKeys.admin_history()
    cached_history = cache_manager.get(cache_key)
    if cached_history:
        return jsonify({'success': True, 'history': cached_history})

    reservations = Reservation.query.order_by(Reservation.parking_timestamp.desc()).all()
    history = []

    for r in reservations:
        duration_hours = None
        end_time_str = None
        cost = 0
        breakdown = {}
        if r.leaving_timestamp:
            duration = r.leaving_timestamp - r.parking_timestamp
            duration_hours = round(duration.total_seconds() / 3600, 2)
            end_time_str = r.leaving_timestamp.strftime("%Y-%m-%d %H:%M:%S")
            cost = r.parking_cost or 0
            lot = ParkingLot.query.filter_by(prime_location_name=r.prime_location_name).first()
            if lot and cost == 0:
                base_rate = lot.price_per_hour
                cost = round(duration_hours * base_rate, 2)
                breakdown = {
                    'base_rate': base_rate,
                    'duration_hours': duration_hours,
                    'total_cost': cost
                }
        user = db.session.get( User, r.user_id)
        username = user.username if user else 'Unknown User'
        spot_number = 'N/A'
        if r.spot_id:
            spot = db.session.get( ParkingSpot, r.spot_id)
            if spot:
                spot_number = spot.spot_number

        booking_time_str = None
        if r.booking_timestamp:
            booking_time_str = r.booking_timestamp.strftime("%Y-%m-%d %H:%M:%S")

        history.append({
            'id': r.id,
            'user_id': r.user_id,
            'user_name': username,
            'location': r.prime_location_name,
            'spot_number': spot_number,
            'vehicle_number': r.vehicle_number,
            'booking_timestamp': booking_time_str,
            'booking_status': r.booking_status,
            'start_time': r.parking_timestamp.strftime("%Y-%m-%d %H:%M:%S") if r.parking_timestamp else None,
            'end_time': end_time_str,
            'cost': cost,
            'cost_breakdown': breakdown
        })

    cache_manager.set(cache_key, history, CacheTTL.ADMIN_HISTORY)
    return jsonify({'success': True, 'history': history})

def user_view_parking_lots():
    cache_key = CacheKeys.parking_lots_all()
    cached_lots = cache_manager.get(cache_key)
    if cached_lots:
        return jsonify({'lots': cached_lots})

    lots = ParkingLot.query.all()
    data = []
    for lot in lots:
        available_spots = sum(1 for s in lot.spots if s.status == 'A' and not s.is_under_maintenance)
        data.append({
            'id': lot.id,
            'prime_location_name': lot.prime_location_name,
            'address': lot.address,
            'pin_code': lot.pin_code,
            'price_per_hour': lot.price_per_hour,
            'available_spots': available_spots
        })

    cache_manager.set(cache_key, data, CacheTTL.PARKING_LOTS_ALL)
    return jsonify({'lots': data})


@app.route('/api/user/export-my-history', methods=['POST'])
@auth_required
def export_user_history():
    try:
        current_user_id = request.current_user_id
        try:
            from .tasks import export_user_history_to_email
            task = export_user_history_to_email.delay(current_user_id)
            return jsonify({
                'success': True,
                'message': '✅ Your parking history export has been queued! You will receive an email with the CSV file shortly.',
                'task_id': task.id
            }), 202

        except ImportError:
            return jsonify({
                'success': False,
                'message': 'Export service is currently unavailable. Please try again later.'
            }), 503

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error queuing export task: {str(e)}'}), 500