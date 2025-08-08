from django.db import models
from django.conf import settings
from products.models import Product

class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"cart for {self.user.username}"

    @property
    def total_items(self):
        total = 0
        for item in self.items.all():
            total += item.count
        return total

    @property
    def total_price(self):
        total = 0
        for item in self.items.all():
            total += item.count * item.product.price
        return total

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    count = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("cart", "product")

    def __str__(self):
        return f"{self.count} x {self.product.name}"

    @property
    def subtotal(self):
        return self.count * self.product.price
