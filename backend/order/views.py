from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Product, Order
from .serializers import ProductSerializer, OrderSerializer
from django.core.mail import send_mail
from django.conf import settings


class ProductListView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class OrderCreateView(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def perform_create(self, serializer):
        order = serializer.save()
    
        confirm_url = f"{settings.FRONTEND_URL}/confirm-order/{order.id}/"
        
        send_mail(
            subject='Order Confirmation',
            message=(
                f"Dear {order.customer_name},\n\n"
                f"Your order details:\n"
                f"Order ID: {order.order_id}\n"
                f"Product: {order.product.name}\n"
                f"Quantity: {order.quantity}\n"
                f"Total Cost: {order.total_cost}\n\n"
                f"Please confirm your order by clicking the button below:\n"
                f"Confirm Order: {confirm_url}"
            ),
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[order.customer_email],
            html_message=(
                f"<p>Dear {order.customer_name},</p>"
                f"<p>Your order details:</p>"
                f"<ul>"
                f"<li>Order ID: {order.order_id}</li>"
                f"<li>Product: {order.product.name}</li>"
                f"<li>Quantity: {order.quantity}</li>"
                f"<li>Total Cost: {order.total_cost}</li>"
                f"</ul>"
                f'<p><a href="{confirm_url}" style="padding: 10px; background-color: #28a745; color: white; text-decoration: none;">Confirm Order</a></p>'
            ),
        )

class OrderDetailView(generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    lookup_field = 'id'

class ConfirmOrderView(APIView):
    def post(self, request, order_id):
       
        try:
            order = Order.objects.get(id=order_id, status='Order Placed')
            admin_email = settings.EMAIL_HOST_USER

            send_mail(
                subject=f'Order Confirmation Received - Order {order.order_id}',
                message=(
                    f"Order confirmation received:\n"
                    f"Order ID: {order.order_id}\n"
                    f"Customer: {order.customer_name}\n"
                    f"Product: {order.product.name}\n"
                    f"Quantity: {order.quantity}\n"
                    f"Total Cost: {order.total_cost}\n"
                    f"Customer Email: {order.customer_email}"
                ),
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[admin_email],
                html_message=(
                    f"<p>We are pleased to confirm the order:</p>"
                    f"<ul>"
                    f"<li>Order ID: {order.order_id}</li>"
                    f"<li>Customer: {order.customer_name}</li>"
                    f"<li>Product: {order.product.name}</li>"
                    f"<li>Quantity: {order.quantity}</li>"
                    f"<li>Total Cost: {order.total_cost}</li>"
                    f"<li>Customer Email: {order.customer_email}</li>"
                    f"</ul>"
                    f"<p>Order successfully confirmed.</p>"
                ),
            )
            return Response({'message': f'Order {order.order_id} confirmed successfully.'}, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found or already confirmed'}, status=status.HTTP_404_NOT_FOUND)