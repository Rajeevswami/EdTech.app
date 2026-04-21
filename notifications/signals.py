from django.db.models.signals import post_save
from django.dispatch import receiver
from payments.models import Order
from courses.models import Enrollment
from .models import Notification


@receiver(post_save, sender=Order)
def notify_payment_success(sender, instance, created, **kwargs):
    if not created and instance.status == 'completed':
        Notification.objects.create(
            recipient=instance.student,
            notification_type='payment_success',
            title='Payment Successful! 🎉',
            message=f'Your payment of ₹{instance.amount} for "{instance.course.title}" was successful.',
            data={'order_id': str(instance.id), 'course_id': str(instance.course.id)},
        )


@receiver(post_save, sender=Enrollment)
def notify_course_enrolled(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            recipient=instance.student,
            notification_type='course_enrolled',
            title='Enrolled Successfully! 📚',
            message=f'You have been enrolled in "{instance.course.title}". Start learning now!',
            data={'course_id': str(instance.course.id)},
        )
