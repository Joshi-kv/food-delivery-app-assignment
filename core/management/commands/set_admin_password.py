"""
Management command to set or reset administrator password
Usage: python manage.py set_admin_password <email> <password>
"""

from django.core.management.base import BaseCommand, CommandError
from core.models import User


class Command(BaseCommand):
    help = 'Set or reset administrator password'

    def add_arguments(self, parser):
        parser.add_argument(
            'email',
            type=str,
            help='Administrator email address'
        )
        parser.add_argument(
            'password',
            type=str,
            nargs='?',
            default=None,
            help='New password (optional, will prompt if not provided)'
        )
        parser.add_argument(
            '--create',
            action='store_true',
            help='Create administrator if not exists'
        )

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        create = options['create']

        # Validate email
        if '@' not in email:
            raise CommandError('Invalid email address')

        # Get or create administrator
        try:
            user = User.objects.get(email=email, role='administrator')
            self.stdout.write(f'Found administrator: {user.mobile_number} ({user.email})')
        except User.DoesNotExist:
            if create:
                # Create new administrator
                mobile_number = input('Enter mobile number for new administrator: ')
                first_name = input('Enter first name (optional): ')
                last_name = input('Enter last name (optional): ')
                
                user = User.objects.create_user(
                    mobile_number=mobile_number,
                    email=email,
                    role='administrator',
                    first_name=first_name if first_name else '',
                    last_name=last_name if last_name else '',
                    is_staff=True,
                    is_superuser=True
                )
                self.stdout.write(self.style.SUCCESS(f'Created new administrator: {user.mobile_number} ({user.email})'))
            else:
                raise CommandError(f'Administrator with email {email} not found. Use --create to create a new one.')
        except User.MultipleObjectsReturned:
            raise CommandError(f'Multiple administrators found with email {email}')

        # Get password if not provided
        if not password:
            from getpass import getpass
            password = getpass('Enter new password: ')
            password_confirm = getpass('Confirm password: ')
            
            if password != password_confirm:
                raise CommandError('Passwords do not match')

        # Validate password
        if len(password) < 6:
            raise CommandError('Password must be at least 6 characters long')

        # Set password
        user.set_password(password)
        user.save()

        self.stdout.write(self.style.SUCCESS(f'Password updated successfully for {user.email}'))
        self.stdout.write(f'Administrator can now login at /admin/login/ with:')
        self.stdout.write(f'  Email: {user.email}')
        self.stdout.write(f'  Password: {"*" * len(password)}')

