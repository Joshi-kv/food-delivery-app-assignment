"""
Management command to setup RBAC system with dynamic menus
Following the pattern from hisense-hiconnect reference project
Uses Django's built-in Permission system
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from core.models import DynamicMenu, GroupMenuAccess, Booking, User, ChatMessage


class Command(BaseCommand):
    help = 'Setup RBAC system with dynamic menus and group access'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up RBAC system...'))

        # Create groups
        self.create_groups()

        # Assign Django permissions to groups (following hisense-hiconnect pattern)
        self.assign_permissions()

        # Create menus
        self.create_menus()

        # Assign menu access to groups
        self.assign_menu_access()

        self.stdout.write(self.style.SUCCESS('RBAC system setup completed successfully!'))

    def create_groups(self):
        """Create user groups"""
        self.stdout.write('Creating user groups...')

        groups = ['Customers', 'Delivery Partners', 'Admins']

        for group_name in groups:
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'  Created group: {group_name}'))
            else:
                self.stdout.write(f'  Group already exists: {group_name}')

    def assign_permissions(self):
        """
        Assign Django's auto-generated permissions to groups
        Following hisense-hiconnect pattern - using Django's built-in permissions
        """
        self.stdout.write('Assigning Django permissions to groups...')

        # Get groups
        customers_group = Group.objects.get(name='Customers')
        delivery_partners_group = Group.objects.get(name='Delivery Partners')
        admins_group = Group.objects.get(name='Admins')

        # Get content types
        booking_ct = ContentType.objects.get_for_model(Booking)
        user_ct = ContentType.objects.get_for_model(User)
        chatmessage_ct = ContentType.objects.get_for_model(ChatMessage)

        # Customer permissions - can create, view, and change their own bookings
        customer_permissions = [
            Permission.objects.get(content_type=booking_ct, codename='add_booking'),
            Permission.objects.get(content_type=booking_ct, codename='view_booking'),
            Permission.objects.get(content_type=booking_ct, codename='change_booking'),
            Permission.objects.get(content_type=user_ct, codename='change_user'),  # For profile updates
            Permission.objects.get(content_type=chatmessage_ct, codename='view_chatmessage'),
            Permission.objects.get(content_type=chatmessage_ct, codename='add_chatmessage'),
        ]
        customers_group.permissions.set(customer_permissions)
        self.stdout.write(self.style.SUCCESS(f'  Assigned {len(customer_permissions)} permissions to Customers'))

        # Delivery Partner permissions - can view and change bookings (for status updates)
        delivery_permissions = [
            Permission.objects.get(content_type=booking_ct, codename='view_booking'),
            Permission.objects.get(content_type=booking_ct, codename='change_booking'),
            Permission.objects.get(content_type=user_ct, codename='change_user'),  # For profile updates
            Permission.objects.get(content_type=chatmessage_ct, codename='view_chatmessage'),
            Permission.objects.get(content_type=chatmessage_ct, codename='add_chatmessage'),
        ]
        delivery_partners_group.permissions.set(delivery_permissions)
        self.stdout.write(self.style.SUCCESS(f'  Assigned {len(delivery_permissions)} permissions to Delivery Partners'))

        # Admin permissions - all permissions for all models
        admin_permissions = Permission.objects.filter(
            content_type__in=[booking_ct, user_ct, chatmessage_ct]
        )
        admins_group.permissions.set(admin_permissions)
        self.stdout.write(self.style.SUCCESS(f'  Assigned {admin_permissions.count()} permissions to Admins'))

        self.stdout.write(self.style.SUCCESS('Permission assignment completed!'))

    def create_menus(self):
        """Create dynamic menus"""
        self.stdout.write('Creating dynamic menus...')

        # Define menu structure
        # NOTE: route_name should use namespaced URL names (e.g., 'customer:dashboard')
        menus = [
            # Customer Menus
            {
                'title': 'Dashboard',
                'icon': 'fa fa-dashboard',
                'key_word': 'customer_dashboard',
                'route_name': 'customer:dashboard',
                'is_left_menu': True,
                'is_role_access': True,
                'is_active': True,
                'sort_order': 1,
                'parent': None
            },
            {
                'title': 'My Bookings',
                'icon': 'fa fa-list',
                'key_word': 'customer_bookings',
                'route_name': 'customer:booking_list',
                'is_left_menu': True,
                'is_role_access': True,
                'is_active': True,
                'sort_order': 2,
                'parent': None
            },
            {
                'title': 'Create Booking',
                'icon': 'fa fa-plus',
                'key_word': 'create_booking',
                'route_name': 'customer:create_booking',
                'is_left_menu': True,
                'is_role_access': True,
                'is_active': True,
                'sort_order': 3,
                'parent': None
            },
            {
                'title': 'Profile',
                'icon': 'fa fa-user',
                'key_word': 'customer_profile',
                'route_name': 'customer:profile',
                'is_left_menu': True,
                'is_role_access': True,
                'is_active': True,
                'sort_order': 4,
                'parent': None
            },

            # Delivery Partner Menus
            {
                'title': 'Dashboard',
                'icon': 'fa fa-dashboard',
                'key_word': 'delivery_dashboard',
                'route_name': 'delivery_partner:dashboard',
                'is_left_menu': True,
                'is_role_access': True,
                'is_active': True,
                'sort_order': 1,
                'parent': None
            },
            {
                'title': 'My Deliveries',
                'icon': 'fa fa-truck',
                'key_word': 'delivery_bookings',
                'route_name': 'delivery_partner:delivery_list',
                'is_left_menu': True,
                'is_role_access': True,
                'is_active': True,
                'sort_order': 2,
                'parent': None
            },
            {
                'title': 'Profile',
                'icon': 'fa fa-user',
                'key_word': 'delivery_profile',
                'route_name': 'delivery_partner:profile',
                'is_left_menu': True,
                'is_role_access': True,
                'is_active': True,
                'sort_order': 3,
                'parent': None
            },

            # Admin Menus
            {
                'title': 'Dashboard',
                'icon': 'fa fa-dashboard',
                'key_word': 'admin_dashboard',
                'route_name': 'administrator:dashboard',
                'is_left_menu': True,
                'is_role_access': True,
                'is_active': True,
                'sort_order': 1,
                'parent': None
            },
            {
                'title': 'All Bookings',
                'icon': 'fa fa-list-alt',
                'key_word': 'admin_bookings',
                'route_name': 'administrator:booking_list',
                'is_left_menu': True,
                'is_role_access': True,
                'is_active': True,
                'sort_order': 2,
                'parent': None
            },
            {
                'title': 'Users',
                'icon': 'fa fa-users',
                'key_word': 'admin_users',
                'route_name': 'administrator:user_list',
                'is_left_menu': True,
                'is_role_access': True,
                'is_active': True,
                'sort_order': 3,
                'parent': None
            },
            {
                'title': 'Reports',
                'icon': 'fa fa-bar-chart',
                'key_word': 'admin_reports',
                'route_name': 'administrator:reports',
                'is_left_menu': True,
                'is_role_access': True,
                'is_active': True,
                'sort_order': 4,
                'parent': None
            },
        ]

        for menu_data in menus:
            menu, created = DynamicMenu.objects.get_or_create(
                key_word=menu_data['key_word'],
                defaults=menu_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  Created menu: {menu.title}'))
            else:
                self.stdout.write(f'  Menu already exists: {menu.title}')

    def assign_menu_access(self):
        """Assign menu access to groups"""
        self.stdout.write('Assigning menu access to groups...')

        # Get groups
        customers_group = Group.objects.get(name='Customers')
        delivery_partners_group = Group.objects.get(name='Delivery Partners')
        admins_group = Group.objects.get(name='Admins')

        # Customer menu access
        customer_menus = DynamicMenu.objects.filter(
            key_word__in=['customer_dashboard', 'customer_bookings', 'create_booking', 'customer_profile']
        )
        for menu in customer_menus:
            access, created = GroupMenuAccess.objects.get_or_create(
                group=customers_group,
                dynamic_menu=menu
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  Assigned {menu.title} to Customers'))

        # Delivery Partner menu access
        delivery_menus = DynamicMenu.objects.filter(
            key_word__in=['delivery_dashboard', 'delivery_bookings', 'delivery_profile']
        )
        for menu in delivery_menus:
            access, created = GroupMenuAccess.objects.get_or_create(
                group=delivery_partners_group,
                dynamic_menu=menu
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  Assigned {menu.title} to Delivery Partners'))

        # Admin menu access
        admin_menus = DynamicMenu.objects.filter(
            key_word__in=['admin_dashboard', 'admin_bookings', 'admin_users', 'admin_reports']
        )
        for menu in admin_menus:
            access, created = GroupMenuAccess.objects.get_or_create(
                group=admins_group,
                dynamic_menu=menu
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  Assigned {menu.title} to Admins'))

        self.stdout.write(self.style.SUCCESS('Menu access assignment completed!'))

