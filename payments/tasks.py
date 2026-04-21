from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@shared_task
def cleanup_pending_orders():
    """Delete pending orders older than 24 hours"""
    from .models import Order
    cutoff = timezone.now() - timedelta(hours=24)
    old_orders = Order.objects.filter(status='pending', created_at__lt=cutoff)
    count = old_orders.count()
    old_orders.delete()
    logger.info(f"Cleaned up {count} stale pending orders")
    return count


@shared_task
def send_payment_receipt(order_id):
    """Send payment receipt email after successful payment"""
    from .models import Order
    try:
        order = Order.objects.select_related('student', 'course').get(id=order_id)
        send_mail(
            subject=f'Payment Receipt — {order.course.title}',
            message=(
                f"Hi {order.student.first_name or order.student.username},\n\n"
                f"Your payment of ₹{order.amount} for '{order.course.title}' was successful.\n"
                f"Order ID: {order.razorpay_order_id}\n\n"
                f"Happy learning! 🎓"
            ),
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[order.student.email],
            fail_silently=True,
        )
        logger.info(f"Receipt sent for order {order_id}")
    except Exception as e:
        logger.error(f"Receipt email failed: {e}")
