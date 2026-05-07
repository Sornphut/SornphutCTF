from django.db import models
from django.contrib.auth.models import User

class Score(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lab_id = models.IntegerField()
    points = models.IntegerField(default=0)
    flag = models.CharField(max_length=100, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'lab_id')

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.IntegerField(default=1000)

    def __str__(self):
        return f"{self.user.username} ({self.balance} บาท)"