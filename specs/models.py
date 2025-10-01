from django.db import models

# Add models here if you want to persist spec data, processing runs, etc.

class ProcessingRun(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    input_filename = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=50, default='pending')

    def __str__(self):
        return f"Run {self.id} - {self.status}"
