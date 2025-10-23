"""
Delivery Partner app URL configuration
"""
from django.urls import path
from . import views

app_name = 'delivery_partner'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.DeliveryDashboardView.as_view(), name='dashboard'),

    # Deliveries
    path('deliveries/', views.DeliveryListView.as_view(), name='delivery_list'),
    path('deliveries/<int:booking_id>/', views.ViewDeliveryView.as_view(), name='view_delivery'),
    path('deliveries/<int:booking_id>/update-status/', views.UpdateBookingStatusView.as_view(), name='update_status'),

    # Chat
    path('chat/<int:booking_id>/', views.ChatView.as_view(), name='chat'),

    # Profile
    path('profile/', views.ProfileView.as_view(), name='profile'),

    # API endpoints
    path('api/bookings/<int:booking_id>/status/', views.GetBookingStatusAPIView.as_view(), name='api_booking_status'),
    path('api/bookings/<int:booking_id>/unread-messages/', views.GetUnreadMessagesCountAPIView.as_view(), name='api_unread_messages'),
]

