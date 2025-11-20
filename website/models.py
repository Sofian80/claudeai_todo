from django.db import models
from django.contrib.auth.models import User

class Todo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='todos')
    date = models.DateField()
    task = models.TextField()
    time = models.TimeField(null=True, blank=True)  # Optional time for hourly scheduling
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date', 'time', 'created_at']

    def __str__(self):
        return f"{self.user.username} - {self.date}: {self.task[:50]}"
