from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=255)
    cost = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class Order(models.Model):

    STATUS_CHOICES = [
        ('Order Placed', 'Order Placed'),
        ('Confirmed', 'Confirmed'),
    ]

    order_id = models.CharField(max_length=255, unique=True, editable=False)
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Order Placed')
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order_id} - {self.customer_name}"
    
    def save(self, *args, **kwargs):
        if not self.order_id:
            import random
            self.order_id = f"ORD{random.randint(100000, 999999)}"
            while Order.objects.filter(order_id=self.order_id).exists():
                self.order_id = f"ORD{random.randint(100000, 999999)}"
        super().save(*args, **kwargs)