from django.contrib import admin
from .models import ProcessingRun

@admin.register(ProcessingRun)
class ProcessingRunAdmin(admin.ModelAdmin):
    list_display = ('id', 'input_filename', 'status', 'created_at')
