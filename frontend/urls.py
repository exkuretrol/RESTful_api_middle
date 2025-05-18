from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from frontend import views

app_name = "frontend"

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("", views.LeaveRequestsView.as_view(), name="home"),
]
