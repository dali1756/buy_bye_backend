from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework_simplejwt.tokens import RefreshToken
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from .serializers import ProfileSerializer
from .forms import ProfileUpdateForm, PasswordChangeForm, UserRegistrationForm
import os

User = get_user_model()

class ProfileView(generics.RetrieveAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class ProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        try:
            user = request.user
            form = ProfileUpdateForm(data=request.data, user=user, instance=user)
            if form.is_valid():
                updated_user = form.save()
                serializer = ProfileSerializer(updated_user)
                return Response({
                    "message": "個人資料更新成功。",
                    "user": serializer.data
                }, status=status.HTTP_200_OK)
            else:
                # 返回驗證錯誤
                return Response({
                    "error": "資料驗證失敗。",
                    "details": form.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"更新失敗：{str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            form = PasswordChangeForm(user=user, data=request.data)
            if form.is_valid():
                form.save()
                return Response({
                    "message": "密碼修改成功。"
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "error": "密碼修改失敗。",
                    "details": form.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"密碼修改失敗：{str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@method_decorator(csrf_exempt, name="dispatch")
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            form = UserRegistrationForm(data=request.data)
            if form.is_valid():
                user = form.save()
                return Response({
                    "message": "註冊成功。",
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "name": user.name,
                        "username": user.username
                    }
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "error": "註冊失敗",
                    "details": form.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"註冊失敗： {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@method_decorator(csrf_exempt, name="dispatch")
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            email = request.data.get("email")
            password = request.data.get("password")
            if not email or not password:
                return Response({"error": "請輸入正確資料。"}, status=status.HTTP_400_BAD_REQUEST)
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                refresh = RefreshToken.for_user(user)
                return Response({
                    "message": "登入成功。",
                    "user": {
                        "email": user.email,
                        "name": getattr(user, 'name', user.username),
                    },
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh),
                }, status=status.HTTP_200_OK)
            else:
                return Response({"error": "登入失敗，請檢查帳號或密碼。"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@method_decorator(csrf_exempt, name="dispatch")
class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            logout(request)
            return Response({"message": "登出成功。"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Google 登入
class GoogleLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get("token")
        if not token:
            return Response({"error": "沒有 token。"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            info = id_token.verify_oauth2_token(
                token, 
                google_requests.Request(), 
                os.getenv("GOOGLE_CLIENT_ID")
            )
            email = info.get("email")
            name = info.get("name")
            user, created = User.objects.get_or_create(
                email=email, 
                defaults={
                    "username": email,
                    "name": name,
                }
            )
            if created:
                user.set_unusable_password()
                user.save()
            refresh = RefreshToken.for_user(user)
            if created:
                message = "首次登入成功。"
            else:
                message = "登入成功。"
            return Response({
                "message": message,
                "user": {
                    "email": user.email,
                    "name": user.get_display_name(),
                },
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
            })
        except ValueError as e:
            return Response({"error": "此為無效的 Google token。"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
