from django.urls import path
from .views import OrderViewSet

urlpatterns = [
    path('orders/', OrderViewSet.as_view({'get': 'list'}), name='order-list'),
    path('orders/create/', OrderViewSet.as_view({'post': 'create_order'}), name='create-order'),
    path('orders/verify/', OrderViewSet.as_view({'post': 'verify_payment'}), name='verify-payment'),
]
