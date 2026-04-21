import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('edtech')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Periodic tasks
app.conf.beat_schedule = {
    'cleanup-pending-orders': {
        'task': 'payments.tasks.cleanup_pending_orders',
        'schedule': crontab(hour=0, minute=0),  # Daily at midnight
    },
    'send-live-class-reminders': {
        'task': 'live_classes.tasks.send_live_class_reminders',
        'schedule': crontab(hour=9, minute=0),  # Daily at 9 AM
    },
    'generate-course-certificates': {
        'task': 'courses.tasks.generate_certificates',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
