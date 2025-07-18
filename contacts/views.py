from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from .serializers import ContactMessageSerializer
from rest_framework.generics import CreateAPIView
import logging

logger = logging.getLogger(__name__)

class ContactSubmitCreateView(CreateAPIView):
    serializer_class = ContactMessageSerializer
    permission_classes = [AllowAny]

    # 取得客戶 IP
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip

    def perform_create(self, serializer):
        contact_message = serializer.save(ip_address=self.get_client_ip(self.request), user_agent=self.request.META.get("HTTP_USER_AGENT", ""))
        try:
            self.send_confirmation_email(contact_message)
        except Exception as e:
            logger.error(f"發送確認郵件失敗：{str(e)}")
        try:
            self.send_notification_email(contact_message)
        except Exception as e:
            logger.error(f"發送通知郵件失敗：{str(e)}")

    def send_confirmation_email(self, contact_message):
        subject = "BuyBye - 我們已收到您的聯絡訊息"
        message = f"""
                親愛的 {contact_message.first_name} {contact_message.last_name}，
                感謝您聯絡 BuyBye 客服！
                我們已收到您的訊息：
                類別：{contact_message.get_category_display()}
                訂單編號：{contact_message.order_number or "無"}
                聯絡電話：{contact_message.phone}
                我們的客服團隊將盡快處理您的問題，預計在 24 小時內回覆。
                如有緊急問題，請直接撥打客服專線：02-1234-5678
                謝謝！
                BuyBye 客服團隊
                """
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[contact_message.email],
            fail_silently=False,
        )

    def send_notification_email(self, contact_message):
        subject = f"新的客服訊息 - {contact_message.get_category_display()}"
        message = f"""
                收到新的客服訊息：
                客戶資訊：
                姓名：{contact_message.first_name} {contact_message.last_name}
                電話：{contact_message.phone}
                信箱：{contact_message.email}
                類別：{contact_message.get_category_display()}
                訂單編號：{contact_message.order_number or "無"}
                訊息內容：
                {contact_message.message}
                IP 位址：{contact_message.ip_address}
                提交時間：{contact_message.created_at.strftime("%Y-%m-%d %H:%M:%S")}
                請盡快處理此訊息。
                """
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.CUSTOMER_SERVICE_EMAIL],
            fail_silently=False,
        )

    def create(self, request, *args, **kwargs):
        try:
            response = super().create(request, *args, **kwargs)
            return Response({
                "success": True,
                "message": "感謝您的聯絡，我們已收到您的訊息，將盡快回覆您！",
                "contact_id": response.data.get("id") if hasattr(response, "data") else None
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"提交聯絡表單錯誤：{str(e)}")
            return Response({
                "success": False,
                "message": "系統錯誤，請稍後再試。"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
