from django.db import models
from django.utils import timezone
from core.models import User, Address
from shops.models import Shop, Product

class Order(models.Model):
    STATUS_CHOICES = (
        ('placed', 'Placed'),
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('preparing', 'Preparing'),
        ('ready_to_deliver', 'Ready to Deliver'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('failed', 'Failed'),
    )
    VALID_STATUS_TRANSITIONS = {
        'placed': ['pending', 'cancelled'],  
        'pending': ['confirmed', 'cancelled'],
        'confirmed': ['preparing', 'cancelled'],
        'preparing': ['ready_to_deliver', 'cancelled'],
        'ready_to_deliver': ['out_for_delivery', 'cancelled'],
        'out_for_delivery': ['delivered', 'cancelled'],
        'delivered': [],
        'cancelled': [],
        'failed': []
    }

    PAYMENT_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    ]

    PAYMENT_METHOD_CHOICES = [
        ("cod", "Cash on Delivery"),
        ("upi", "UPI"),
        ("card", "Credit/Debit Card"),
    ]

    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
        
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders", default=1)
    # order_number = models.CharField(max_length=50, unique=True)
    order_number = models.CharField(max_length=50, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default="pending")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True, null=True)
    status_changed_at = models.DateTimeField(blank=True, null=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    delivery_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    is_cancelled_by = models.CharField(max_length=20, blank=True, null=True)  # customer/shopkeeper
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} from {self.shop.name} - {self.status}"

    def save(self, *args, **kwargs):
        if self.pk:  # only on update
            old_status = Order.objects.get(pk=self.pk).status
            if old_status != self.status:
                self.status_changed_at = timezone.now()
        super().save(*args, **kwargs)

    # def __str__(self):
    #     return self.order_number

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # snapshot
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.total_price = self.price * self.quantity
        super().save(*args, **kwargs)

    # def __str__(self):
    #     return f"{self.product.name} ({self.order.order_number})"

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order #{self.order.id})"


