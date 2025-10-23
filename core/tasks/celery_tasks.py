"""
Celery tasks for the food delivery application
"""
from celery import shared_task
from django.core.cache import caches
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


@shared_task(name='core.tasks.cleanup_expired_otps')
def cleanup_expired_otps():
    """
    Cleanup expired OTPs from Redis cache
    This task runs periodically via Celery Beat
    """
    try:
        otp_cache = caches['otp_cache']
        # Redis automatically handles TTL, but we can log the cleanup
        logger.info("OTP cleanup task executed - Redis handles TTL automatically")
        return "OTP cleanup completed"
    except Exception as e:
        logger.error(f"Error in cleanup_expired_otps: {str(e)}")
        return f"Error: {str(e)}"


@shared_task(name='core.tasks.send_sms')
def send_sms_task(mobile_number, message):
    """
    Send SMS to a mobile number
    This is a placeholder for actual SMS integration
    
    Args:
        mobile_number (str): Mobile number to send SMS to
        message (str): Message content
    """
    try:
        # TODO: Integrate with SMS provider (Twilio, AWS SNS, etc.)
        logger.info(f"SMS to {mobile_number}: {message}")
        
        # For development, just log the message
        print(f"[SMS] To: {mobile_number}, Message: {message}")
        
        return f"SMS sent to {mobile_number}"
    except Exception as e:
        logger.error(f"Error sending SMS to {mobile_number}: {str(e)}")
        return f"Error: {str(e)}"


@shared_task(name='core.tasks.send_email')
def send_email_task(email, subject, message):
    """
    Send email
    This is a placeholder for actual email integration
    
    Args:
        email (str): Email address
        subject (str): Email subject
        message (str): Email content
    """
    try:
        # TODO: Integrate with email provider
        logger.info(f"Email to {email}: {subject}")
        
        # For development, just log the message
        print(f"[EMAIL] To: {email}, Subject: {subject}, Message: {message}")
        
        return f"Email sent to {email}"
    except Exception as e:
        logger.error(f"Error sending email to {email}: {str(e)}")
        return f"Error: {str(e)}"


@shared_task(name='core.tasks.send_booking_notification')
def send_booking_notification(booking_id, notification_type):
    """
    Send booking notification to relevant parties
    
    Args:
        booking_id (int): Booking ID
        notification_type (str): Type of notification (created, assigned, status_update, etc.)
    """
    try:
        from core.models import Booking
        
        booking = Booking.objects.get(id=booking_id)
        
        if notification_type == 'created':
            # Notify customer
            message = f"Your booking #{booking.id} has been created successfully."
            send_sms_task.delay(booking.customer.mobile_number, message)
            
        elif notification_type == 'assigned':
            # Notify delivery partner
            if booking.delivery_partner:
                message = f"New booking #{booking.id} assigned to you. Pickup: {booking.pickup_address}"
                send_sms_task.delay(booking.delivery_partner.mobile_number, message)
            
            # Notify customer
            message = f"Your booking #{booking.id} has been assigned to a delivery partner."
            send_sms_task.delay(booking.customer.mobile_number, message)
            
        elif notification_type == 'status_update':
            # Notify customer about status change
            message = f"Your booking #{booking.id} status: {booking.get_status_display()}"
            send_sms_task.delay(booking.customer.mobile_number, message)
            
        elif notification_type == 'delivered':
            # Notify customer
            message = f"Your booking #{booking.id} has been delivered successfully."
            send_sms_task.delay(booking.customer.mobile_number, message)
        
        logger.info(f"Booking notification sent: {notification_type} for booking #{booking_id}")
        return f"Notification sent for booking #{booking_id}"
        
    except Exception as e:
        logger.error(f"Error sending booking notification: {str(e)}")
        return f"Error: {str(e)}"


@shared_task(name='core.tasks.send_booking_reminders')
def send_booking_reminders():
    """
    Send reminders for pending bookings
    This task runs periodically via Celery Beat
    """
    try:
        from core.models import Booking
        from datetime import timedelta
        
        # Get bookings that are pending for more than 30 minutes
        threshold_time = timezone.now() - timedelta(minutes=30)
        pending_bookings = Booking.objects.filter(
            status='pending',
            created_at__lte=threshold_time
        )
        
        count = 0
        for booking in pending_bookings:
            # Send reminder to admin or relevant party
            logger.info(f"Reminder: Booking #{booking.id} is pending for more than 30 minutes")
            count += 1
        
        return f"Sent {count} booking reminders"
        
    except Exception as e:
        logger.error(f"Error in send_booking_reminders: {str(e)}")
        return f"Error: {str(e)}"

