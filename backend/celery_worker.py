import os
import sys
from dotenv import load_dotenv
from celery import Celery
from celery.schedules import crontab
from . import tasks

load_dotenv()

if sys.platform == 'win32':
    os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')

def create_celery_app():
    from .app import create_app
    flask_app = create_app()
    celery = Celery(
        flask_app.import_name,
        backend=os.getenv('CELERY_RESULT_BACKEND'),
        broker=os.getenv('CELERY_BROKER_URL'),
        include=['backend.tasks']  
    )

    if sys.platform == 'win32':
        celery.conf.update(
            worker_pool='solo',worker_prefetch_multiplier=1,worker_concurrency=1,result_persistent=False,
            task_serializer='json',result_serializer='json',accept_content=['json'],enable_utc=True,timezone='UTC',)

    celery.conf.update(flask_app.config)
    celery.conf.beat_schedule = {
        'send-daily-reminders': {
            'task': 'tasks.send_daily_reminders',
            'schedule': crontab(hour=5, minute=30), #IST 11:00 AM
        },
        'send-monthly-reports': {
            'task': 'tasks.queue_monthly_reports_for_all_users',
            'schedule': crontab(day_of_month=1, hour=0, minute=0),
        },
        'cleanup-old-exports': {
            'task': 'tasks.cleanup_old_exports',
            'schedule': crontab(day_of_week=0, hour=0, minute=0),
        },
        'auto-cancel-expired-bookings': {
            'task': 'tasks.auto_cancel_expired_bookings',
            'schedule': crontab(minute=0), 
        },
    }
    celery.conf.timezone = 'UTC'

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with flask_app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

celery_app = create_celery_app()
tasks.celery_app = celery_app
print(" Tasks module imported and configured successfully")