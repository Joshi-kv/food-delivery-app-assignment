"""
Core app URL configuration - Authentication and shared views (Class-Based Views)
"""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Home
    path('', views.HomeView.as_view(), name='home'),

    # Authentication - Login
    path('login/', views.LoginView.as_view(), name='login'),
    path('admin/login/', views.AdminLoginView.as_view(), name='admin_login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    # Authentication - Signup
    path('signup/', views.CustomerSignupView.as_view(), name='signup'),
    path('delivery/signup/', views.DeliveryPartnerSignupView.as_view(), name='delivery_signup'),

    # Dashboard (redirects based on role)
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
]

