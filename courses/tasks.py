from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@shared_task
def generate_certificates():
    """
    Find enrollments that hit 100% progress today and send certificate email.
    """
    from courses.models import Enrollment

    completed_today = Enrollment.objects.filter(
        completed=True,
        completed_at__date=timezone.now().date(),
    ).select_related('student', 'course')

    for enrollment in completed_today:
        student = enrollment.student
        course = enrollment.course
        if not student.email:
            continue
        send_mail(
            subject=f'🏆 Certificate of Completion — {course.title}',
            message=(
                f"Congratulations {student.first_name or student.username}!\n\n"
                f"You have successfully completed '{course.title}'.\n"
                f"Keep up the great work! 🎓"
            ),
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[student.email],
            fail_silently=True,
        )

    logger.info(f"Certificates sent to {completed_today.count()} students")
    return completed_today.count()
