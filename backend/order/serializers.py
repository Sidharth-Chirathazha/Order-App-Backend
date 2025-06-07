from rest_framework import serializers
from .models import Product,Order

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id','name','cost']

class OrderSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )
    class Meta:
        model = Order
        fields = ['id', 'order_id', 'customer_name', 'quantity', 'product', 'product_id', 'total_cost', 'customer_email', 'status']