
from rest_framework import serializers
from marshmallow import Schema, fields, validate
from .models import Resume, Job, ResumeMatch

class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = ['id', 'skills', 'experience', 'education', 'skills_feedback', 'format_feedback', 'ats_feedback']

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'

class ResumeMatchSerializer(serializers.ModelSerializer):
    job = JobSerializer(read_only=True)
    
    class Meta:
        model = ResumeMatch
        fields = ['id', 'job', 'score', 'matched_skills']

class ResumeValidationSchema(Schema):
    skills = fields.String(required=True)
    experience = fields.String(required=True)
    education = fields.String(required=True)
    min_word_count = fields.Integer(validate=validate.Range(min=100))
