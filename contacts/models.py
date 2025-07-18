from django.db import models
from django.utils import timezone

class ContactMessage(models.Model):
    CATEGORY_CHOICES = [
        ("order", "訂單問題"),
        ("product", "商品問題"),
        ("payment", "付款問題"),
        ("shipping", "配送問題"),
        ("return", "退換貨"),
        ("account", "帳戶問題"),
        ("other", "其他"),
    ]

    STATUS_CHOICES = [
        ("pending", "待處理"),
        ('processing', "處理中"),
        ("resolved", "已解決"),
        ("closed", "已關閉"),
    ]

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    order_number = models.CharField(max_length=100, blank=True, null=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    processed_by = models.ForeignKey("members.Member", on_delete=models.SET_NULL, null=True, blank=True, related_name="processed_contacts")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.get_category_display()}"
