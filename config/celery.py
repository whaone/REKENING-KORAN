# config/celery.py
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('rekening_koran')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Baris sakti ini yang akan mencari tasks.py di setiap app
app.autodiscover_tasks()