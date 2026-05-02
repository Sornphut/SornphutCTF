📄 ตัวอย่าง README.md
markdown
# SornphutCTF / FirstWeb

โปรเจกต์ Django สำหรับการเรียนรู้และสร้าง Web Application เบื้องต้น พร้อม Labs ด้าน Security (SQL Injection, XSS, CSRF, File Upload, IDOR)

---

## 🚀 การเริ่มต้นใช้งาน

### 1. สร้าง Virtual Environment
```bash
virtualenv venv
.\venv\Scripts\activate
2. ติดตั้ง Django และ Pillow
bash
pip install Django
pip install pillow
3. สร้าง Project และ App
bash
django-admin startproject firstweb
cd firstweb
python manage.py startapp myapp
4. ตั้งค่า Database
ทุกครั้งที่มีการแก้ไข models ให้รัน:

bash
python manage.py makemigrations
python manage.py migrate
5. สร้าง Superuser
เพื่อเข้าใช้งาน Django Admin:

bash
python manage.py createsuperuser
6. รัน Server
bash
python manage.py runserver
เปิดเบราว์เซอร์ไปที่:
http://127.0.0.1:8000/
