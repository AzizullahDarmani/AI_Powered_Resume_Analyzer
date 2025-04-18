from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Job(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    required_skills = models.TextField()
    experience_years = models.IntegerField(default=0)
    location = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class ResumeMatch(models.Model):
    resume = models.ForeignKey('Resume', on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    score = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    matched_skills = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('resume', 'job')

    def __str__(self):
        return f"{self.resume} - {self.job} ({self.score}%)"

class FavoriteJob(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'job')

    def __str__(self):
        return f"{self.user.username} - {self.job.title}"

class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='resumes/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    skills = models.TextField(blank=True)
    experience = models.TextField(blank=True)
    education = models.TextField(blank=True)
    skills_feedback = models.TextField(blank=True)
    format_feedback = models.TextField(blank=True)
    ats_feedback = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username}'s resume"
