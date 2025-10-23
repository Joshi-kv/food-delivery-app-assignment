"""
Context processors for making data available to all templates
Following hisense-hiconnect pattern for menu context processor
"""
from core.models import DynamicMenu, GroupMenuAccess, UserMenuAccess


def user_menus(request):
    """
    Context processor to add user's accessible menus to all templates
    This makes 'user_menus' available in all templates without needing to pass it explicitly

    Usage in templates:
        {% for menu in user_menus %}
            <a href="{% url menu.route_name %}">{{ menu.title }}</a>
        {% endfor %}
    """
    if not request.user.is_authenticated:
        return {'user_menus': []}

    user = request.user

    # Get user's groups
    user_groups = user.groups.all()

    if not user_groups.exists():
        return {'user_menus': []}

    # Get menus from group access
    group_menu_ids = GroupMenuAccess.objects.filter(
        group__in=user_groups
    ).values_list('dynamic_menu_id', flat=True)

    # Get menus from user access (if any)
    user_menu_ids = UserMenuAccess.objects.filter(
        user=user
    ).values_list('dynamic_menu_id', flat=True)

    # Combine both
    menu_ids = set(list(group_menu_ids) + list(user_menu_ids))

    # Get parent menus that are active and should appear in left menu
    menus = DynamicMenu.objects.filter(
        id__in=menu_ids,
        is_active=True,
        parent=None,
        is_left_menu=True
    ).order_by('sort_order')

    return {'user_menus': menus}


def user_role_info(request):
    """
    Context processor to add user role information to all templates
    Makes it easier to show/hide elements based on user role
    
    Usage in templates:
        {% if is_customer %}
            <!-- Customer-specific content -->
        {% endif %}
    """
    if not request.user.is_authenticated:
        return {
            'is_customer': False,
            'is_delivery_partner': False,
            'is_administrator': False,
        }
    
    user = request.user
    
    return {
        'is_customer': user.role == 'customer',
        'is_delivery_partner': user.role == 'delivery_partner',
        'is_administrator': user.role == 'admin' or user.is_superuser,
    }

