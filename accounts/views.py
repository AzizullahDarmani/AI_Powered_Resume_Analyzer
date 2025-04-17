
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
    import re
    
    # Expanded technical skills with categories
    skill_categories = {
        'Programming Languages': [
            'python', 'java', 'javascript', 'typescript', 'c\\+\\+', 'ruby', 'php',
            'scala', 'kotlin', 'swift', 'rust', 'go', 'perl', 'r'
        ],
        'Web Technologies': [
            'html', 'css', 'react', 'angular', 'vue', 'django', 'flask',
            'node\\.?js', 'express', 'spring', 'laravel', 'bootstrap',
            'jquery', 'webpack', 'sass', 'less'
        ],
        'Databases': [
            'sql', 'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch',
            'cassandra', 'oracle', 'sqlite', 'graphql', 'firebase'
        ],
        'DevOps & Tools': [
            'git', 'docker', 'kubernetes', 'jenkins', 'aws', 'azure',
            'gcp', 'terraform', 'ansible', 'circleci', 'travis'
        ],
        'Soft Skills': [
            'leadership', 'communication', 'teamwork', 'problem[- ]solving',
            'analytical', 'project management', 'time management',
            'critical thinking', 'creativity', 'collaboration'
        ]
    }
    
    found_skills = {}
    for category, skills in skill_categories.items():
        pattern = '|'.join(f"\\b{skill}\\b" for skill in skills)
        matches = re.finditer(pattern, text.lower())
        found = sorted(set(match.group() for match in matches))
        if found:
            found_skills[category] = found
    
    # Format the output
    output = []
    for category, skills in found_skills.items():
        output.append(f"{category}: {', '.join(skills)}")
    
    return "\n".join(output) if output else "No specific skills detected"

def extract_experience(text):
    import re
    from datetime import datetime
    
    # Enhanced patterns for experience extraction
    job_title_pattern = r'\b(senior|junior|lead|principal|software|developer|engineer|manager|director|intern|consultant|architect|analyst|specialist)\b'
    company_patterns = [
        r'at\s+([A-Z][A-Za-z0-9\s&]+(?:Inc\.|LLC|Ltd\.?|GmbH|Corp\.?|Limited|Company)?)',
        r'([A-Z][A-Za-z0-9\s&]+(?:Inc\.|LLC|Ltd\.?|GmbH|Corp\.?|Limited|Company)?)\s*[-–]\s*(?:' + job_title_pattern + ')',
    ]
    date_pattern = r'\b(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*)?(?:19|20)\d{2}\b'
    
    experiences = []
    
    # Find job titles with surrounding context
    for match in re.finditer(job_title_pattern, text, re.IGNORECASE):
        # Get larger context (200 characters)
        start = max(0, match.start() - 100)
        end = min(len(text), match.end() + 100)
        context = text[start:end].strip()
        
        # Look for dates in the context
        dates = re.findall(date_pattern, context)
        # Look for company names
        company = None
        for pattern in company_patterns:
            company_match = re.search(pattern, context)
            if company_match:
                company = company_match.group(1)
                break
        
        experience = {
            'title': match.group(),
            'company': company,
            'dates': dates,
            'context': context
        }
        experiences.append(experience)
    
    # Format the output
    formatted_experiences = []
    for exp in experiences:
        entry = []
        if exp['title']:
            entry.append(f"Position: {exp['title'].title()}")
        if exp['company']:
            entry.append(f"Company: {exp['company'].strip()}")
        if exp['dates']:
            entry.append(f"Period: {' - '.join(exp['dates'])}")
        entry.append(f"Details: {exp['context']}")
        formatted_experiences.append("\n".join(entry))
    
    return "\n\n".join(formatted_experiences) if formatted_experiences else "No specific experience detected"

def extract_education(text):
    import re
    
    # Enhanced patterns for education extraction
    education_patterns = {
        'degree': r'\b(Bachelor|Master|PhD|BSc|MSc|BA|BS|MA|MS|Doctorate|Associate)\s*(?:of|in|\'s)?\s*(?:Science|Arts|Engineering|Business|[A-Za-z]+)?\b',
        'field': r'\b(Computer Science|Information Technology|Software Engineering|Business Administration|Data Science|Mathematics|Physics|Engineering)\b',
        'university': r'\b([A-Z][A-Za-z\s&]+(?:University|College|Institute|School|Academy))\b',
        'year': r'\b(19|20)\d{2}\b'
    }
    
    education_entries = []
    
    # Find education entries
    for match in re.finditer(education_patterns['university'], text):
        # Get context (200 characters)
        start = max(0, match.start() - 100)
        end = min(len(text), match.end() + 100)
        context = text[start:end]
        
        entry = {
            'university': match.group(),
            'degree': None,
            'field': None,
            'year': None,
            'context': context
        }
        
        # Look for other components in the context
        degree_match = re.search(education_patterns['degree'], context)
        if degree_match:
            entry['degree'] = degree_match.group()
            
        field_match = re.search(education_patterns['field'], context)
        if field_match:
            entry['field'] = field_match.group()
            
        years = re.findall(education_patterns['year'], context)
        if years:
            entry['year'] = years
            
        education_entries.append(entry)
    
    # Format the output
    formatted_education = []
    for edu in education_entries:
        entry = []
        if edu['university']:
            entry.append(f"Institution: {edu['university']}")
        if edu['degree']:
            entry.append(f"Degree: {edu['degree']}")
        if edu['field']:
            entry.append(f"Field: {edu['field']}")
        if edu['year']:
            entry.append(f"Year(s): {', '.join(edu['year'])}")
        entry.append(f"Details: {edu['context']}")
        formatted_education.append("\n".join(entry))
    
    return "\n\n".join(formatted_education) if formatted_education else "No specific education detected"
