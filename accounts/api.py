
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from ratelimit.decorators import ratelimit
from .models import Resume, Job, ResumeMatch
from .serializers import ResumeSerializer, JobSerializer, ResumeMatchSerializer

class ResumeViewSet(viewsets.ModelViewSet):
    serializer_class = ResumeSerializer
    permission_classes = [IsAuthenticated]

    @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes
    @method_decorator(vary_on_cookie)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        return Resume.objects.filter(user=self.request.user)

@method_decorator(ratelimit(key='user', rate='100/h'), name='dispatch')
class JobViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@ratelimit(key='user', rate='50/h')
def get_resume_matches(request):
    matches = ResumeMatch.objects.filter(resume__user=request.user)
    serializer = ResumeMatchSerializer(matches, many=True)
    return Response(serializer.data)
