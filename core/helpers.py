"""
Helper functions for the food delivery application
"""
import random
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import ActivityLog
from .utils.otp_manager import otp_manager

User = get_user_model()


def generate_otp():
    """Generate a 4-digit OTP"""
    # For development, always return 1234 as specified in requirements
    return otp_manager.generate_otp()


def create_otp(mobile_number):
    """
    Create and save OTP for a mobile number using Redis

    Returns:
        dict: Result from OTP manager with keys:
            - success: bool
            - otp: str (if successful)
            - message: str
            - expires_in: int (seconds)
    """
    result = otp_manager.create_otp(mobile_number)

    # In production, send SMS here if successful
    # if result['success']:
    #     from .tasks import send_sms_task
    #     send_sms_task.delay(mobile_number, f"Your OTP is: {result['otp']}")

    return result


def verify_otp(mobile_number, otp_code):
    """
    Verify OTP for a mobile number using Redis

    Returns:
        dict: Result from OTP manager with keys:
            - success: bool
            - message: str
            - attempts_left: int
    """
    return otp_manager.verify_otp(mobile_number, otp_code)


def log_activity(user, action, description=None, request=None):
    """Log user activity"""
    ip_address = None
    user_agent = None
    
    if request:
        # Get IP address
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')
        
        # Get user agent
        user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    ActivityLog.objects.create(
        user=user,
        action=action,
        description=description,
        ip_address=ip_address,
        user_agent=user_agent
    )


def get_user_role_group(role):
    """Get or create group for a role"""
    from django.contrib.auth.models import Group
    
    role_group_map = {
        'customer': 'Customers',
        'delivery_partner': 'Delivery Partners',
        'admin': 'Admins',
        'administrator': 'Admins',  # Support both 'admin' and 'administrator'
    }
    
    group_name = role_group_map.get(role)
    if group_name:
        group, created = Group.objects.get_or_create(name=group_name)
        return group
    return None


def assign_user_to_role_group(user):
    """Assign user to their role group"""
    group = get_user_role_group(user.role)
    if group:
        user.groups.clear()
        user.groups.add(group)


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def is_admin_user(user):
    """Check if user is admin"""
    return user.is_authenticated and (user.role == 'admin' or user.is_superuser)


def is_customer(user):
    """Check if user is customer"""
    return user.is_authenticated and user.role == 'customer'


def is_delivery_partner(user):
    """Check if user is delivery partner"""
    return user.is_authenticated and user.role == 'delivery_partner'


def can_access_booking(user, booking):
    """Check if user can access a booking"""
    if is_admin_user(user):
        return True
    
    if is_customer(user) and booking.customer_id == user.id:
        return True
    
    if is_delivery_partner(user) and booking.delivery_partner_id == user.id:
        return True
    
    return False


def can_cancel_booking(user, booking):
    """Check if user can cancel a booking"""
    # Only customer can cancel
    if not is_customer(user) or booking.customer_id != user.id:
        return False
    
    # Can only cancel if not delivered or already cancelled
    if booking.status in ['delivered', 'cancelled']:
        return False
    
    return True


def can_update_booking_status(user, booking):
    """Check if user can update booking status"""
    # Admin can always update
    if is_admin_user(user):
        return True
    
    # Delivery partner can update their assigned bookings
    if is_delivery_partner(user) and booking.delivery_partner_id == user.id:
        return True
    
    return False


def get_next_booking_status(current_status):
    """Get the next valid status for a booking"""
    status_flow = {
        'pending': 'assigned',
        'assigned': 'started',
        'started': 'reached',
        'reached': 'collected',
        'collected': 'delivered',
    }
    return status_flow.get(current_status)


def get_available_delivery_partners():
    """Get list of available delivery partners"""
    return User.objects.filter(
        role='delivery_partner',
        is_active=True
    ).order_by('first_name', 'last_name')

