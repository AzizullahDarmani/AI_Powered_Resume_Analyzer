
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import (
    ResumeSerializer, JobSerializer, ResumeMatchSerializer, 
    FavoriteJobSerializer, ResumeValidation, ResumeValidationSchema
)
from .models import Resume, Job, ResumeMatch, FavoriteJob
from django.shortcuts import get_object_or_404

class ResumeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ResumeSerializer
    
    def get_queryset(self):
        return Resume.objects.filter(user=self.request.user)

class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]

class ResumeMatchViewSet(viewsets.ModelViewSet):
    serializer_class = ResumeMatchSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ResumeMatch.objects.filter(resume__user=self.request.user)

class FavoriteJobViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteJobSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return FavoriteJob.objects.filter(user=self.request.user)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def validate_resume(request):
    try:
        # Pydantic validation
        resume_data = ResumeValidation(**request.data)
        
        # Marshmallow validation
        schema = ResumeValidationSchema()
        schema.load(request.data)
        
        return Response({'status': 'valid'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
