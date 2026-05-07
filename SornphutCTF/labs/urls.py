# labs/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("leaderboard/", views.leaderboard_view, name="leaderboard"),
    path("lab1/", views.sql_injection_lab, name="lab1"),
    path("lab1-secure/", views.secure_login, name="lab1-secure"),
    path("lab2/", views.xss_lab, name="lab2"),
    path("lab2-secure/", views.xss_lab_secure, name="lab2-secure"),
    path("lab3/", views.csrf_lab, name="lab3"),
    path("lab3-transfer/", views.transfer, name="transfer"),
    path("lab3-secure/", views.csrf_lab_secure, name="csrf_lab_secure"),
    path("lab4/", views.file_upload_lab, name="lab4"),
    path("lab4-secure/", views.file_upload_secure, name="lab4-secure"),
    path("lab5/", views.idor_lab, name="lab5"),
    path("lab5-secure/", views.idor_lab_secure, name="lab5-secure"),
]
