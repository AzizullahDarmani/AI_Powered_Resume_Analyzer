
from rest_framework import serializers
from .models import Resume, Job, ResumeMatch, FavoriteJob
from pydantic import BaseModel, Field
from marshmallow import Schema, fields, validate
from typing import List

# Pydantic model for resume validation
class ResumeValidation(BaseModel):
    skills: List[str] = Field(..., min_items=1)
    experience_years: int = Field(..., ge=0)
    education_level: str = Field(..., pattern='^(High School|Bachelor|Master|PhD)$')

# Marshmallow schema for resume validation
class ResumeValidationSchema(Schema):
    skills = fields.List(fields.Str(), required=True, validate=validate.Length(min=1))
    experience_years = fields.Int(required=True, validate=validate.Range(min=0))
    education_level = fields.Str(required=True, validate=validate.OneOf(['High School', 'Bachelor', 'Master', 'PhD']))

# DRF Serializers
class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = '__all__'

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'

class ResumeMatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResumeMatch
        fields = '__all__'

class FavoriteJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteJob
        fields = '__all__'
