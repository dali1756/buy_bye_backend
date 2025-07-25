from django.urls import path
from .views import LoginView, LogoutView, RegisterView, GoogleLoginView, ProfileView, ProfileUpdateView, PasswordChangeView

app_name = "members"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    # google login
    path("google-login/", GoogleLoginView.as_view(), name="google-login"),
    # profile
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/update/", ProfileUpdateView.as_view(), name="profile-update"),
    path("profile/change-password/", PasswordChangeView.as_view(), name="change-password"),
]
