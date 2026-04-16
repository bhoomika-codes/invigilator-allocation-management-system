from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # PDFs
    path('my-duties/', views.download_my_duties, name='my_duties'),
    path('all-duties/', views.download_all_duties, name='all_duties'),
    path('allocate/<int:exam_id>/', views.auto_allocate, name='auto_allocate'),
    path('allocate-result/<int:exam_id>/', views.allocation_result, name='allocation_result'),
    
    # Auth
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html'
    ), name='login'),

    path('logout/', views.user_logout, name='logout'),
]