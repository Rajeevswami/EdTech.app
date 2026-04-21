from django.contrib import admin
from .models import Order, Payment

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('razorpay_order_id', 'student', 'course', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'course')
    search_fields = ('razorpay_order_id', 'student__username', 'course__title')
    readonly_fields = ('created_at', 'completed_at')
    fieldsets = (
        ('Order Info', {
            'fields': ('student', 'course', 'amount')
        }),
        ('Razorpay', {
            'fields': ('razorpay_order_id', 'razorpay_payment_id')
        }),
        ('Status', {
            'fields': ('status', 'created_at', 'completed_at')
        }),
    )

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('razorpay_payment_id', 'order', 'method', 'verified', 'created_at')
    list_filter = ('verified', 'method', 'created_at')
    search_fields = ('razorpay_payment_id', 'order__razorpay_order_id')
    readonly_fields = ('created_at',)
