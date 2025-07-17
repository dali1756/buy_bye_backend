from django.contrib.auth.models import AbstractUser
from django.db import models

class Member(AbstractUser):
    GENDER_CHOICES = [
        ("M", "男性"),
        ("F", "女性"),
        ("O", "其他"),
    ]

    name = models.CharField(max_length=50, null=False)
    email = models.EmailField(unique=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "name"]
    
    class Meta:
        verbose_name = "使用者"
        verbose_name_plural = "使用者"
        db_table = "members_member"

    def __str__(self):
        return f"{self.email} ({self.name or self.username})"

    def get_full_name(self):
        return self.name or self.username

    def get_display_name(self):
        return self.name or self.username