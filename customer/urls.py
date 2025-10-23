"""
Customer app URL configuration
"""
from django.urls import path
from . import views

app_name = 'customer'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.CustomerDashboardView.as_view(), name='dashboard'),

    # Bookings
    path('bookings/', views.BookingListView.as_view(), name='booking_list'),
    path('bookings/create/', views.CreateBookingView.as_view(), name='create_booking'),
    path('bookings/<int:booking_id>/', views.ViewBookingView.as_view(), name='view_booking'),
    path('bookings/<int:booking_id>/cancel/', views.CancelBookingView.as_view(), name='cancel_booking'),

    # Chat
    path('chat/<int:booking_id>/', views.ChatView.as_view(), name='chat'),

    # Profile
    path('profile/', views.ProfileView.as_view(), name='profile'),

    # API endpoints
    path('api/bookings/<int:booking_id>/status/', views.GetBookingStatusAPIView.as_view(), name='api_booking_status'),
    path('api/bookings/<int:booking_id>/unread-messages/', views.GetUnreadMessagesCountAPIView.as_view(), name='api_unread_messages'),
]

