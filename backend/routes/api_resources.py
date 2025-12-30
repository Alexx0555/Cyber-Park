from flask import request, jsonify
from flask_restful import Resource
from functools import wraps
import jwt
import os
from datetime import datetime, timedelta

from ..models import db, User, ParkingLot, ParkingSpot, Reservation, UserFeedback, MaintenanceRequest
from ..cache_utils import cache_manager, CacheKeys, CacheTTL, invalidate_parking_cache, invalidate_user_cache, invalidate_admin_cache

JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return {'success': False, 'message': 'Token is missing'}, 401

        try:
            if token.startswith('Bearer '):
                token = token[7:]

            data = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
            current_user_id = data['user_id']
            request.current_user_id = current_user_id

        except jwt.ExpiredSignatureError:
            return {'success': False, 'message': 'Token has expired'}, 401
        
        except jwt.InvalidTokenError:
            return {'success': False, 'message': 'Token is invalid'}, 401

        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return {'success': False, 'message': 'Token is missing'}, 401

        try:
            if token.startswith('Bearer '):
                token = token[7:]

            data = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
            current_user_id = data['user_id']
            user = db.session.get(User, current_user_id)
            if not user or user.role != 'admin':
                return {'success': False, 'message': 'Admin access required'}, 403

            request.current_user_id = current_user_id

        except jwt.ExpiredSignatureError:
            return {'success': False, 'message': 'Token has expired'}, 401

        except jwt.InvalidTokenError:
            return {'success': False, 'message': 'Token is invalid'}, 401

        return f(*args, **kwargs)
    return decorated_function

def create_access_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + JWT_ACCESS_TOKEN_EXPIRES,
        'iat': datetime.utcnow(),
        'type': 'access'
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')

def create_refresh_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + JWT_REFRESH_TOKEN_EXPIRES,
        'iat': datetime.utcnow(),
        'type': 'refresh'
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')

class LoginResource(Resource):
    def post(self):
        data = request.get_json()
        if not data or not data.get('uname') or not data.get('pwd'):
            return {'success': False, 'message': 'Username and password are required'}, 400
        
        uname = data['uname']
        pwd = data['pwd']
        user = User.query.filter_by(username=uname).first()
        if user and user.chckpwd(pwd):
            access_token = create_access_token(user.id)
            refresh_token = create_refresh_token(user.id)
            return {
                'success': True,
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user_role': user.role,
                'message': 'Login successful'
            }, 200

        else:
            return {'success': False, 'message': 'Invalid username or password'}, 401

class RefreshTokenResource(Resource):
    def post(self):
        data = request.get_json()
        if not data or not data.get('refresh_token'):
            return {'success': False, 'message': 'Refresh token is required'}, 400
        
        refresh_token = data['refresh_token']
        
        try:
            # Decode and validate the refresh token
            payload = jwt.decode(refresh_token, JWT_SECRET_KEY, algorithms=['HS256'])
            
            # Verify it's a refresh token type
            if payload.get('type') != 'refresh':
                return {'success': False, 'message': 'Invalid token type. Refresh token required'}, 401
            
            # Get user_id from the refresh token payload
            user_id = payload.get('user_id')
            if not user_id:
                return {'success': False, 'message': 'Invalid token payload'}, 401
            
            # Verify user still exists
            user = db.session.get(User, user_id)
            if not user:
                return {'success': False, 'message': 'User not found'}, 404
            
            # Generate new access token
            new_access_token = create_access_token(user_id)
            
            return {
                'success': True,
                'access_token': new_access_token,
                'message': 'Token refreshed successfully'
            }, 200
            
        except jwt.ExpiredSignatureError:
            return {'success': False, 'message': 'Refresh token has expired. Please login again'}, 401
        
        except jwt.InvalidTokenError:
            return {'success': False, 'message': 'Invalid refresh token'}, 401
        
        except Exception as e:
            return {'success': False, 'message': f'Token refresh failed: {str(e)}'}, 500

class LogoutResource(Resource):
    @auth_required
    def post(self):
        try:
            token = request.headers.get('Authorization')
            if token and token.startswith('Bearer '):
                token = token[7:]
                
                # Add token to blacklist (imported from app.py module level)
                from ..app import blacklisted_tokens
                blacklisted_tokens.add(token)
                
                return {
                    'success': True,
                    'message': 'Logged out successfully'
                }, 200
            
            return {'success': False, 'message': 'No token provided'}, 400
            
        except Exception as e:
            return {'success': False, 'message': f'Logout failed: {str(e)}'}, 500

class RegisterResource(Resource):
    def post(self):
        data = request.get_json()
        required_fields = ['uname', 'email', 'phone', 'pwd']
        field_errors = {}
        for field in required_fields:
            if not data.get(field):
                field_errors[field] = f'{field.capitalize()} is required'
        
        if field_errors:
            return {'success': False, 'field_errors': field_errors}, 400
        
        if User.query.filter_by(username=data['uname']).first():
            return {'success': False, 'field_errors': {'uname': 'Username already exists'}}, 400
        
        if User.query.filter_by(email=data['email']).first():
            return {'success': False, 'field_errors': {'email': 'Email already registered'}}, 400
        
        pwd = data['pwd']
        if len(pwd) < 6:
            return {'success': False, 'field_errors': {'pwd': 'Password must be at least 6 characters'}}, 400
        
        try:
            new_user = User(username=data['uname'],email=data['email'],phone_number=data['phone'],role='user')
            new_user.setpwd(pwd)
            db.session.add(new_user)
            db.session.commit()
            return {'success': True, 'message': 'Registration successful'}, 201
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Registration failed: {str(e)}'}, 500

class ProfileResource(Resource):
    @auth_required
    def get(self):
        current_user_id = request.current_user_id
        cache_key = CacheKeys.user_profile(current_user_id)
        cached_profile = cache_manager.get(cache_key)
        if cached_profile:
            return {'success': True, 'user': cached_profile}
        
        user = db.session.get(User, current_user_id)
        if not user:
            return {'success': False, 'message': 'User not found'}, 404
        
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'phone_number': user.phone_number,
            'role': user.role,
            'loyalty_points': user.loyalty_points,
            'created_at': user.profile_created_at.isoformat() if user.profile_created_at else None
        }
        
        cache_manager.set(cache_key, user_data, CacheTTL.USER_PROFILE)
        return {'success': True, 'user': user_data}, 200

class UserFeedbackResource(Resource):
    @auth_required
    def post(self):
        try:
            current_user_id = request.current_user_id
            data = request.get_json()

            if not data or not data.get('description'):
                return {'success': False, 'message': 'Feedback description is required'}, 400

            user = User.query.get(current_user_id)
            if not user:
                return {'success': False, 'message': 'User not found'}, 404

            feedback = UserFeedback(
                user_id=current_user_id,
                user_name=user.username,
                user_email=user.email,
                user_phone=user.phone_number or '',
                parking_lot_id=data.get('parking_lot_id'),
                parking_lot_name=data.get('parking_lot_name', ''),
                spot_number=data.get('spot_number', ''),
                issue_category=data.get('issue_category', 'Other'),
                description=data['description'],
                status='Open'
            )

            db.session.add(feedback)
            db.session.commit()

            invalidate_user_cache(current_user_id)
            return {'success': True, 'message': 'Feedback submitted successfully'}, 201

        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Error submitting feedback: {str(e)}'}, 500
    
    @auth_required
    def get(self):
        try:
            current_user_id = request.current_user_id
            cache_key = f"user:feedback:{current_user_id}"
            cached_feedback = cache_manager.get(cache_key)
            if cached_feedback:
                return {'success': True, 'feedback': cached_feedback}
            
            feedback_list = UserFeedback.query.filter_by(user_id=current_user_id).order_by(UserFeedback.submitted_at.desc()).all()
            feedback_data = []

            for feedback in feedback_list:
                feedback_data.append({
                    'id': feedback.id,
                    'user_name': feedback.user_name,
                    'user_email': feedback.user_email,
                    'parking_lot_name': feedback.parking_lot_name,
                    'spot_number': feedback.spot_number,
                    'issue_category': feedback.issue_category,
                    'description': feedback.description,
                    'status': feedback.status,
                    'admin_response': feedback.admin_response,
                    'submitted_at': feedback.submitted_at.isoformat() if feedback.submitted_at else None,
                    'updated_at': feedback.updated_at.isoformat() if feedback.updated_at else None
                })
            
            cache_manager.set(cache_key, feedback_data, 600) 
            
            return {'success': True, 'feedback': feedback_data}
            
        except Exception as e:
            return {'success': False, 'message': f'Error retrieving feedback: {str(e)}'}, 500

class UserParkingLotsResource(Resource):
    @auth_required
    def get(self):
        cache_key = "user:parking:lots:all"
        cached_lots = cache_manager.get(cache_key)
        if cached_lots:
            return {'success': True, 'parking_lots': cached_lots}

        lots = ParkingLot.query.all()
        data = []
        for lot in lots:
            available_spots = sum(1 for s in lot.spots if s.status == 'A' and not s.is_under_maintenance)

            data.append({
                'id': lot.id,
                'name': lot.prime_location_name,
                'capacity': lot.total_number_of_spots, 
                'available': available_spots, 
                'price_per_hour': lot.price_per_hour,
                'location': lot.address 
            })

        cache_manager.set(cache_key, data, CacheTTL.PARKING_LOTS_ALL)

        return {'success': True, 'parking_lots': data}

class UserParkingLotSpotsResource(Resource):
    @auth_required
    def get(self, lot_id):
        current_user_id = request.current_user_id
        cache_key = f"user:parking:spots:{lot_id}"
        cached_spots = cache_manager.get(cache_key)
        if cached_spots:
            return {'success': True, 'spots': cached_spots}

        lot = db.session.get(ParkingLot, lot_id)
        if not lot:
            return {'success': False, 'message': 'Parking lot not found'}, 404

        spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
        data = []

        for spot in spots:
            spot_data = {
                'id': spot.id,
                'spot_number': spot.spot_number,
                'status': spot.status,
                'vehicle_type': spot.vehicle_type_supported,
                'is_available': spot.status == 'A',
                'is_booked': spot.status == 'B',
                'is_occupied': spot.status == 'O',
                'is_maintenance': spot.status == 'M' or spot.is_under_maintenance
            }

            if spot.status == 'B':
                booking = Reservation.query.filter_by(
                    spot_id=spot.id,
                    booking_status='booked',
                    leaving_timestamp=None).first()

                if booking:
                    current_time = datetime.utcnow() + timedelta(hours=5, minutes=30)
                    booking_expiry = booking.booking_timestamp + timedelta(hours=12)

                    spot_data.update({
                        'booking_id': booking.id,
                        'booked_by_current_user': booking.user_id == current_user_id,
                        'booking_expires_at': booking_expiry.isoformat(),
                        'booking_expired': current_time > booking_expiry,
                        'vehicle_number': booking.vehicle_number if booking.user_id == current_user_id else None
                    })

            data.append(spot_data)

        cache_manager.set(cache_key, data, CacheTTL.PARKING_SPOTS)
        return {'success': True, 'spots': data}

class UserActiveReservationsResource(Resource):
    @auth_required
    def get(self):
        current_user_id = request.current_user_id
        cache_key = f"user:active_reservations:{current_user_id}"
        cached_reservations = cache_manager.get(cache_key)

        if cached_reservations:
            return {'success': True, 'active_reservations': cached_reservations}

        reservations = Reservation.query.filter_by(
            user_id=current_user_id,
            booking_status='occupied',
            leaving_timestamp=None
        ).order_by(Reservation.parking_timestamp.desc()).all()

        data = []
        for reservation in reservations:
            spot = db.session.get(ParkingSpot, reservation.spot_id)
            data.append({
                'id': reservation.id,
                'prime_location_name': reservation.prime_location_name,
                'spot_number': spot.spot_number if spot else 'N/A',
                'vehicle_number': reservation.vehicle_number,
                'parking_timestamp': reservation.parking_timestamp.isoformat() if reservation.parking_timestamp else None,
                'occupancy_timestamp': reservation.occupancy_timestamp.isoformat() if reservation.occupancy_timestamp else None,
                'booking_status': reservation.booking_status
            })

        cache_manager.set(cache_key, data, CacheTTL.USER_RESERVATIONS)
        return {'success': True, 'active_reservations': data}

class UserBookSpotResource(Resource):
    @auth_required
    def post(self):
        current_user_id = request.current_user_id
        data = request.json
        if not data or not data.get('spot_id') or not data.get('vehicle_number'):
            return {'success': False, 'message': 'Spot ID and vehicle number are required'}, 400

        spot_id = data['spot_id']
        vehicle_number = data['vehicle_number']
        points_to_redeem = data.get('points_to_redeem', 0)
        spot = db.session.get(ParkingSpot, spot_id)
        if not spot:
            return {'success': False, 'message': 'Parking spot not found'}, 404

        if spot.status != 'A':
            return {'success': False, 'message': 'Parking spot is not available'}, 400

        user = db.session.get(User, current_user_id)
        if not user:
            return {'success': False, 'message': 'User not found'}, 404

        if points_to_redeem > 0 and (user.loyalty_points or 0) < points_to_redeem:
            return {'success': False, 'message': 'Insufficient loyalty points'}, 400

        existing_occupied_reservation = Reservation.query.filter_by(
            vehicle_number=vehicle_number,
            leaving_timestamp=None 
        ).join(ParkingSpot).filter(
            ParkingSpot.status == 'O'  
        ).first()

        if existing_occupied_reservation:
            occupied_spot = db.session.get(ParkingSpot, existing_occupied_reservation.spot_id)
            spot_number = occupied_spot.spot_number if occupied_spot else "Unknown"

            return {
                'success': False,
                'conflict_data': {
                    'prime_location_name': existing_occupied_reservation.prime_location_name,
                    'spot_number': spot_number,
                    'vehicle_number': vehicle_number,
                    'parking_timestamp': existing_occupied_reservation.parking_timestamp.isoformat()
                },
                'message': f'Vehicle {vehicle_number} is already occupied at {existing_occupied_reservation.prime_location_name} - Spot {spot_number}. Please release this spot before booking elsewhere.',
                'error_type': 'vehicle_occupied_elsewhere'
            }, 400

        try:
            reservation = Reservation(
                user_id=current_user_id,
                user_name=user.username,
                spot_id=spot_id,
                prime_location_name=spot.lot.prime_location_name,
                vehicle_number=vehicle_number,
                booking_timestamp=datetime.utcnow() + timedelta(hours=5, minutes=30),
                booking_status='booked',
                parking_timestamp=datetime.utcnow() + timedelta(hours=5, minutes=30),
                loyalty_points_redeemed=points_to_redeem  # Store redeemed points for later discount calculation
            )

            spot.status = 'B'
            if points_to_redeem > 0:
                user.loyalty_points = (user.loyalty_points or 0) - points_to_redeem

            db.session.add(reservation)
            db.session.commit()

            invalidate_parking_cache(spot.lot_id)
            invalidate_parking_cache()
            invalidate_user_cache(current_user_id)
            invalidate_admin_cache()
            discount_amount = points_to_redeem * 0.1  

            return {
                'success': True,
                'message': 'Parking spot booked successfully! You have 12 hours to occupy the spot.',
                'booking_id': reservation.id,
                'booking_expires_at': (reservation.booking_timestamp + timedelta(hours=12)).isoformat(),
                'points_redeemed': points_to_redeem,
                'discount_applied': discount_amount,
                'remaining_points': user.loyalty_points
            }, 201

        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Error booking spot: {str(e)}'}, 500

class UserCancelBookingResource(Resource):
    @auth_required
    def post(self):
        try:
            data = request.get_json()
            booking_id = data.get('booking_id')
            if not booking_id:
                return {'success': False, 'message': 'Booking ID is required'}, 400
            
            booking = Reservation.query.filter_by(
                id=booking_id,
                user_id=request.current_user_id,
                booking_status='booked'
            ).first()
            if not booking:
                return {'success': False, 'message': 'Booking not found or already processed'}, 404
            
            spot = db.session.get(ParkingSpot, booking.spot_id)
            if spot:
                spot.status = 'A'
                invalidate_parking_cache(spot.lot_id)
            
            db.session.delete(booking)
            db.session.commit()
            invalidate_user_cache(request.current_user_id)
            
            return {
                'success': True,
                'message': 'Booking cancelled successfully'
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Error cancelling booking: {str(e)}'}, 500


class UserOccupySpotResource(Resource):
    @auth_required
    def post(self):
        current_user_id = request.current_user_id
        data = request.json

        booking_id = data.get('booking_id')
        if not booking_id:
            return {'success': False, 'message': 'Booking ID is required'}, 400

        reservation = Reservation.query.filter_by(
            id=booking_id,
            user_id=current_user_id,
            booking_status='booked').first()

        if not reservation:
            return {'success': False, 'message': 'Booking not found or already processed'}, 404

        current_time = datetime.utcnow() + timedelta(hours=5, minutes=30)
        booking_expiry = reservation.booking_timestamp + timedelta(hours=12)

        if current_time > booking_expiry:
            spot = db.session.get(ParkingSpot, reservation.spot_id)
            if spot:
                spot.status = 'A'

            db.session.delete(reservation)
            db.session.commit()
            return {'success': False, 'message': 'Booking has expired (12 hours). The spot has been released.'}, 400

        try:
            reservation.booking_status = 'occupied'
            reservation.occupancy_timestamp = current_time
            reservation.parking_timestamp = current_time 

            spot = db.session.get(ParkingSpot, reservation.spot_id)
            if spot:
                spot.status = 'O'

            db.session.commit()

            invalidate_parking_cache(spot.lot_id if spot else None)
            invalidate_parking_cache()
            invalidate_user_cache(current_user_id)
            invalidate_admin_cache()

            return {
                'success': True,
                'message': 'Parking spot occupied successfully! Billing has started.',
                'occupied_at': reservation.occupancy_timestamp.isoformat(),
                'billing_started_at': reservation.parking_timestamp.isoformat()
            }, 200

        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Error occupying spot: {str(e)}'}, 500


class UserBookingHistoryResource(Resource):
    @auth_required
    def get(self):
        try:
            current_user_id = request.current_user_id
            cache_key = CacheKeys.user_history(current_user_id)
            cached_history = cache_manager.get(cache_key)
            if cached_history:
                return {'success': True, 'history': cached_history}
            
            reservations = Reservation.query.filter_by(user_id=current_user_id).order_by(
                Reservation.booking_timestamp.desc(),
                Reservation.parking_timestamp.desc()).all()
            
            history = []
            for reservation in reservations:
                spot_number = reservation.spot.spot_number if reservation.spot else 'N/A'
                booking_time_str = reservation.booking_timestamp.strftime("%Y-%m-%d %H:%M:%S") if reservation.booking_timestamp else 'N/A'
                end_time_str = 'N/A'
                cost = 0
                breakdown = 'No cost calculated'
                
                if reservation.leaving_timestamp:
                    end_time_str = reservation.leaving_timestamp.strftime("%Y-%m-%d %H:%M:%S")
                    cost = reservation.parking_cost or 0
                    if reservation.parking_timestamp:
                        duration = reservation.leaving_timestamp - reservation.parking_timestamp
                        hours = duration.total_seconds() / 3600
                        breakdown = f"{hours:.1f} hours × rate"
                
                booking_status = self._get_user_status_description(reservation)
                history.append({
                    'id': reservation.id,
                    'location': reservation.prime_location_name,
                    'spot_number': spot_number,
                    'vehicle_number': reservation.vehicle_number,
                    'booking_timestamp': booking_time_str,
                    'booking_status': booking_status,
                    'start_time': reservation.parking_timestamp.strftime("%Y-%m-%d %H:%M:%S") if reservation.parking_timestamp else None,
                    'end_time': end_time_str,
                    'cost': cost,
                    'cost_breakdown': breakdown
                })
            cache_manager.set(cache_key, history, CacheTTL.USER_HISTORY)
            return {'success': True, 'history': history}
            
        except Exception as e:
            return {'success': False, 'message': f'Error fetching booking history: {str(e)}'}, 500

    def _get_user_status_description(self, reservation):
        status = reservation.booking_status or 'occupied' 
        
        if status == 'booked':
            if reservation.booking_timestamp:
                current_time = datetime.utcnow() + timedelta(hours=5, minutes=30)
                booking_expiry = reservation.booking_timestamp + timedelta(hours=12)
                if current_time > booking_expiry:
                    return '❌ Booking Expired'
            return '📅 Booked'
        
        elif status == 'occupied':
            if reservation.leaving_timestamp:
                return '✅ Completed'
            else:
                return '✅ Active'
            
        elif status == 'cancelled':
            if reservation.cancellation_reason == 'user_cancelled':
                return '❌ Cancelled by You'
            elif reservation.cancellation_reason == 'auto_cancelled_12hr':
                return '❌ Auto-cancelled'
            else:
                return '❌ Cancelled'
            
        else:
            return '✅ Completed'  

class UserReleaseSpotResource(Resource):
    @auth_required
    def post(self, reservation_id):
            current_user_id = request.current_user_id

            try:
                reservation = db.session.get(Reservation, reservation_id)
                if not reservation:
                    return jsonify({'success': False, 'message': 'Reservation not found'}), 404

                if reservation.user_id != current_user_id:
                    return jsonify({'success': False, 'message': 'Unauthorized'}), 403

                if reservation.leaving_timestamp:
                    return jsonify({'success': False, 'message': 'Spot already released'}), 400

                now = datetime.utcnow() + timedelta(hours=5, minutes=30)
                reservation.leaving_timestamp = now
                duration = now - reservation.parking_timestamp
                duration_hours = duration.total_seconds() / 3600
                # Case-insensitive lookup for parking lot
                lot = ParkingLot.query.filter(
                    db.func.lower(ParkingLot.prime_location_name) == reservation.prime_location_name.lower()).first()
                hourly_rate = lot.price_per_hour if lot else 5.0
                total_cost = round(duration_hours * hourly_rate, 2)

                # Apply loyalty points discount if points were redeemed during booking
                loyalty_discount = 0
                points_redeemed = reservation.loyalty_points_redeemed or 0
                if points_redeemed > 0:
                    loyalty_discount = points_redeemed * 0.1  # $0.10 per point
                    total_cost = max(0, total_cost - loyalty_discount)  # Ensure cost doesn't go negative

                reservation.parking_cost = total_cost
                points_earned = int(duration_hours * 2)
                user = db.session.get(User, current_user_id)
                if user:
                    user.loyalty_points = (user.loyalty_points or 0) + points_earned

                spot = db.session.get(ParkingSpot, reservation.spot_id)
                if spot:
                    spot.status = 'A'

                db.session.commit()

                if spot:
                    invalidate_parking_cache(spot.lot_id)

                invalidate_parking_cache() 
                invalidate_user_cache(current_user_id)
                invalidate_admin_cache() 

                if spot:
                    cache_manager.delete(f"spot:{spot.id}")
                    cache_manager.delete(f"lot_spots:{spot.lot_id}")

                duration_hours_display = int(duration_hours)
                duration_minutes_display = int((duration_hours % 1) * 60)
                duration_str = f"{duration_hours_display}h {duration_minutes_display}m"
                release_details = {
                    'prime_location_name': reservation.prime_location_name,
                    'spot_number': spot.spot_number if spot else 'N/A',
                    'duration': duration_str,
                    'total_cost': total_cost,
                    'points_earned': points_earned,
                    'loyalty_discount_applied': loyalty_discount if loyalty_discount > 0 else None,
                    'points_redeemed': points_redeemed if points_redeemed > 0 else None
                }

                return jsonify({
                    'success': True,
                    'message': 'Spot released successfully',
                    'release_details': release_details
                })

            except Exception as e:
                db.session.rollback()
                return jsonify({'success': False, 'message': f'Error releasing spot: {str(e)}'}), 500

class AdminExportUsersResource(Resource):
    @admin_required
    def post(self):
        try:
            current_user_id = request.current_user_id

            
            from ..tasks import export_bulk_to_admin_email
            task = export_bulk_to_admin_email.delay(current_user_id)

            return {
                'success': True,
                'message': '✅ User export has been queued! You will receive an email with the CSV file shortly.',
                'task_id': task.id
            }, 202

        except Exception as e:
            return {'success': False, 'message': f'Error queuing export task: {str(e)}'}, 500

class AdminSendMonthlyReportsResource(Resource):
    @admin_required
    def post(self):
        try:
            try:
                from backend.tasks import queue_monthly_reports_for_all_users
                task = queue_monthly_reports_for_all_users.delay()

                return {
                    'success': True,
                    'message': '✅ Monthly reports generation has been queued! All users will receive their reports via email shortly.',
                    'task_id': task.id
                }, 202

            except ImportError:
                return {
                    'success': False,
                    'message': 'Task queue system is not available. Please ensure Celery worker is running.'
                }, 503

        except Exception as e:
            return {'success': False, 'message': f'Error queuing monthly reports task: {str(e)}'}, 500

class AdminParkingLotsResource(Resource):
    @admin_required
    def get(self):
        cache_key = "admin:parking:lots:all"
        cached_lots = cache_manager.get(cache_key)
        if cached_lots:
            return {'success': True, 'parking_lots': cached_lots}

        lots = ParkingLot.query.all()
        data = []
        for lot in lots:
            total_spots = ParkingSpot.query.filter_by(lot_id=lot.id).count()
            available_spots = ParkingSpot.query.filter_by(lot_id=lot.id, status='A').count()
            occupied_spots = ParkingSpot.query.filter_by(lot_id=lot.id, status='O').count()
            maintenance_spots = ParkingSpot.query.filter_by(lot_id=lot.id, status='M').count()

            data.append({
                'id': lot.id,
                'name': lot.prime_location_name,
                'address': lot.address,  
                'pin_code': lot.pin_code, 
                'capacity': total_spots,  
                'available': available_spots, 
                'occupied': occupied_spots,  
                'maintenance': maintenance_spots,
                'price_per_hour': lot.price_per_hour,
                'created_at': lot.created_at.isoformat() if lot.created_at else None
            })
        cache_manager.set(cache_key, data, CacheTTL.PARKING_AVAILABILITY)
        return {'success': True, 'parking_lots': data}

    @admin_required
    def post(self):
        try:
            data = request.get_json()
            required_fields = ['name', 'address', 'capacity', 'price_per_hour', 'pin_code']
            for field in required_fields:
                if not data.get(field):
                    return {'success': False, 'message': f'{field.replace("_", " ").title()} is required'}, 400

            # Case-insensitive check for existing parking lot names
            existing_lot = ParkingLot.query.filter(
                db.func.lower(ParkingLot.prime_location_name) == data['name'].lower()).first()
            if existing_lot:
                return {'success': False, 'message': 'Parking lot with this name already exists'}, 400

            new_lot = ParkingLot(
                prime_location_name=data['name'].lower(),  # Store in lowercase for consistency
                address=data['address'], 
                pin_code=data['pin_code'],
                total_number_of_spots=int(data['capacity']),  
                price_per_hour=float(data['price_per_hour']),
                created_at=datetime.utcnow() + timedelta(hours=5, minutes=30)
            )

            db.session.add(new_lot)
            db.session.flush()  

            for i in range(1, int(data['capacity']) + 1): 
                spot = ParkingSpot(
                    lot_id=new_lot.id,
                    spot_number=str(i),
                    status='A', 
                    vehicle_type_supported='non-EV')
                db.session.add(spot)

            db.session.commit()

            invalidate_parking_cache()
            invalidate_admin_cache()
            return {'success': True, 'message': 'Parking lot created successfully'}, 201

        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Error creating parking lot: {str(e)}'}, 500

class AdminParkingLotResource(Resource):
    @admin_required
    def delete(self, lot_id):
        try:
            lot = db.session.get(ParkingLot, lot_id)
            if not lot:
                return {'success': False, 'message': 'Parking lot not found'}, 404

            active_reservations = db.session.query(Reservation).join(ParkingSpot).filter(
                ParkingSpot.lot_id == lot_id,
                Reservation.leaving_timestamp.is_(None)).count()

            if active_reservations > 0:
                return {
                    'success': False,
                    'message': f'Cannot delete parking lot: {active_reservations} active reservations found. Please wait for users to release their spots.'
                }, 400

            spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
            spot_ids = [spot.id for spot in spots]
            if spot_ids:
                Reservation.query.filter(
                    Reservation.spot_id.in_(spot_ids),
                    Reservation.leaving_timestamp.is_not(None) 
                ).delete(synchronize_session=False)
                MaintenanceRequest.query.filter(MaintenanceRequest.spot_id.in_(spot_ids)).delete(synchronize_session=False)

            for spot in spots:
                db.session.delete(spot)

            db.session.delete(lot)
            db.session.commit()

            invalidate_parking_cache()
            invalidate_admin_cache()
            cache_manager.delete("user:parking:lots:all")

            return {'success': True, 'message': 'Parking lot and all its spots deleted successfully.'}

        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Error deleting parking lot: {str(e)}'}, 500



class AdminParkingRecordsResource(Resource):
    @admin_required
    def get(self):
        try:
            cache_key = "admin:parking:records:all"
            cached_records = cache_manager.get(cache_key)

            if cached_records:
                return {'success': True, 'records': cached_records}

            reservations = Reservation.query.order_by(
                Reservation.booking_timestamp.desc(),
                Reservation.parking_timestamp.desc()).all()

            data = []
            for reservation in reservations:
                try:
                    user = db.session.get(User, reservation.user_id)
                    user_name = user.username if user else reservation.user_name or 'Unknown'
                    spot = db.session.get(ParkingSpot, reservation.spot_id)
                    spot_number = spot.spot_number if spot else 'Unknown'
                    duration_hours = None
                    if reservation.parking_timestamp and reservation.leaving_timestamp:
                        duration = reservation.leaving_timestamp - reservation.parking_timestamp
                        duration_hours = round(duration.total_seconds() / 3600, 2)

                    status_display = reservation.booking_status or 'completed'
                    if reservation.booking_status in ['cancelled', 'auto_cancelled']:
                        status_display = 'Cancelled'

                    elif reservation.leaving_timestamp:
                        status_display = 'Completed'
                    elif reservation.booking_status == 'occupied':
                        status_display = 'Active'

                    elif reservation.booking_status == 'booked':
                        status_display = 'Booked'

                    record = {
                        'id': reservation.id,
                        'user_name': user_name,
                        'prime_location_name': reservation.prime_location_name or 'Unknown',
                        'spot_number': spot_number,
                        'vehicle_number': reservation.vehicle_number or 'N/A',
                        'start_time': reservation.parking_timestamp.isoformat() if reservation.parking_timestamp else None,
                        'end_time': reservation.leaving_timestamp.isoformat() if reservation.leaving_timestamp else None,
                        'cost': float(reservation.parking_cost) if reservation.parking_cost else 0.0,
                        'duration_hours': duration_hours,
                        'booking_status': status_display,
                        'booking_timestamp': reservation.booking_timestamp.isoformat() if reservation.booking_timestamp else None,
                        'occupancy_timestamp': reservation.occupancy_timestamp.isoformat() if reservation.occupancy_timestamp else None
                    }
                    
                    data.append(record)
                    
                except Exception as record_error:
                    print(f"Error processing reservation {reservation.id}: {str(record_error)}")
                    continue

            cache_manager.set(cache_key, data, CacheTTL.PARKING_AVAILABILITY)

            return {'success': True, 'records': data}

        except Exception as e:
            print(f"Error in get_admin_parking_records: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'message': f'Error loading parking records: {str(e)}'}, 500
           
class AdminFeedbackResource(Resource):
    @admin_required
    def get(self):
        try:
            cache_key = "admin:feedback:all"
            cached_feedback = cache_manager.get(cache_key)
            if cached_feedback:
                return {'success': True, 'feedback': cached_feedback}

            feedback_list = UserFeedback.query.order_by(UserFeedback.submitted_at.desc()).all()
            data = []

            for feedback in feedback_list:
                data.append({
                    'id': feedback.id,
                    'user_id': feedback.user_id,
                    'user_name': feedback.user_name,
                    'user_email': feedback.user_email,
                    'user_phone': feedback.user_phone,
                    'parking_lot_name': feedback.parking_lot_name,
                    'spot_number': feedback.spot_number,
                    'issue_category': feedback.issue_category,
                    'description': feedback.description,
                    'status': feedback.status,
                    'admin_response': feedback.admin_response,
                    'submitted_at': feedback.submitted_at.isoformat() if feedback.submitted_at else None,
                    'updated_at': feedback.updated_at.isoformat() if feedback.updated_at else None
                })

            cache_manager.set(cache_key, data, CacheTTL.ADMIN_FEEDBACK)

            return {'success': True, 'feedback': data}

        except Exception as e:
            return {'success': False, 'message': f'Error loading feedback: {str(e)}'}, 500

    @admin_required
    def put(self):
        try:
            data = request.get_json()
            feedback_id = data.get('feedback_id')
            status = data.get('status')
            admin_response = data.get('admin_response')
            if not feedback_id:
                return {'success': False, 'message': 'Feedback ID is required'}, 400

            feedback = db.session.get(UserFeedback, feedback_id)
            if not feedback:
                return {'success': False, 'message': 'Feedback not found'}, 404

            if status:
                feedback.status = status
            if admin_response:
                feedback.admin_response = admin_response

            feedback.updated_at = datetime.utcnow() + timedelta(hours=5, minutes=30)
            db.session.commit()
            cache_manager.delete("admin:feedback:all")
            return {'success': True, 'message': 'Feedback updated successfully'}

        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Error updating feedback: {str(e)}'}, 500

class AdminToggleMaintenanceResource(Resource):
    @admin_required
    def put(self, spot_id):
        try:
            spot = db.session.get(ParkingSpot, spot_id)
            if not spot:
                return {'success': False, 'message': 'Parking spot not found'}, 404
            
            spot.is_under_maintenance = not spot.is_under_maintenance
            db.session.commit()
            invalidate_parking_cache()
            status = "under maintenance" if spot.is_under_maintenance else "available"
            return {
                'success': True,
                'message': f'Spot {spot.spot_number} is now {status}',
                'spot': {
                    'id': spot.id,
                    'spot_number': spot.spot_number,
                    'is_under_maintenance': spot.is_under_maintenance
                }
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Error toggling maintenance: {str(e)}'}, 500

class AdminToggleSpotTypeResource(Resource):
    @admin_required
    def put(self, spot_id):
        try:
            data=request.get_json()
            vehicle_type = data.get('vehicle_type')
            spot = db.session.get(ParkingSpot, spot_id)
            if not spot:
                return {'success': False, 'message': 'Parking spot not found'}, 404
            
            old_type = spot.vehicle_type_supported
            spot.vehicle_type_supported = vehicle_type
            db.session.commit()

            invalidate_parking_cache(spot.lot_id)
                
            return jsonify({
            'success': True,
            'message': f'Spot {spot.spot_number} vehicle type updated from {old_type} to {vehicle_type}',
            'spot_id': spot_id,
            'old_type': old_type,
            'new_type': vehicle_type
        })
            
        except Exception as e:
            return {'success': False, 'message': f'Error toggling spot type: {str(e)}'}, 500


class AdminCreateParkingLotResource(Resource):
    @admin_required
    def post(self):
        try:
            data = request.get_json()
            data['prime_location_name']=data['prime_location_name'].lower()
            required_fields = ['prime_location_name', 'address', 'pin_code', 'price_per_hour', 'total_number_of_spots']
            for field in required_fields:
                if not data.get(field):
                    return {'success': False, 'message': f'{field} is required'}, 400
            
            # Case-insensitive check for existing parking lot names
            existing_lot = ParkingLot.query.filter(
                db.func.lower(ParkingLot.prime_location_name) == data['prime_location_name'].lower()).first()
            
            if existing_lot:
                return {'success': False, 'message': 'Parking lot with this name already exists'}, 400
            
            new_lot = ParkingLot(
                prime_location_name=data['prime_location_name'].lower(),
                address=data['address'],
                pin_code=data['pin_code'],
                price_per_hour=float(data['price_per_hour']),
                total_number_of_spots=int(data['total_number_of_spots'])
            )
            
            db.session.add(new_lot)
            db.session.flush()  
            
            for i in range(1, int(data['total_number_of_spots']) + 1):
                spot = ParkingSpot(
                    lot_id=new_lot.id,
                    spot_number=f"S{i:03d}",
                    status='A',
                    is_under_maintenance=False,
                    is_ev_spot=False
                )
                db.session.add(spot)
            
            db.session.commit()
            invalidate_parking_cache()
            invalidate_admin_cache()
            
            return {
                'success': True,
                'message': 'Parking lot created successfully',
                'lot_id': new_lot.id
            }, 201
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Error creating parking lot: {str(e)}'}, 500

class AdminEditParkingLotResource(Resource):
    @admin_required
    def put(self, lot_id):
        try:
            data = request.json
            lot = db.session.get(ParkingLot, lot_id)
            if not lot:
                return jsonify({'success': False, 'message': 'Parking lot not found'}), 404

            errors = []
            name = data.get('name', '').strip().lower()  # Convert to lowercase for case-insensitive comparison
            if not name:
                errors.append("Parking lot name is required")

            address = data.get('address', '').strip()
            if not address:
                errors.append("Address is required")

            elif len(address) < 5:
                errors.append("Address must be at least 5 characters long")

            pincode = data.get('pin_code', '').strip()
            if not pincode:
                errors.append("Pin code is required")

            elif not pincode.isdigit() or len(pincode) != 6:
                errors.append("Pin code must be exactly 6 digits")

            price = data.get('price_per_hour')
            if price is None:
                errors.append("Price per hour is required")

            else:
                try:
                    price = float(price)
                    if price <= 0:
                        errors.append("Price per hour must be greater than 0")
                    price = round(price, 2)

                except (TypeError, ValueError):
                    errors.append("Price per hour must be a valid number")

            capacity = data.get('capacity')
            if capacity is None:
                errors.append("Capacity is required")
            else:
                try:
                    capacity = int(capacity)
                    if capacity <= 0 or capacity > 1000:
                        errors.append("Capacity must be between 1 and 1000")
                except (TypeError, ValueError):
                    errors.append("Capacity must be a valid number")

            if errors:
                return jsonify({'success': False, 'message': '; '.join(errors)}), 400

            # Case-insensitive check for existing parking lot names
            existing_lot = ParkingLot.query.filter(
                db.func.lower(ParkingLot.prime_location_name) == name.lower(),
                ParkingLot.id != lot_id
            ).first()
            if existing_lot:
                return jsonify({'success': False, 'message': 'Parking lot with this name already exists'}), 400

            old_name = lot.prime_location_name
            name_changed = old_name.lower() != name.lower()
            lot.prime_location_name = name
            lot.price_per_hour = price
            lot.address = address
            lot.pin_code = pincode
            if name_changed:
                reservations_to_update = Reservation.query.filter_by(prime_location_name=old_name).all()
                for reservation in reservations_to_update:
                    reservation.prime_location_name = name

            current_spots = ParkingSpot.query.filter_by(lot_id=lot_id).count()
            if capacity > current_spots:
                # Get the highest existing spot number to maintain sequential numbering
                existing_spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
                max_spot_num = 0
                for spot in existing_spots:
                    # Extract numeric part from spot number (e.g., "S001" -> 1, "S123" -> 123)
                    try:
                        if spot.spot_number.startswith('S'):
                            num = int(spot.spot_number[1:])
                        else:
                            num = int(spot.spot_number)
                        max_spot_num = max(max_spot_num, num)
                    except (ValueError, IndexError):
                        # If spot number format is unexpected, use current count as fallback
                        max_spot_num = max(max_spot_num, current_spots)

                # Create new spots with proper sequential numbering
                spots_to_add = capacity - current_spots
                for i in range(spots_to_add):
                    new_spot_number = max_spot_num + i + 1
                    new_spot = ParkingSpot(
                        lot_id=lot_id,
                        spot_number=f"S{new_spot_number:03d}",  # Format as S001, S002, etc.
                        status='A',
                        vehicle_type_supported='non-EV'
                    )
                    db.session.add(new_spot)

            elif capacity < current_spots:
                booked_occupied_count = ParkingSpot.query.filter(
                    ParkingSpot.lot_id == lot_id,
                    ParkingSpot.status.in_(['B', 'O'])).count()

                if capacity < booked_occupied_count:
                    return jsonify({
                        'success': False,
                        'message': f'Cannot reduce capacity to {capacity}. Currently {booked_occupied_count} spots are booked or occupied. Minimum capacity allowed: {booked_occupied_count}'
                    }), 400

                available_spots = ParkingSpot.query.filter_by(
                    lot_id=lot_id,
                    status='A'
                ).order_by(ParkingSpot.id.desc()).all()

                spots_to_remove = []
                for spot in available_spots:
                    has_reservations = Reservation.query.filter_by(spot_id=spot.id).first() is not None
                    if not has_reservations:
                        spots_to_remove.append(spot)
                        if len(spots_to_remove) >= (current_spots - capacity):
                            break

                if len(spots_to_remove) < (current_spots - capacity):
                    for spot in available_spots:
                        if spot not in spots_to_remove:
                            spots_to_remove.append(spot)
                            if len(spots_to_remove) >= (current_spots - capacity):
                                break

                for spot in spots_to_remove:
                    db.session.delete(spot)

            lot.total_number_of_spots = capacity
            db.session.commit()
            invalidate_parking_cache(lot_id)  
            invalidate_parking_cache() 
            invalidate_admin_cache() 

            if name_changed:
                affected_users = db.session.query(Reservation.user_id).filter_by(prime_location_name=name).distinct().all()
                for user_tuple in affected_users:
                    invalidate_user_cache(user_tuple[0])

            return jsonify({'success': True, 'message': 'Parking lot updated successfully'})

        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Error updating parking lot: {str(e)}'}), 500

class AdminDeleteParkingLotResource(Resource):
    @admin_required
    def delete(self, lot_id):
        try:
            lot = db.session.get(ParkingLot, lot_id)
            if not lot:
                return {'success': False, 'message': 'Parking lot not found'}, 404
            
            active_reservations = Reservation.query.join(ParkingSpot).filter(
                ParkingSpot.lot_id == lot_id,
                Reservation.leaving_timestamp.is_(None)).count()
            
            if active_reservations > 0:
                return {
                    'success': False, 
                    'message': 'Cannot delete parking lot with active reservations'
                }, 400
            
            ParkingSpot.query.filter_by(lot_id=lot_id).delete()
            db.session.delete(lot)
            db.session.commit()
            
            invalidate_parking_cache()
            invalidate_admin_cache()
            
            return {
                'success': True,
                'message': 'Parking lot deleted successfully'
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Error deleting parking lot: {str(e)}'}, 500

class AdminUsersResource(Resource):
    @admin_required
    def get(self):
        try:
            cache_key = "admin:users:all"
            cached_users = cache_manager.get(cache_key)
            if cached_users:
                return {'success': True, 'users': cached_users}

            users = User.query.filter(User.role != 'admin').all()
            data = []
            for user in users:
                # Get active reservation info for current spot and location
                active_res = Reservation.query.filter_by(
                    user_id=user.id,
                    leaving_timestamp=None).first()

                data.append({
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role or 'user',
                    'phone_number': user.phone_number,
                    'loyalty_points': user.loyalty_points or 0,
                    'profile_created_at': user.profile_created_at.isoformat() if user.profile_created_at else None,
                    'current_spot': active_res.spot.spot_number if active_res and active_res.spot else None,
                    'location': active_res.prime_location_name if active_res else None
                })

            cache_manager.set(cache_key, data, CacheTTL.ADMIN_RECORDS)
            return {'success': True, 'users': data}

        except Exception as e:
            return {'success': False, 'message': f'Error loading users: {str(e)}'}, 500

class AdminGetSpotsbylotsResource(Resource):
    @admin_required
    def get(self, lot_id):
        cache_key = CacheKeys.parking_spots(lot_id)
        cached_spots = cache_manager.get(cache_key)

        if cached_spots:
            return jsonify({'success': True, 'spots': cached_spots})

        spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
        data = []
        for spot in spots:
            reservation = None
            if spot.status == 'O':
                reservation = Reservation.query.filter_by(
                    spot_id=spot.id,
                    leaving_timestamp=None
                ).first()

            elif spot.status == 'B':
                reservation = Reservation.query.filter_by(
                    spot_id=spot.id,
                    booking_status='booked',
                    leaving_timestamp=None
                ).first()

            data.append({
                'id': spot.id,
                'spot_number': spot.spot_number,
                'status': spot.status,
                'vehicle_type': spot.vehicle_type_supported,
                'is_occupied': spot.status == 'O',
                'is_booked': spot.status == 'B',
                'is_maintenance': spot.is_under_maintenance,
                'maintenance_reason': spot.maintenance_reason,
                'maintenance_started_at': spot.maintenance_started_at.isoformat() if spot.maintenance_started_at else None,
                'vehicle_number': reservation.vehicle_number if reservation else None,
                'user_name': reservation.user_name if reservation else None,
                'parking_timestamp': reservation.parking_timestamp.isoformat() if reservation and reservation.parking_timestamp else None,
                'booking_timestamp': reservation.booking_timestamp.isoformat() if reservation and reservation.booking_timestamp else None
            })

        cache_manager.set(cache_key, data, CacheTTL.PARKING_SPOTS)
        return jsonify({'success': True, 'spots': data})

class UserChangePasswordResource(Resource):
    @auth_required
    def post(self):
        try:
            current_user_id = request.current_user_id
            data = request.get_json()
            current_pwd = data.get('current_password')
            new_pwd = data.get('new_password')
            if not current_pwd or not new_pwd:
                return {'success': False, 'message': 'Current password and new password are required'}, 400

            user = db.session.get(User, current_user_id)
            if not user:
                return {'success': False, 'message': 'User not found'}, 404

            if not user.chckpwd(current_pwd):
                return {'success': False, 'message': 'Current password is incorrect'}, 400

            if len(new_pwd) < 6:
                return {'success': False, 'message': 'New password must be at least 6 characters long'}, 400

            if not any(c.isupper() for c in new_pwd):
                return {'success': False, 'message': 'Password must contain at least one uppercase letter'}, 400

            if not any(c.islower() for c in new_pwd):
                return {'success': False, 'message': 'Password must contain at least one lowercase letter'}, 400

            if not any(c.isdigit() for c in new_pwd):
                return {'success': False, 'message': 'Password must contain at least one number'}, 400

            if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in new_pwd):
                return {'success': False, 'message': 'Password must contain at least one symbol'}, 400

            user.setpwd(new_pwd)
            db.session.commit()
            invalidate_user_cache(current_user_id)
            return {'success': True, 'message': 'Password changed successfully'}

        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Error changing password: {str(e)}'}, 500

class UserUpdateProfileResource(Resource):
    @auth_required
    def put(self):
        try:
            current_user_id = request.current_user_id
            data = request.get_json()
            user = db.session.get(User, current_user_id)
            if not user:
                return {'success': False, 'message': 'User not found'}, 404

            if 'email' in data:
                email = data['email'].strip()
                if not email:
                    return {'success': False, 'message': 'Email cannot be empty'}, 400

                existing_user = User.query.filter(User.email == email, User.id != current_user_id).first()
                if existing_user:
                    return {'success': False, 'message': 'Email is already taken'}, 400

                user.email = email

            if 'phone_number' in data:
                phone = data['phone_number']
                if phone and len(phone) < 10:
                    return {'success': False, 'message': 'Phone number must be at least 10 digits'}, 400
                user.phone_number = phone

            if 'username' in data:
                username = data['username'].strip()
                if not username:
                    return {'success': False, 'message': 'Username cannot be empty'}, 400

                existing_user = User.query.filter(User.username == username, User.id != current_user_id).first()
                if existing_user:
                    return {'success': False, 'message': 'Username is already taken'}, 400

                user.username = username

            db.session.commit()

            invalidate_user_cache(current_user_id)

            return {'success': True, 'message': 'Profile updated successfully','user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'phone_number': user.phone_number,
                'role': user.role,
                'loyalty_points': user.loyalty_points,
                'profile_created_at': user.profile_created_at.isoformat()
            }}

        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Error updating profile: {str(e)}'}, 500

class UserReservationsResource(Resource):
    @auth_required
    def get(self):
        try:
            current_user_id = request.current_user_id
            cache_key = f"user:reservations:{current_user_id}"
            cached_reservations = cache_manager.get(cache_key)
            if cached_reservations:
                return {'success': True, 'reservations': cached_reservations}

            reservations = Reservation.query.filter_by(user_id=current_user_id).order_by(Reservation.parking_timestamp.desc()).all()
            data = []

            for reservation in reservations:
                data.append({
                    'id': reservation.id,
                    'spot_number': reservation.spot.spot_number if reservation.spot else 'Unknown',
                    'prime_location_name': reservation.prime_location_name,
                    'vehicle_number': reservation.vehicle_number,
                    'parking_timestamp': reservation.parking_timestamp.isoformat() if reservation.parking_timestamp else None,
                    'leaving_timestamp': reservation.leaving_timestamp.isoformat() if reservation.leaving_timestamp else None,
                    'parking_cost': reservation.parking_cost,
                    'status': 'Active' if not reservation.leaving_timestamp else 'Completed',
                    'duration_hours': self._calculate_duration(reservation.parking_timestamp, reservation.leaving_timestamp) if reservation.leaving_timestamp else None
                })

            cache_manager.set(cache_key, data, CacheTTL.USER_RESERVATIONS)

            return {'success': True, 'reservations': data}

        except Exception as e:
            return {'success': False, 'message': f'Error loading reservations: {str(e)}'}, 500

    def _calculate_duration(self, start_time, end_time):
        if not start_time or not end_time:
            return None

        duration = end_time - start_time
        return round(duration.total_seconds() / 3600, 2) 

    def _get_user_status_description(self, reservation):
        status = reservation.booking_status or 'occupied'
        
        if status == 'booked':
            if reservation.booking_timestamp:
                current_time = datetime.utcnow() + timedelta(hours=5, minutes=30)
                booking_expiry = reservation.booking_timestamp + timedelta(hours=12)
                if current_time > booking_expiry:
                    return '❌ Booking Expired'

            return '📅 Booked'

        elif status == 'occupied':
            if reservation.leaving_timestamp:
                return '✅ Completed'

            else:
                return '✅ Active'

        elif status == 'cancelled':
            if reservation.cancellation_reason == 'user_cancelled':
                return '❌ Cancelled by You'

            elif reservation.cancellation_reason == 'auto_cancelled_12hr':
                return '❌ Auto-cancelled'

            else:
                return '❌ Cancelled'

        else:
            return '✅ Completed' 

class AdminUpdateFeedbackResource(Resource):
    @admin_required
    def put(self, feedback_id):
        try:
            data = request.get_json()
            feedback = db.session.get(UserFeedback, feedback_id)
            
            if not feedback:
                return {'success': False, 'message': 'Feedback not found'}, 404
            
            if 'subject' in data:
                feedback.description = data['subject']
            
            if 'admin_response' in data:
                feedback.admin_response = data['admin_response']
            
            db.session.commit()
            invalidate_admin_cache()
            return {
                'success': True,
                'message': 'Feedback updated successfully',
                'feedback': {
                    'id': feedback.id,
                    'subject': feedback.description,
                    'admin_response': feedback.admin_response,
                }
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Error updating feedback: {str(e)}'}, 500