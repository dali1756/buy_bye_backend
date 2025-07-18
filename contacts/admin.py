from django.contrib import admin
from .models import ContactMessage

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "email", "category", "status", "created_at"]
    list_filter = ["category", "status", "created_at"]
    search_fields = ["first_name", "last_name", "email", "order_number"]
    readonly_fields = ["created_at", "ip_address", "user_agent"]
    list_per_page = 20
    fieldsets = (
        ("客戶資訊", {
            "fields": ("first_name", "last_name", "email", "phone")
        }),
        ("訊息內容", {
            "fields": ("category", "order_number", "message")
        }),
        ("處理狀態", {
            "fields": ("status", "processed_by")
        }),
        ("系統資訊", {
            "fields": ("created_at", "updated_at", "ip_address", "user_agent"),
            "classes": ("collapse",)
        }),
    )
