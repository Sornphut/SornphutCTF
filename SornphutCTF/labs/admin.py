from django.contrib import admin
from .models import Profile, User, Score

admin.site.register(Score)
admin.site.register(Profile)