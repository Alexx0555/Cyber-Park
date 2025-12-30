import csv
import os
from datetime import datetime, timedelta
from flask import render_template
from celery import Celery
from .models import User, Reservation, ParkingSpot
from .utils import send_email_utility, send_html_email

celery_app = Celery('tasks')

@celery_app.task(name='tasks.export_history_csv')
def export_history_csv(user_id):
    from .app import create_app

    app = create_app()
    with app.app_context():
        user = User.query.get(user_id)
        if not user:
            return f"User with ID {user_id} not found"

        hist_rec = Reservation.query.filter_by(user_id=user_id).order_by(Reservation.parking_timestamp.desc()).all()
        filepath = os.path.join("exports", f"{user.username}_history_{datetime.now().strftime('%Y%m%d')}.csv")
        os.makedirs('exports', exist_ok=True)

        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['record_id', 'location_name', 'spot_number', 'vehicle_number', 'start_time', 'end_time', 'cost', 'duration_hours']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for rec in hist_rec:
                spot_number = 'N/A'
                if rec.spot_id:
                    spot = ParkingSpot.query.get(rec.spot_id)
                    if spot:
                        spot_number = spot.spot_number

                durhrs = 0
                if rec.leaving_timestamp and rec.parking_timestamp:
                    dur = rec.leaving_timestamp - rec.parking_timestamp
                    durhrs = round(dur.total_seconds() / 3600, 2)

                writer.writerow({
                    'record_id': rec.id,
                    'location_name': rec.prime_location_name,
                    'spot_number': spot_number,
                    'vehicle_number': rec.vehicle_number,
                    'start_time': rec.parking_timestamp.strftime('%Y-%m-%d %H:%M:%S') if rec.parking_timestamp else 'N/A',
                    'end_time': rec.leaving_timestamp.strftime('%Y-%m-%d %H:%M:%S') if rec.leaving_timestamp else 'Active',
                    'cost': rec.parking_cost or 0,
                    'duration_hours': durhrs
                })

        subject = "📜 Your Parking History Scroll is Ready! 📜"
        body = f"""Greetings, {user.username}!

The Oracle's Scribes have finished preparing your parking history scroll.

📊 Summary:
- Total Records: {len(hist_rec)}
- Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- File: {user.username}_history_{datetime.now().strftime('%Y%m%d')}.csv

Your mystical parking chronicle is attached to this email as a CSV file. You can open it with Excel, Google Sheets, or any spreadsheet application.

May your parking adventures be ever prosperous!

The CyberPark Oracle 🔮"""

        with open(filepath, 'rb') as csv_file:
            csv_content = csv_file.read()

        send_email_utility(user.email,subject,body,
            attachments=[(f"{user.username}_history_{datetime.now().strftime('%Y%m%d')}.csv", 'text/csv', csv_content)])

        return f"Successfully generated {filepath} with {len(hist_rec)} records"

@celery_app.task(name='tasks.send_daily_reminders')
def send_daily_reminders():
    from .models import User, ParkingLot
    from .app import create_app
    from flask import render_template

    app = create_app()
    with app.app_context():
        try:
            today = datetime.now().date()
            yesterday = today - timedelta(days=1)
            new_lots = ParkingLot.query.filter(ParkingLot.created_at >= yesterday).all()
            users = User.query.filter(User.role != 'admin').all()
            if not users:
                return "No users found to send reminders to"

            sent_count = 0
            failed_count = 0
            for u in users:
                try:
                    html_body = render_template('daily_reminder.html',
                        username=u.username,
                        current_date=datetime.now().strftime('%B %d, %Y'),
                        new_lots_info=getnewlotinfo(new_lots) if new_lots else "No new parking lots today.",
                        loyalty_points=u.loyalty_points or 0
                    )
                    subject = f"🚗 CyberPark Daily Reminder - {datetime.now().strftime('%B %d, %Y')}"
                    success = send_html_email(u.email, subject, html_body)
                    if success:
                        sent_count += 1
                    else:
                        failed_count += 1

                except Exception as user_error:
                    print(f"Failed to send reminder to {u.email}: {str(user_error)}")
                    failed_count += 1
                    continue

            return f"Daily reminders sent: {sent_count} successful, {failed_count} failed. New lots: {len(new_lots)}"

        except Exception as e:
            return f"Error in daily reminders: {str(e)}"

def getnewlotinfo(nlots):
    if not nlots:
        return "No new parking lots today."

    info = "<ul>"
    for lot in nlots:
        info += f"<li><strong>{lot.prime_location_name}</strong> - {lot.total_number_of_spots} spots available at ${lot.price_per_hour}/hour</li>"
    info += "</ul>"
    return info


@celery_app.task(name='tasks.export_bulk_to_admin_email')
def export_bulk_to_admin_email(admin_user_id):
    from .models import db, User, Reservation
    from .app import create_app

    app = create_app()
    with app.app_context():
        try:
            admin = User.query.get(admin_user_id)
            if not admin or admin.role != 'admin':
                return "Error: Admin user not found"

            users = User.query.filter(User.role != 'admin').all()
            os.makedirs("exports", exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"bulk_export_admin_{timestamp}.csv"
            filepath = os.path.join("exports", filename)
            totrecs = 0
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['user_id', 'username', 'email', 'phone_number', 'loyalty_points',
                             'record_id', 'location_name', 'spot_number', 'vehicle_number',
                             'start_time', 'end_time', 'cost', 'duration_hours']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for u in users:
                    reservations = Reservation.query.filter_by(user_id=u.id).order_by(Reservation.parking_timestamp.desc()).all()

                    if reservations:
                        for reservation in reservations:
                            durhrs = None
                            end_time_str = None
                            if reservation.leaving_timestamp and reservation.parking_timestamp:
                                dur = reservation.leaving_timestamp - reservation.parking_timestamp
                                durhrs = round(dur.total_seconds() / 3600, 2)
                                end_time_str = reservation.leaving_timestamp.strftime("%Y-%m-%d %H:%M:%S")

                            writer.writerow({
                                'user_id': u.id,
                                'username': u.username,
                                'email': u.email,
                                'phone_number': u.phone_number,
                                'loyalty_points': u.loyalty_points or 0,
                                'record_id': reservation.id,
                                'location_name': reservation.prime_location_name,
                                'spot_number': reservation.spot_id,
                                'vehicle_number': reservation.vehicle_number,
                                'start_time': reservation.parking_timestamp.strftime("%Y-%m-%d %H:%M:%S")  if reservation.parking_timestamp else 'N/A',
                                'end_time': end_time_str or "Active",
                                'cost': reservation.parking_cost or 0,
                                'duration_hours': durhrs if durhrs is not None else ''
                            })
                            totrecs += 1

                    else:
                        writer.writerow({
                            'user_id': u.id,
                            'username': u.username,
                            'email': u.email,
                            'phone_number': u.phone_number,
                            'loyalty_points': u.loyalty_points or 0,
                            'record_id': '',
                            'location_name': '',
                            'spot_number': '',
                            'vehicle_number': '',
                            'start_time': '',
                            'end_time': '',
                            'cost': '',
                            'duration_hours': ''
                        })
                        totrecs += 1

            subject = f"🔮 CyberPark Bulk Export - All Users Data ({datetime.now().strftime('%Y-%m-%d')})"
            body = f"""Greetings, Supreme Oracle {admin.username}!

Your requested bulk export of all users' parking data has been completed.

📊 Export Summary:
- Total Users: {len(users)}
- Total Records: {totrecs}
- Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- File: {filename}

The complete dataset is attached as a CSV file containing:
- User profiles (ID, username, email, phone, loyalty points)
- All parking reservations and history
- Costs, durations, and locations

This export was generated for administrative purposes and contains sensitive user data. Please handle with appropriate security measures.

May this data illuminate your administrative decisions!

The CyberPark Oracle 🔮"""

            with open(filepath, 'rb') as csv_file:
                csv_content = csv_file.read()

            send_email_utility(admin.email,subject,body,attachments=[(filename, 'text/csv', csv_content)])

            return f"Successfully generated and emailed bulk export with {totrecs} records for {len(users)} users to {admin.email}"

        except Exception as e:
            return f"Error generating bulk export for admin: {str(e)}"

@celery_app.task(name='tasks.cleanup_old_exports')
def cleanup_old_exports():
    import time

    try:
        exports_dir = "exports"
        if not os.path.exists(exports_dir):
            return "Exports directory does not exist"

        cutoff_time = time.time() - (7 * 24 * 60 * 60) 
        deleted_count = 0
        total_size = 0

        for filename in os.listdir(exports_dir):
            filepath = os.path.join(exports_dir, filename)
            if not os.path.isfile(filepath):
                continue

            file_modified_time = os.path.getmtime(filepath)
            if file_modified_time < cutoff_time:
                try:
                    file_size = os.path.getsize(filepath)
                    os.remove(filepath)
                    deleted_count += 1
                    total_size += file_size
                    print(f"Deleted old export file: {filename}")

                except Exception as e:
                    print(f"Failed to delete {filename}: {str(e)}")
                    continue

        total_size_mb = round(total_size / (1024 * 1024), 2)
        return f"Cleanup completed: Deleted {deleted_count} old export files, freed {total_size_mb} MB of space"

    except Exception as e:
        return f"Error during cleanup: {str(e)}"

@celery_app.task(name='tasks.send_monthly_report')
def send_monthly_report(user_id):
    from .app import create_app

    app = create_app()
    with app.app_context():
        user = User.query.get(user_id)
        if not user:
            return f"User with ID {user_id} not found"

        one_month = datetime.now() - timedelta(days=30)
        monthly_rec = Reservation.query.filter(
            Reservation.user_id == user_id,Reservation.parking_timestamp >= one_month).all()
        tot_spent = sum(r.parking_cost or 0 for r in monthly_rec)
        tot_sessions = len(monthly_rec)
        comp_sessions = len([r for r in monthly_rec if r.leaving_timestamp])
        act_sessions = tot_sessions - comp_sessions
        tothrs = 0
        for rec in monthly_rec:
            if rec.leaving_timestamp and rec.parking_timestamp:
                dur = rec.leaving_timestamp - rec.parking_timestamp
                tothrs += dur.total_seconds() / 3600

        loc_usage = {}
        for rec in monthly_rec:
            loc = rec.prime_location_name
            loc_usage[loc] = loc_usage.get(loc, 0) + 1

        most_used = max(loc_usage.items(), key=lambda x: x[1]) if loc_usage else ("None", 0)

        html_body = render_template('monthly_report.html',user=user,records=monthly_rec,total_spent=tot_spent,total_sessions=tot_sessions,
            completed_sessions=comp_sessions,active_sessions=act_sessions,total_hours=round(tothrs, 2),most_used_location=most_used[0],
            location_usage=loc_usage,report_month=datetime.now().strftime('%B %Y'))

        subject = f"🔮 Oracle's Report: Your Parking Chronicle for {datetime.now().strftime('%B %Y')}"
        send_html_email(user.email, subject, html_body)
        return f"Monthly report sent to {user.email} for {datetime.now().strftime('%B %Y')}"

@celery_app.task(name='tasks.queue_monthly_reports_for_all_users')
def queue_monthly_reports_for_all_users():
    from .models import User
    from .app import create_app

    app = create_app()
    with app.app_context():
        try:
            users = User.query.filter(User.role != 'admin').all()
            qco = 0
            for u in users:
                send_monthly_report.delay(u.id) 
                qco += 1

            return f"Successfully queued monthly reports for {qco} users (excluding admin accounts)"
        
        except Exception as e:
            return f"Error queuing monthly reports: {str(e)}"


@celery_app.task(name='tasks.export_user_history_to_email')
def export_user_history_to_email(user_id):
    from .models import User, Reservation
    from .app import create_app

    app = create_app()
    with app.app_context():
        try:
            user = User.query.get(user_id)
            if not user:
                return "Error: User not found"

            os.makedirs("exports", exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{user.username}_history_{timestamp}.csv"
            filepath = os.path.join("exports", filename)
            reservations = Reservation.query.filter_by(user_id=user.id).order_by(Reservation.parking_timestamp.desc()).all()
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['location', 'spot_number', 'vehicle', 'start_time', 'end_time', 'duration', 'cost']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for reservation in reservations:
                    duration_str = "Active"
                    end_time_str = "Active"
                    cost = reservation.parking_cost or 0

                    if reservation.leaving_timestamp and reservation.parking_timestamp:
                        end_time_str = reservation.leaving_timestamp.strftime('%Y-%m-%d %H:%M:%S')
                        dur = reservation.leaving_timestamp - reservation.parking_timestamp
                        hours = dur.total_seconds() / 3600
                        duration_str = f"{hours:.1f} hours"

                    spot_number = reservation.spot.spot_number if reservation.spot else 'N/A'

                    writer.writerow({
                        'location': reservation.prime_location_name,
                        'spot_number': spot_number,
                        'vehicle': reservation.vehicle_number,
                        'start_time': reservation.parking_timestamp.strftime('%Y-%m-%d %H:%M:%S') if reservation.parking_timestamp else 'N/A',
                        'end_time': end_time_str,
                        'duration': duration_str,
                        'cost': f"${cost:.2f}"
                    })

            subject = f"CyberPark - Your Parking History Export"
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #4CAF50; text-align: center;">🚗 CyberPark History Export</h2>
                    <h3>Hello {user.username}!</h3>

                    <p>Your parking history export is ready! Please find your complete parking records attached as a CSV file.</p>

                    <div style="background-color: #f9f9f9; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h4 style="color: #2196F3; margin-top: 0;">📊 Export Details</h4>
                        <ul style="list-style: none; padding: 0;">
                            <li style="padding: 5px 0;"><strong>📅 Export Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</li>
                            <li style="padding: 5px 0;"><strong>📋 Total Records:</strong> {len(reservations)}</li>
                            <li style="padding: 5px 0;"><strong>📎 File Format:</strong> CSV (Excel Compatible)</li>
                        </ul>
                    </div>

                    <div style="background-color: #e8f5e8; padding: 15px; border-radius: 8px; margin: 20px 0;">
                        <h4 style="color: #4CAF50; margin-top: 0;">💡 CSV File Contents</h4>
                        <p>Your export includes: Location, Spot Number, Vehicle, Start Time, End Time, Duration, and Cost for all your parking sessions.</p>
                    </div>

                    <div style="text-align: center; margin: 30px 0;">
                        <p style="color: #666;">Thank you for using CyberPark!</p>
                        <p style="font-size: 12px; color: #999;">
                            Export generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """

            with open(filepath, 'rb') as f:
                csv_data = f.read()

            attachments = [(filename, 'text/csv', csv_data)]
            success = send_email_utility(to_mail=user.email,sub=subject,body=html_body,attachments=attachments,is_html=True)

            if success:
                return f"Successfully exported {len(reservations)} records and sent to {user.email}"
            else:
                return f"Export completed but email delivery failed for {user.email}"

        except Exception as e:
            return f"Error exporting user history: {str(e)}"

@celery_app.task(name='tasks.auto_cancel_expired_bookings')
def auto_cancel_expired_bookings():
    from .models import db, ParkingSpot
    from .app import create_app
    from .cache_utils import invalidate_parking_cache, invalidate_admin_cache

    app = create_app()
    with app.app_context():
        try:
            current_utc = datetime.utcnow()
            expiry_cutoff = current_utc - timedelta(hours=12)
            expired_bookings = Reservation.query.filter(
                Reservation.booking_status == 'booked',
                Reservation.booking_timestamp <= expiry_cutoff).all()

            cancelled_count = 0
            for booking in expired_bookings:
                spot = ParkingSpot.query.get(booking.spot_id)
                if spot and spot.status == 'B':
                    spot.status = 'A'
                    invalidate_parking_cache(spot.lot_id)

                db.session.delete(booking)
                cancelled_count += 1

            db.session.commit()
            invalidate_parking_cache()
            invalidate_admin_cache()

            return f"Successfully auto-cancelled {cancelled_count} expired bookings"

        except Exception as e:
            db.session.rollback()
            return f"Error auto-cancelling expired bookings: {str(e)}"