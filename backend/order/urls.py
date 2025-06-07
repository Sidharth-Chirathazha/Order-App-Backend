from django.urls import path
from .views import ProductListView, OrderCreateView, ConfirmOrderView,OrderDetailView

urlpatterns = [
    path('products/', ProductListView.as_view(), name='product-list'),
    path('orders/', OrderCreateView.as_view(), name='order-create'),
    path('orders/<int:id>/', OrderDetailView.as_view(), name='order-detail'),
    path('confirm-order/<int:order_id>/', ConfirmOrderView.as_view(), name='confirm-order'),
]