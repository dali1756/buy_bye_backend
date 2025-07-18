from django.urls import path
from . import views

urlpatterns = [
    path("submit/", views.ContactSubmitCreateView.as_view(), name="submit_contact"),
]
