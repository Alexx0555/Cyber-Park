import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backend.celery_worker import create_celery_app

celery_app = create_celery_app()
if __name__ == '__main__':
    celery_app.start()