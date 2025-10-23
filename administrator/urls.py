"""
Administrator app URL configuration
"""
from django.urls import path
from . import views

app_name = 'administrator'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.AdminDashboardView.as_view(), name='dashboard'),

    # Bookings
    path('bookings/', views.BookingListView.as_view(), name='booking_list'),
    path('bookings/<int:booking_id>/', views.ViewBookingView.as_view(), name='view_booking'),
    path('bookings/<int:booking_id>/assign/', views.AssignBookingView.as_view(), name='assign_booking'),

    # Users
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/<int:user_id>/', views.UserDetailView.as_view(), name='user_detail'),

    # Reports
    path('reports/', views.ReportsView.as_view(), name='reports'),

    # API endpoints
    path('api/delivery-partners/', views.GetDeliveryPartnersAPIView.as_view(), name='api_delivery_partners'),
    path('api/bookings/<int:booking_id>/status/', views.GetBookingStatusAPIView.as_view(), name='api_booking_status'),
]

