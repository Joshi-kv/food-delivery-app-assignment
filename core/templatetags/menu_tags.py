from django import template
from django.contrib.auth.models import Group
from core.models import DynamicMenu, GroupMenuAccess, UserMenuAccess

register = template.Library()


@register.simple_tag
def get_user_menus(user):
    """Get all menus accessible to the user based on role and permissions"""
    if not user.is_authenticated:
        return []
    
    # Admin gets all menus
    if user.role == 'admin' or user.is_superuser:
        return DynamicMenu.objects.filter(is_active=True, parent=None).order_by('sort_order')
    
    # Get user's groups
    user_groups = user.groups.all()
    
    # Get menus from group access
    group_menu_ids = GroupMenuAccess.objects.filter(
        group__in=user_groups
    ).values_list('dynamic_menu_id', flat=True)
    
    # Get menus from user access
    user_menu_ids = UserMenuAccess.objects.filter(
        user=user
    ).values_list('dynamic_menu_id', flat=True)
    
    # Combine both
    menu_ids = set(list(group_menu_ids) + list(user_menu_ids))
    
    # Get parent menus
    menus = DynamicMenu.objects.filter(
        id__in=menu_ids,
        is_active=True,
        parent=None
    ).order_by('sort_order')
    
    return menus


@register.simple_tag
def get_submenu(parent_menu, user):
    """Get submenus for a parent menu"""
    if not user.is_authenticated:
        return []
    
    # Admin gets all submenus
    if user.role == 'admin' or user.is_superuser:
        return parent_menu.children.filter(is_active=True).order_by('sort_order')
    
    # Get user's groups
    user_groups = user.groups.all()
    
    # Get menus from group access
    group_menu_ids = GroupMenuAccess.objects.filter(
        group__in=user_groups
    ).values_list('dynamic_menu_id', flat=True)
    
    # Get menus from user access
    user_menu_ids = UserMenuAccess.objects.filter(
        user=user
    ).values_list('dynamic_menu_id', flat=True)
    
    # Combine both
    menu_ids = set(list(group_menu_ids) + list(user_menu_ids))
    
    # Get submenus
    submenus = parent_menu.children.filter(
        id__in=menu_ids,
        is_active=True
    ).order_by('sort_order')
    
    return submenus


@register.simple_tag
def has_menu_access(user, menu_id):
    """Check if user has access to a specific menu"""
    if not user.is_authenticated:
        return False
    
    # Admin has access to all menus
    if user.role == 'admin' or user.is_superuser:
        return True
    
    # Get user's groups
    user_groups = user.groups.all()
    
    # Check group access
    group_access = GroupMenuAccess.objects.filter(
        group__in=user_groups,
        dynamic_menu_id=menu_id
    ).exists()
    
    if group_access:
        return True
    
    # Check user access
    user_access = UserMenuAccess.objects.filter(
        user=user,
        dynamic_menu_id=menu_id
    ).exists()
    
    return user_access


@register.filter
def get_role_display(role):
    """Get display name for role"""
    role_map = {
        'customer': 'Customer',
        'delivery_partner': 'Delivery Partner',
        'admin': 'Admin',
    }
    return role_map.get(role, role)


@register.filter
def get_status_badge_class(status):
    """Get Bootstrap badge class for booking status"""
    status_classes = {
        'pending': 'badge-warning',
        'assigned': 'badge-info',
        'started': 'badge-primary',
        'reached': 'badge-primary',
        'collected': 'badge-primary',
        'delivered': 'badge-success',
        'cancelled': 'badge-danger',
    }
    return status_classes.get(status, 'badge-secondary')


@register.filter
def get_status_display(status):
    """Get display name for booking status"""
    status_map = {
        'pending': 'Pending',
        'assigned': 'Assigned',
        'started': 'Started',
        'reached': 'Reached',
        'collected': 'Collected',
        'delivered': 'Delivered',
        'cancelled': 'Cancelled',
    }
    return status_map.get(status, status)


@register.simple_tag
def unread_messages_count(user, booking):
    """Get count of unread messages for a user in a booking"""
    from core.models import ChatMessage
    
    if not user.is_authenticated:
        return 0
    
    return ChatMessage.objects.filter(
        booking=booking,
        receiver=user,
        is_read=False
    ).count()


@register.filter
def format_datetime(value):
    """Format datetime for display"""
    if not value:
        return ''
    
    from django.utils import timezone
    from datetime import datetime, timedelta
    
    now = timezone.now()
    diff = now - value
    
    if diff < timedelta(minutes=1):
        return 'Just now'
    elif diff < timedelta(hours=1):
        minutes = int(diff.total_seconds() / 60)
        return f'{minutes} minute{"s" if minutes > 1 else ""} ago'
    elif diff < timedelta(days=1):
        hours = int(diff.total_seconds() / 3600)
        return f'{hours} hour{"s" if hours > 1 else ""} ago'
    elif diff < timedelta(days=7):
        days = diff.days
        return f'{days} day{"s" if days > 1 else ""} ago'
    else:
        return value.strftime('%b %d, %Y %I:%M %p')

