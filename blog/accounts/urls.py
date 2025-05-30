from django.urls import path

from . import views

app_name = "accounts"
urlpatterns = [
    # auth
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.instant_logout, name="logout"),
    path("signup/", views.SignUpView.as_view(), name="signup"),
    # profile
    path("profile/", views.profile, name="profile"),
    path("update-email/", views.update_email, name="update_email"),
]
