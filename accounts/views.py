
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Resume

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
    # More comprehensive list of technical skills
    technical_skills = [
        'python', 'java', 'javascript', 'html', 'css', 'react', 'django',
        'sql', 'postgresql', 'mysql', 'mongodb', 'docker', 'kubernetes',
        'aws', 'azure', 'git', 'nodejs', 'express', 'flask', 'spring',
        'typescript', 'angular', 'vue', 'php', 'laravel', 'ruby', 'rails'
    ]
    
    # Soft skills
    soft_skills = [
        'leadership', 'communication', 'teamwork', 'problem solving',
        'analytical', 'project management', 'time management',
        'critical thinking', 'creativity', 'collaboration'
    ]
    
    found_tech_skills = [skill for skill in technical_skills if skill.lower() in text.lower()]
    found_soft_skills = [skill for skill in soft_skills if skill.lower() in text.lower()]
    
    all_skills = found_tech_skills + found_soft_skills
    return ", ".join(all_skills) if all_skills else "No specific skills detected"

def extract_experience(text):
    # Look for common experience patterns
    import re
    
    # Look for date patterns and job titles
    experience_patterns = [
        r'\b(19|20)\d{2}\s*[-–]\s*(19|20)\d{2}|present|current\b',
        r'\b(senior|junior|lead|principal|software|developer|engineer|manager|director)\b'
    ]
    
    experiences = []
    for pattern in experience_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            # Get the surrounding context (100 characters)
            start = max(0, match.start() - 50)
            end = min(len(text), match.end() + 50)
            context = text[start:end].strip()
            experiences.append(context)
    
    return "\n".join(experiences) if experiences else "No specific experience detected"

def extract_education(text):
    # Look for education-related keywords
    import re
    
    education_patterns = [
        r'\b(bachelor|master|phd|bsc|msc|ba|bs|ma|ms|doctorate|degree)\b',
        r'\b(university|college|institute|school)\b',
        r'\b(19|20)\d{2}\s*[-–]\s*(19|20)\d{2}|present|current\b'
    ]
    
    education = []
    for pattern in education_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            # Get the surrounding context (100 characters)
            start = max(0, match.start() - 50)
            end = min(len(text), match.end() + 50)
            context = text[start:end].strip()
            education.append(context)
    
    return "\n".join(education) if education else "No specific education detected"
