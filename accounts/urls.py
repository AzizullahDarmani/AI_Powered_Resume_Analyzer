from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, api # api.py needs to be created

router = DefaultRouter()
router.register(r'resumes', api.ResumeViewSet, basename='resume') # ResumeViewSet needs to be defined in api.py
router.register(r'jobs', api.JobViewSet, basename='job') # JobViewSet needs to be defined in api.py

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/matches/', api.get_resume_matches, name='resume-matches'), # get_resume_matches needs to be defined in api.py
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='accounts/logout.html', next_page='login'), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('jobs/', views.jobs_list, name='jobs'),
    path('jobs/add/', views.add_job, name='add_job'),
    path('favorites/', views.favorite_jobs, name='favorite_jobs'),
    path('jobs/<int:job_id>/toggle-favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('clear-matches/', views.clear_matches, name='clear_matches'),
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(template_name='accounts/password_reset.html'),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'),
         name='password_reset_complete'),
]