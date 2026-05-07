import os
from django.shortcuts import render
from django.http import HttpResponse
from labs.models import Score, User
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Profile, Score
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.db.models.signals import post_save
from django.dispatch import receiver

@login_required
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

    return render(request, "labs/sql_injection_login.html")

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
            return HttpResponse("Login Successful! (Vulnerable) FLAG{SQL_INJECTION_SUCCESS}")
        else:
            return HttpResponse("Login Failed! (Vulnerable)")

    return render(request, "labs/sql_injection_login.html")

@csrf_exempt
def xss_lab(request):
    comments = []
    flag = None
    if request.method == "POST":
        comment = request.POST.get("comment", "")
        comments.append(comment)
        # ถ้ามี script tag → ถือว่าทำ XSS สำเร็จ
        if "<script>" in comment.lower():
            flag = "FLAG{XSS_SUCCESS}"
    return render(request, "labs/lab2.html", {"comments": comments, "flag": flag})


# Lab2 Secure
def xss_lab_secure(request):
    comments = []
    if request.method == "POST":
        comment = request.POST.get("comment", "")
        comments.append(comment)  # ✅ Django auto-escape → ปลอดภัย
    return render(request, "labs/lab2_secure.html", {"comments": comments})

# Lab3 Vulnerable
@csrf_exempt
@login_required
def csrf_lab(request):
    message = None
    users = User.objects.exclude(id=request.user.id)
    profile = request.user.profile

    if request.method == "POST":
        to_user = request.POST.get("to_user")
        amount = int(request.POST.get("amount", 0))
        action = request.POST.get("action")

        try:
            target = User.objects.get(username=to_user)
            if action == "transfer":
                profile.balance -= amount
                target.profile.balance += amount
                message = f"โอน {amount} บาทไปยัง {to_user} สำเร็จ (Vulnerable)"
            elif action == "withdraw":
                profile.balance -= amount
                message = f"ถอนเงิน {amount} บาทสำเร็จ (Vulnerable)"
            profile.save()
            target.profile.save()
        except Exception as e:
            message = f"เกิดข้อผิดพลาด: {e}"

    return render(request, "labs/lab3.html", {"users": users, "profile": profile, "message": message})

# Lab3 Secure
@login_required
def csrf_lab_secure(request):
    message = None
    users = User.objects.exclude(id=request.user.id)
    profile, _ = Profile.objects.get_or_create(user=request.user)  # ✅ ป้องกัน error

    if request.method == "POST":
        to_user = request.POST.get("to_user")
        amount = int(request.POST.get("amount", 0))
        action = request.POST.get("action")

        try:
            target = User.objects.get(username=to_user)
            target_profile, _ = Profile.objects.get_or_create(user=target)  # ✅ ป้องกัน error

            if action == "transfer":
                profile.balance -= amount
                target_profile.balance += amount
                message = f"โอน {amount} บาทไปยัง {to_user} สำเร็จ (Secure)"
            elif action == "withdraw":
                profile.balance -= amount
                message = f"ถอนเงิน {amount} บาทสำเร็จ (Secure)"
            profile.save()
            target_profile.save()
        except Exception as e:
            message = f"เกิดข้อผิดพลาด: {e}"

    return render(request, "labs/csrf_secure.html", {"users": users, "profile": profile, "message": message})
#receiver สร้าง Profile อัตโนมัติเมื่อมี User ใหม่ถูกสร้างขึ้นมา
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@login_required
def account_dashboard(request):
    profile = request.user.profile
    return render(request, "labs/account_dashboard.html", {"profile": profile})

#tranfer money (vulnerable to CSRF)
@login_required
def transfer(request):
    message = None
    if request.method == "POST":
        to_user = request.POST.get("to_user")
        amount = int(request.POST.get("amount"))

        # ❌ ไม่มี CSRF protection → เสี่ยงโจมตี
        try:
            target = User.objects.get(username=to_user)
            request.user.profile.balance -= amount
            target.profile.balance += amount
            request.user.profile.save()
            target.profile.save()
            message = f"โอน {amount} บาท ไปยัง {to_user} สำเร็จ"
        except:
            message = "ไม่พบผู้ใช้ปลายทาง"

    return render(request, "labs/lab3.html", {"message": message})

#lab4_file_upload
UPLOAD_DIR = "uploads/"

@csrf_exempt
def file_upload_lab(request):
    if request.method == "POST" and request.FILES.get("file"):
        uploaded_file = request.FILES["file"]

        # ✅ ชี้ไปที่โฟลเดอร์ uploads/
        fs = FileSystemStorage(location=settings.MEDIA_ROOT)
        filename = fs.save(uploaded_file.name, uploaded_file)

        # เมื่ออัปโหลดไฟล์สำเร็จ → โชว์ flag โดยตรง
        return HttpResponse(f"""
            <h1>Lab4: File Upload Vulnerability</h1>
            <p>✅ อัปโหลดสำเร็จ! (Vulnerable) → {filename}</p>
            <div style="margin-top:20px; padding:10px; background:#ffeb3b;">
                FLAG{{FILE_UPLOAD_SUCCESS}}
            </div>
        """)

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

        # ถ้า user_id = 5 → โชว์ flag
        if str(user.id) == "5":
            return HttpResponse("🎯 FLAG{IDOR_SUCCESS}")

        return HttpResponse(f"ข้อมูลผู้ใช้: {user.username} (Vulnerable)")
    except User.DoesNotExist:
        return HttpResponse("ไม่พบผู้ใช้")

#lab5_idor_secure
def idor_lab_secure(request):
    if not request.user.is_authenticated:
        return HttpResponse("กรุณา Login ก่อนเข้าถึงข้อมูล")

    user = request.user
    return HttpResponse(f"ข้อมูลผู้ใช้ของคุณ: {user.username} (Secure)")
#leaderboard
def leaderboard_view(request):
    leaderboard = (
        Score.objects.values("user__username")
        .annotate(total=Sum("points"))
        .order_by("-total")
    )
    return render(request, "labs/leaderboard.html", {"leaderboard": leaderboard})
#login_required
@login_required
def dashboard(request):
    # แสดง lab และคะแนนของ user ที่ login อยู่
    return render(request, "labs/dashboard.html")
#signup view

def signup_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")  # หลังสมัครเสร็จกลับไปหน้า login
    else:
        form = UserCreationForm()
    return render(request, "registration/signup.html", {"form": form})
#lab_info
def lab1_info(request):
    if request.method == "POST":
        flag = request.POST.get("flag")
        correct_flag = "FLAG{SQL_INJECTION_SUCCESS}"  # ตัวอย่าง flag ของ Lab1

        if flag == correct_flag:
            # บันทึกคะแนน
            Score.objects.update_or_create(
                user=request.user,
                lab_id=1,
                defaults={"points": 100, "flag": flag}
            )
            return HttpResponse("🎉 ถูกต้อง! คุณได้ 100 คะแนน")
        else:
            return HttpResponse("❌ Flag ไม่ถูกต้อง")

    # ถ้าเป็น GET → แสดงหน้า info ตามปกติ
    return render(request, "labs/lab1_info.html")

def lab2_info(request):
    message = None
    if request.method == "POST":
        flag = request.POST.get("flag")
        correct_flag = "FLAG{XSS_SUCCESS}"
        if flag == correct_flag:
            Score.objects.update_or_create(
                user=request.user,
                lab_id=2,
                defaults={"points": 100, "flag": flag}
            )
            message = "🎉 ถูกต้อง! คุณได้ 100 คะแนน"
        else:
            message = "❌ Flag ไม่ถูกต้อง"
    return render(request, "labs/lab2_info.html", {"message": message})

@login_required
def lab3_info(request):
    message = None
    if request.method == "POST":
        flag = request.POST.get("flag")
        correct_flag = "FLAG{CSRF_VULNERABLE_SUCCESS}"
        if flag == correct_flag:
            Score.objects.update_or_create(
                user=request.user,
                lab_id=3,
                defaults={"points": 100, "flag": flag}
            )
            message = "🎉 ถูกต้อง! คุณได้ 100 คะแนน"
        else:
            message = "❌ Flag ไม่ถูกต้อง" 
    return render(request, "labs/lab3_info.html", {"message": message})

@login_required
def lab4_info(request):
    message = None
    if request.method == "POST":
        flag = request.POST.get("flag")
        correct_flag = "FLAG{FILE_UPLOAD_SUCCESS}"
        if flag == correct_flag:
            Score.objects.update_or_create(
                user=request.user,
                lab_id=4,
                defaults={"points": 100, "flag": flag}
            )
            message = "🎉 ถูกต้อง! คุณได้ 100 คะแนน"
        else:
            message = "❌ Flag ไม่ถูกต้อง"
    return render(request, "labs/lab4_info.html", {"message": message})


def lab5_info(request):
    message = None
    if request.method == "POST":
        flag = request.POST.get("flag")
        correct_flag = "FLAG{IDOR_SUCCESS}"
        if flag == correct_flag:
            Score.objects.update_or_create(
                user=request.user,
                lab_id=5,
                defaults={"points": 100, "flag": flag}
            )
            message = "🎉 ถูกต้อง! คุณได้ 100 คะแนน"
        else:
            message = "❌ Flag ไม่ถูกต้อง"
    return render(request, "labs/lab5_info.html", {"message": message})

