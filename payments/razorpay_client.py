import razorpay
from django.conf import settings
import logging
import hmac
import hashlib

logger = logging.getLogger(__name__)

class RazorpayPaymentManager:
    def __init__(self):
        self.client = razorpay.Client(
            auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET
            )
        )
    
    def create_order(self, course_id, amount, user_id):
        """
        Create Razorpay order
        amount: in INR
        """
        try:
            order_data = {
                'amount': amount * 100,  # Convert to paise
                'currency': 'INR',
                'receipt': f'course_{course_id}_user_{user_id}',
                'notes': {
                    'course_id': str(course_id),
                    'user_id': str(user_id)
                }
            }
            
            order = self.client.order.create(data=order_data)
            logger.info(f"Order created: {order['id']}")
            return order
        
        except Exception as e:
            logger.error(f"Order creation failed: {str(e)}")
            raise
    
    def verify_payment(self, razorpay_order_id, razorpay_payment_id, razorpay_signature):
        """
        Verify payment signature
        """
        try:
            self.client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            })
            logger.info(f"Payment verified: {razorpay_payment_id}")
            return True
        except Exception as e:
            logger.error(f"Payment verification failed: {str(e)}")
            return False
    
    def refund_payment(self, payment_id, amount=None):
        """
        Refund a payment
        amount: optional, in paise
        """
        try:
            refund_data = {}
            if amount:
                refund_data['amount'] = amount
            
            refund = self.client.payment.refund(payment_id, refund_data)
            logger.info(f"Refund created: {refund['id']}")
            return refund
        except Exception as e:
            logger.error(f"Refund failed: {str(e)}")
            raise
    
    def get_payment_details(self, payment_id):
        """Get payment details from Razorpay"""
        try:
            payment = self.client.payment.fetch(payment_id)
            return payment
        except Exception as e:
            logger.error(f"Failed to fetch payment: {str(e)}")
            raise
