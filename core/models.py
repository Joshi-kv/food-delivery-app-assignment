from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from autoslug import AutoSlugField
from django.utils import timezone


# Custom User Manager
class CustomUserManager(BaseUserManager):
    """Custom user manager for email-based authentication"""

    def create_user(self, mobile_number, password=None, **extra_fields):
        if not mobile_number:
            raise ValueError(_('The Mobile Number must be set'))
        user = self.model(mobile_number=mobile_number, **extra_fields)
        if password:
            user.set_password(password)
        user.save()
        return user

    def create_superuser(self, mobile_number=None, password=None, **extra_fields):
        """
        Create superuser with email instead of mobile number.

        For superusers (administrators), we use email as the primary identifier.
        If mobile_number is not provided, we generate a dummy one from the email.

        Usage:
            python manage.py createsuperuser
            # Will prompt for: Email, Password
            # Mobile number will be auto-generated from email
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        # For superusers, email is required
        email = extra_fields.get('email')
        if not email:
            raise ValueError(_('Superuser must have an email address'))

        # Normalize email
        email = self.normalize_email(email)
        extra_fields['email'] = email

        # Generate mobile number from email if not provided
        if not mobile_number:
            # Create a unique mobile number based on email
            # Format: +admin_<hash of email>
            import hashlib
            email_hash = hashlib.md5(email.encode()).hexdigest()[:10]
            mobile_number = f'+admin_{email_hash}'

            # Ensure uniqueness
            counter = 1
            original_mobile = mobile_number
            while self.model.objects.filter(mobile_number=mobile_number).exists():
                mobile_number = f'{original_mobile}_{counter}'
                counter += 1

        return self.create_user(mobile_number, password, **extra_fields)


# User Roles
ROLE_CHOICES = (
    ('customer', 'Customer'),
    ('delivery_partner', 'Delivery Partner'),
    ('admin', 'Admin'),
)


# Custom User Model
class User(AbstractUser):
    """Custom User model with mobile number authentication and role-based access"""

    username = models.CharField(max_length=150, blank=True, null=True)
    mobile_number = models.CharField(max_length=20, unique=True, verbose_name='Mobile Number')
    email = models.EmailField(blank=True, null=True)
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'mobile_number'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.mobile_number} - {self.get_role_display()}"

    def get_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.mobile_number


# NOTE: OTP is now handled via Redis cache, not database model
# See core/utils/otp_manager.py for OTP implementation


# Dynamic Menu Model (RBAC)
class DynamicMenu(models.Model):
    """Dynamic menu system for role-based access control"""

    title = models.CharField(max_length=200)
    icon = models.CharField(max_length=200, blank=True, null=True)
    key_word = models.CharField(max_length=200, blank=True, null=True)
    title_slug = AutoSlugField(populate_from='title', unique=True, blank=True, null=True)
    route_name = models.CharField(max_length=200, blank=True, null=True)
    is_left_menu = models.BooleanField(default=True)
    is_role_access = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    parent = models.ForeignKey('self', related_name='children', on_delete=models.CASCADE, null=True, blank=True)
    content_type = models.ForeignKey(ContentType, related_name='sub_menus', on_delete=models.CASCADE, null=True, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Dynamic Menu'
        verbose_name_plural = 'Dynamic Menus'
        ordering = ['sort_order', 'title']

    def __str__(self):
        return self.title


# Group Menu Access (RBAC)
class GroupMenuAccess(models.Model):
    """Group-based menu access control"""

    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='menu_access')
    dynamic_menu = models.ForeignKey(DynamicMenu, related_name='group_access', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Group Menu Access'
        verbose_name_plural = 'Group Menu Access'
        unique_together = ('group', 'dynamic_menu')

    def __str__(self):
        return f"{self.group.name} - {self.dynamic_menu.title}"


# User Menu Access (RBAC)
class UserMenuAccess(models.Model):
    """User-specific menu access control"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='menu_access')
    dynamic_menu = models.ForeignKey(DynamicMenu, related_name='user_access', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'User Menu Access'
        verbose_name_plural = 'User Menu Access'
        unique_together = ('user', 'dynamic_menu')

    def __str__(self):
        return f"{self.user.mobile_number} - {self.dynamic_menu.title}"


# Booking Status Choices
BOOKING_STATUS_CHOICES = (
    ('pending', 'Pending'),
    ('assigned', 'Assigned'),
    ('started', 'Started'),
    ('reached', 'Reached'),
    ('collected', 'Collected'),
    ('delivered', 'Delivered'),
    ('cancelled', 'Cancelled'),
)


# Booking Model
class Booking(models.Model):
    """Booking model for food delivery orders"""

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_bookings')
    delivery_partner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='delivery_bookings')

    # Booking Details
    pickup_address = models.TextField()
    delivery_address = models.TextField()
    customer_notes = models.TextField(blank=True, null=True)

    # Status
    status = models.CharField(max_length=20, choices=BOOKING_STATUS_CHOICES, default='pending')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assigned_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    reached_at = models.DateTimeField(null=True, blank=True)
    collected_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    # Additional Info
    cancellation_reason = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'
        ordering = ['-created_at']

    def __str__(self):
        return f"Booking #{self.id} - {self.customer.mobile_number} - {self.get_status_display()}"

    def can_chat(self):
        """Check if chat is enabled for this booking"""
        # Chat is only enabled when:
        # 1. A delivery partner has been assigned
        # 2. The booking status is one of: assigned, started, reached, collected
        return self.delivery_partner is not None and self.status in ['assigned', 'started', 'reached', 'collected']


# Booking Status Log
class BookingStatusLog(models.Model):
    """Log for tracking booking status changes"""

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='status_logs')
    status = models.CharField(max_length=20, choices=BOOKING_STATUS_CHOICES)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Booking Status Log'
        verbose_name_plural = 'Booking Status Logs'
        ordering = ['-created_at']

    def __str__(self):
        return f"Booking #{self.booking.id} - {self.get_status_display()} - {self.created_at}"


# Chat Message Model
class ChatMessage(models.Model):
    """Real-time chat messages between customer and delivery partner"""

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='chat_messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Chat Message'
        verbose_name_plural = 'Chat Messages'
        ordering = ['created_at']
        permissions = [
            ('chat_with_customer', 'Can chat with customer'),
            ('chat_with_delivery_partner', 'Can chat with delivery partner'),
        ]

    def __str__(self):
        return f"Message from {self.sender.mobile_number} to {self.receiver.mobile_number}"


# Activity Log Model
class ActivityLog(models.Model):
    """Activity log for tracking user actions"""

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Activity Log'
        verbose_name_plural = 'Activity Logs'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.action} - {self.created_at}"
