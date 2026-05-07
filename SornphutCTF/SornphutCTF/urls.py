from django.contrib import admin
from django.urls import path
from labs import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("admin/", admin.site.urls),

    # ✅ หน้าแรกเป็น Login
    path("", auth_views.LoginView.as_view(template_name="registration/login.html"), name="home"),
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
    path("signup/", views.signup_view, name="signup"),

    # ✅ Dashboard และ Labs
    path("dashboard/", views.dashboard, name="dashboard"),
    path("leaderboard/", views.leaderboard_view, name="leaderboard"),
    path("lab1/", views.sql_injection_lab, name="lab1"),
    path("lab1-secure/", views.secure_login, name="lab1-secure"),
    path("lab2/", views.xss_lab, name="lab2"),
    path("lab2-secure/", views.xss_lab_secure, name="lab2-secure"),
    path("lab3/", views.csrf_lab, name="lab3"),
    path("lab3-secure/", views.csrf_lab_secure, name="lab3-secure"),
    path("lab4/", views.file_upload_lab, name="lab4"),
    path("lab4-secure/", views.file_upload_secure, name="lab4-secure"),
    path("lab5/", views.idor_lab, name="lab5"),
    path("lab5-secure/", views.idor_lab_secure, name="lab5-secure"),
    path("lab1-info/", views.lab1_info, name="lab1-info"),
    path("lab2-info/", views.lab2_info, name="lab2-info"),
    path("lab3-info/", views.lab3_info, name="lab3-info"),
    path("lab4-info/", views.lab4_info, name="lab4-info"),
    path("lab5-info/", views.lab5_info, name="lab5-info"),
    path("account/", views.account_dashboard, name="account_dashboard"),
]
