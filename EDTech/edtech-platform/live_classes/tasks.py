from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_live_class_reminders():
    """
    Send reminder emails 30 minutes before each scheduled live class.
    Run this task every 15 minutes via Celery Beat.
    """
    from .models import LiveClass
    from courses.models import Enrollment

    now = timezone.now()
    window_start = now + timedelta(minutes=25)
    window_end = now + timedelta(minutes=35)

    upcoming = LiveClass.objects.filter(
        status='scheduled',
        scheduled_at__gte=window_start,
        scheduled_at__lte=window_end,
    )

    for lc in upcoming:
        enrollments = Enrollment.objects.filter(
            course=lc.course
        ).select_related('student')

        for enrollment in enrollments:
            student = enrollment.student
            if not student.email:
                continue
            send_mail(
                subject=f'Reminder: "{lc.title}" starts in 30 minutes',
                message=(
                    f"Hi {student.first_name or student.username},\n\n"
                    f'Your live class "{lc.title}" starts at {lc.scheduled_at.strftime("%H:%M UTC")}.\n'
                    f"Be ready to join!\n\nHappy learning! 🎓"
                ),
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[student.email],
                fail_silently=True,
            )

        logger.info(f"Reminders sent for live class {lc.id}")

    return upcoming.count()
