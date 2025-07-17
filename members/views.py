from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")
        password_confirmation = data.get("passwordConfirmation")
        if not all([name, email, password, password_confirmation]):
            return Response({"error": "尚有欄位未填寫。"}, status=status.HTTP_400_BAD_REQUEST)
        if password != password_confirmation:
            return Response({"error": "密碼不一致。"}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            return Response({"error": "此信箱已被註冊。"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.create_user(username=email, email=email, name=name, password=password)
            print(f"User created: {user}")
            return Response({"message": "註冊成功。"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(f"Error: {e}")
            return Response({"error": f"註冊失敗: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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