
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.contrib import messages

from django.contrib.auth.forms import UserCreationForm
from django import forms

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

import os
from PyPDF2 import PdfReader
from docx import Document
import magic

@login_required
def profile(request):
    if request.method == 'POST' and request.FILES.get('resume'):
        file = request.FILES['resume']
        
        # Validate file type
        mime = magic.Magic(mime=True)
        file_type = mime.from_buffer(file.read(1024))
        file.seek(0)  # Reset file pointer
        
        if file_type not in ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
            messages.error(request, 'Please upload only PDF or DOCX files.')
            return redirect('profile')
        
        # Create resume object
        resume = Resume.objects.create(user=request.user, file=file)
        
        # Extract text based on file type
        if file_type == 'application/pdf':
            pdf = PdfReader(file)
            text = ""
            for page in pdf.pages:
                text += page.extract_text()
        else:
            doc = Document(file)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        
        # Simple AI extraction (placeholder - you can enhance this)
        skills = extract_skills(text)
        experience = extract_experience(text)
        education = extract_education(text)
        
        # Update resume with extracted information
        resume.skills = skills
        resume.experience = experience
        resume.education = education
        resume.save()
        
        messages.success(request, 'Resume uploaded and processed successfully!')
        return redirect('profile')
    
    resumes = Resume.objects.filter(user=request.user).order_by('-uploaded_at')
    return render(request, 'accounts/profile.html', {'resumes': resumes})

def extract_skills(text):
    # Placeholder - implement more sophisticated extraction
    common_skills = ['python', 'java', 'javascript', 'html', 'css', 'react', 'django']
    found_skills = [skill for skill in common_skills if skill.lower() in text.lower()]
    return ", ".join(found_skills)

def extract_experience(text):
    # Placeholder - implement more sophisticated extraction
    return "Experience extracted from resume"

def extract_education(text):
    # Placeholder - implement more sophisticated extraction
    return "Education extracted from resume"
