from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db import transaction
import logging

from .models import Order, Payment
from .serializers import OrderSerializer, PaymentSerializer, CreateOrderSerializer, VerifyPaymentSerializer
from .razorpay_client import RazorpayPaymentManager
from courses.models import Course, Enrollment

logger = logging.getLogger(__name__)

class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(student=self.request.user)
    
    @action(detail=False, methods=['post'])
    def create_order(self, request):
        """Create Razorpay payment order"""
        try:
            serializer = CreateOrderSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            course_id = serializer.validated_data['course_id']
            course = Course.objects.get(id=course_id)
            
            # Check if already enrolled
            if Enrollment.objects.filter(student=request.user, course=course).exists():
                return Response(
                    {'error': 'Already enrolled in this course'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if already paid for
            if Order.objects.filter(
                student=request.user,
                course=course,
                status__in=['completed', 'pending']
            ).exists():
                return Response(
                    {'error': 'Order already exists for this course'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create order in database
            with transaction.atomic():
                order = Order.objects.create(
                    student=request.user,
                    course=course,
                    amount=course.price
                )
                
                # Create Razorpay order
                razorpay_manager = RazorpayPaymentManager()
                razorpay_order = razorpay_manager.create_order(
                    course_id=course.id,
                    amount=course.price,
                    user_id=request.user.id
                )
                
                # Update order with Razorpay ID
                order.razorpay_order_id = razorpay_order['id']
                order.save()
            
            logger.info(f"Order created: {order.id} for user {request.user.id}")
            
            return Response({
                'order_id': str(order.id),
                'razorpay_order_id': razorpay_order['id'],
                'amount': order.amount,
                'currency': 'INR',
                'key': settings.RAZORPAY_KEY_ID,
            }, status=status.HTTP_201_CREATED)
        
        except Course.DoesNotExist:
            return Response(
                {'error': 'Course not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Order creation error: {str(e)}")
            return Response(
                {'error': 'Order creation failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def verify_payment(self, request):
        """Verify Razorpay payment and enroll student"""
        try:
            serializer = VerifyPaymentSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            razorpay_order_id = serializer.validated_data['razorpay_order_id']
            razorpay_payment_id = serializer.validated_data['razorpay_payment_id']
            razorpay_signature = serializer.validated_data['razorpay_signature']
            
            # Get order
            try:
                order = Order.objects.get(
                    razorpay_order_id=razorpay_order_id,
                    student=request.user
                )
            except Order.DoesNotExist:
                return Response(
                    {'error': 'Order not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Verify signature
            razorpay_manager = RazorpayPaymentManager()
            is_valid = razorpay_manager.verify_payment(
                razorpay_order_id,
                razorpay_payment_id,
                razorpay_signature
            )
            
            if is_valid:
                with transaction.atomic():
                    # Create payment record
                    payment = Payment.objects.create(
                        order=order,
                        razorpay_payment_id=razorpay_payment_id,
                        razorpay_signature=razorpay_signature,
                        verified=True
                    )
                    
                    # Update order
                    order.status = 'completed'
                    order.razorpay_payment_id = razorpay_payment_id
                    order.completed_at = timezone.now()
                    order.save()
                    
                    # Enroll student in course
                    enrollment, created = Enrollment.objects.get_or_create(
                        student=request.user,
                        course=order.course
                    )
                    
                    # Update course stats
                    if created:
                        order.course.total_students += 1
                        order.course.save()
                
                logger.info(f"Payment verified: {payment.id}")
                
                return Response({
                    'status': 'success',
                    'payment_id': str(payment.id),
                    'order_id': str(order.id),
                    'message': 'Payment successful! You are now enrolled in the course.'
                }, status=status.HTTP_200_OK)
            else:
                with transaction.atomic():
                    order.status = 'failed'
                    order.save()
                
                logger.warning(f"Payment verification failed: {razorpay_order_id}")
                
                return Response(
                    {'error': 'Payment verification failed'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        except Exception as e:
            logger.error(f"Verification error: {str(e)}")
            return Response(
                {'error': 'Verification failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Payment.objects.filter(order__student=self.request.user)
