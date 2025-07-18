from rest_framework import serializers
from .models import ContactMessage

class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ["category", "order_number", "first_name", "last_name", "phone", "email", "message"]

    def validate_email(self, value):
        if not value:
            raise serializers.ValidationError("電子郵件為必填欄位。")
        return value

    def validate_phone(self, value):
        import re
        if not re.match(r'^[\d\-\+\(\)\s]+$', value):
            raise serializers.ValidationError("請輸入有效的電話號碼。")
        return value
