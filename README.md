virtualenv venv
.\venv\Scripts\activate 
django-admin startproject firstweb
cd firstweb
pip install Django 
pip install pillow
python manage.py runserver	# test runserver
python manage.py startapp myapp # create app

python manage.py makemigrations
python manage.py migrate 	# every time config database

python manage.py createsuperuser # create superuser
