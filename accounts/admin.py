
from django.contrib import admin
from .models import Resume, Job, ResumeMatch

admin.site.register(Resume)
admin.site.register(Job)
admin.site.register(ResumeMatch)
