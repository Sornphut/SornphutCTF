import os
from django.shortcuts import render
from django.http import HttpResponse
from labs.models import User
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from django.conf import settings

def dashboard(request):
    # ตัวอย่างข้อมูลที่จะแสดงใน Dashboard
    labs = [
        {"id": 1, "name": "Lab1 - SQL Injection", "url": "/lab1/"},
        {"id": 2, "name": "Lab1 Secure Version", "url": "/lab1-secure/"},
        {"id": 3, "name": "Lab2 - XSS", "url": "/lab2/"},
        {"id": 4, "name": "Lab2 - XSS Secure", "url": "/lab2-secure/"},
        {"id": 5, "name": "Lab3 - CSRF", "url": "/lab3/"},
        {"id": 6, "name": "Lab3 - CSRF Secure", "url": "/lab3-secure/"},
        {"id": 7, "name": "Lab4 - File Upload", "url": "/lab4/"},
        {"id": 8, "name": "Lab4 - File Upload Secure", "url": "/lab4-secure/"},
        {"id": 9, "name": "Lab5 - IDOR", "url": "/lab5/"},
        {"id": 10, "name": "Lab5 - IDOR Secure", "url": "/lab5-secure/"},
    ]
    return render(request, "labs/dashboard.html", {"labs": labs})
# ✅ Secure Version (ORM + CSRF)
def secure_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # ✅ ใช้ ORM ตรวจสอบ username และ password
        user = User.objects.filter(username=username, password=password).first()

        if user:
            return HttpResponse("Login สำเร็จ! 🎉")
        else:
            return HttpResponse("Login ไม่ผ่าน ❌ (Username หรือ Password ผิด)")

    return render(request, "labs/login.html")

# ❌ Vulnerable Version (raw SQL, exempt CSRF)
@csrf_exempt
def sql_injection_lab(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        query = f"SELECT * FROM labs_user WHERE username = '{username}' AND password = '{password}'"
        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()

        if result:
            return HttpResponse("Login Successful! (Vulnerable)")
        else:
            return HttpResponse("Login Failed! (Vulnerable)")

    return render(request, "labs/login.html")

@csrf_exempt
def xss_lab(request):
    if request.method == "POST":
        comment = request.POST.get("comment", "")
        # ❌ ไม่ sanitize → เสี่ยง XSS
        return HttpResponse(f"คุณพิมพ์ว่า: {comment}")

    return HttpResponse("""
        <h1>Lab2: XSS</h1>
        <form method='post'>
            Comment: <input name='comment'><br>
            <button type='submit'>Submit</button>
        </form>
    """)

def xss_lab_secure(request):
    comment = ""
    if request.method == "POST":
        comment = request.POST.get("comment", "")
    return render(request, "labs/xss_secure.html", {"comment": comment})
#lab3@csrf_exempt
@csrf_exempt
def csrf_lab(request):
    if request.method == "POST":
        return HttpResponse("การทำงานสำเร็จ! (แต่เสี่ยง CSRF)")
    return HttpResponse("""
        <h1>Lab3: CSRF</h1>
        <form method='post'>
            <button type='submit'>โอนเงิน 100 บาท</button>
        </form>
    """)
#lab3_secure
def csrf_lab_secure(request):
    if request.method == "POST":
        return HttpResponse("การทำงานสำเร็จ! (Secure)")
    return render(request, "labs/csrf_secure.html")
#lab4_file_upload
UPLOAD_DIR = "uploads/"

@csrf_exempt
def file_upload_lab(request):
    if request.method == "POST" and request.FILES.get("file"):
        uploaded_file = request.FILES["file"]

        # ✅ ชี้ไปที่โฟลเดอร์ uploads/
        fs = FileSystemStorage(location=settings.MEDIA_ROOT)
        filename = fs.save(uploaded_file.name, uploaded_file)

        return HttpResponse(f"อัปโหลดสำเร็จ! (Vulnerable) → {filename}")

    return HttpResponse("""
        <h1>Lab4: File Upload Vulnerability</h1>
        <form method='post' enctype='multipart/form-data'>
            <input type='file' name='file'><br>
            <button type='submit'>Upload</button>
        </form>
    """)
#lab4_secure_file_upload
def file_upload_secure(request):
    if request.method == "POST" and request.FILES.get("file"):
        uploaded_file = request.FILES["file"]
        allowed_extensions = [".jpg", ".png", ".gif"]
        ext = os.path.splitext(uploaded_file.name)[1].lower()
        if ext not in allowed_extensions:
            return HttpResponse("❌ ไม่อนุญาตให้อัปโหลดไฟล์นี้ (Secure)")

        fs = FileSystemStorage(location=settings.MEDIA_ROOT)
        filename = fs.save(uploaded_file.name, uploaded_file)
        return HttpResponse(f"✅ อัปโหลดสำเร็จ! (Secure) → {filename}")

    # ✅ ใช้ render เพื่อให้ Django ประมวลผล {% csrf_token %}
    return render(request, "labs/file_upload_secure.html")
#lab5_idor
def idor_lab(request):
    user_id = request.GET.get("id", "1")
    try:
        user = User.objects.get(id=user_id)
        return HttpResponse(f"ข้อมูลผู้ใช้: {user.username} (Vulnerable)")
    except User.DoesNotExist:
        return HttpResponse("ไม่พบผู้ใช้")
#lab5_idor_secure
def idor_lab_secure(request):
    if not request.user.is_authenticated:
        return HttpResponse("กรุณา Login ก่อนเข้าถึงข้อมูล")

    user = request.user
    return HttpResponse(f"ข้อมูลผู้ใช้ของคุณ: {user.username} (Secure)")
