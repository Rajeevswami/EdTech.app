from rest_framework import serializers
from .models import Order, Payment

class OrderSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    course_price = serializers.IntegerField(source='course.price', read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'course', 'course_title', 'course_price', 'amount', 'status', 'created_at', 'completed_at']
        read_only_fields = ['id', 'created_at', 'completed_at']


class PaymentSerializer(serializers.ModelSerializer):
    order_details = OrderSerializer(source='order', read_only=True)
    
    class Meta:
        model = Payment
        fields = ['id', 'order', 'order_details', 'razorpay_payment_id', 'method', 'verified', 'created_at']
        read_only_fields = ['id', 'created_at']


class CreateOrderSerializer(serializers.Serializer):
    course_id = serializers.UUIDField()
    
    def validate_course_id(self, value):
        from courses.models import Course
        try:
            Course.objects.get(id=value)
        except Course.DoesNotExist:
            raise serializers.ValidationError("Course not found")
        return value


class VerifyPaymentSerializer(serializers.Serializer):
    razorpay_order_id = serializers.CharField()
    razorpay_payment_id = serializers.CharField()
    razorpay_signature = serializers.CharField()
