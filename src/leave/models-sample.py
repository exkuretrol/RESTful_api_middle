# leave/models.py
from django.db import models

class User(models.Model):
    name = models.CharField(max_length=100)
    is_manager = models.BooleanField(default=False)

class LeaveRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, default='pending')  # 'pending', 'approved', 'rejected'
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)