from django.contrib import admin
from django.urls import path
from labs.views import sql_injection_lab, secure_login, dashboard, xss_lab, xss_lab_secure, csrf_lab, csrf_lab_secure, file_upload_lab, file_upload_secure, idor_lab, idor_lab_secure
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path("dashboard/", dashboard),
    path("admin/", admin.site.urls),
    path("lab1/", sql_injection_lab),
    path("lab1-secure/", secure_login),
    path("lab2/", xss_lab),
    path("lab2-secure/", xss_lab_secure),
    path("lab3/", csrf_lab),
    path("lab3-secure/", csrf_lab_secure),
    path("lab4/", file_upload_lab),
    path("lab4-secure/", file_upload_secure),
    path("lab5/", idor_lab),
    path("lab5-secure/", idor_lab_secure),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
