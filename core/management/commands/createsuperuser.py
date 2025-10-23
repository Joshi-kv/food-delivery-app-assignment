"""
Custom createsuperuser command that uses email instead of mobile number
This overrides Django's default createsuperuser command

Note: This command overrides the built-in Django createsuperuser command.
To ensure it takes precedence, make sure 'core' app is listed BEFORE
'django.contrib.auth' in INSTALLED_APPS (which it is by default).
"""

from django.core.management.base import BaseCommand, CommandError
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db import DEFAULT_DB_ALIAS
from getpass import getpass
import sys


class Command(BaseCommand):
    help = 'Create a superuser with email and password'
    requires_migrations_checks = True
    stealth_options = ('stdin',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Import here to avoid circular imports
        from core.models import User
        self.UserModel = User

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            dest='email',
            default=None,
            help='Specifies the email for the superuser.',
        )
        parser.add_argument(
            '--noinput', '--no-input',
            action='store_false',
            dest='interactive',
            help=(
                'Tells Django to NOT prompt the user for input of any kind. '
                'You must use --email with --noinput. Superusers created with '
                '--noinput will not be able to log in until they\'re given a '
                'valid password.'
            ),
        )
        parser.add_argument(
            '--database',
            default=DEFAULT_DB_ALIAS,
            help='Specifies the database to use. Default is "default".',
        )

    def handle(self, *args, **options):
        email = options['email']
        database = options['database']
        interactive = options['interactive']

        # Get email
        if not email:
            if not interactive:
                raise CommandError('--email is required when using --noinput')

            # Interactive mode - prompt for email
            while True:
                email = input('Email address: ').strip()
                if email:
                    try:
                        validate_email(email)
                        break
                    except ValidationError:
                        self.stderr.write(self.style.ERROR('Invalid email address. Please try again.'))
                else:
                    self.stderr.write(self.style.ERROR('Email address is required.'))
        else:
            # Validate provided email
            try:
                validate_email(email)
            except ValidationError:
                raise CommandError('Invalid email address')

        # Normalize email
        email = email.strip().lower()

        # Check if user with this email already exists
        if self.UserModel.objects.using(database).filter(email=email).exists():
            raise CommandError(f'User with email {email} already exists')

        # Get password
        password = None
        if not interactive:
            # Non-interactive mode - password must be set later
            self.stdout.write(
                self.style.WARNING(
                    'Superuser created with unusable password. '
                    'Use "python manage.py set_admin_password %s" to set a password.' % email
                )
            )
        else:
            # Interactive mode - prompt for password
            while not password:
                password = getpass('Password: ')
                if not password:
                    self.stderr.write(self.style.ERROR('Password cannot be empty.'))
                    continue

                password_confirm = getpass('Password (again): ')

                if password != password_confirm:
                    self.stderr.write(self.style.ERROR('Passwords do not match. Please try again.'))
                    password = None
                    continue

                if len(password) < 6:
                    self.stderr.write(self.style.ERROR('Password must be at least 6 characters long.'))
                    password = None
                    continue

        # Get optional fields
        first_name = ''
        last_name = ''
        if interactive:
            first_name = input('First name (optional): ').strip()
            last_name = input('Last name (optional): ').strip()

        # Create superuser
        try:
            user = self.UserModel.objects.db_manager(database).create_superuser(
                mobile_number=None,  # Will be auto-generated
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name
            )

            if interactive:
                self.stdout.write('')
                self.stdout.write(self.style.SUCCESS('✅ Superuser created successfully!'))
                self.stdout.write('')
                self.stdout.write(f'📧 Email: {user.email}')
                self.stdout.write(f'📱 Mobile Number (auto-generated): {user.mobile_number}')
                self.stdout.write(f'👤 Role: {user.get_role_display()}')
                self.stdout.write(f'🔧 Is Staff: {user.is_staff}')
                self.stdout.write(f'⭐ Is Superuser: {user.is_superuser}')
                self.stdout.write('')
                self.stdout.write(self.style.SUCCESS('You can now login at /admin/login/ with:'))
                self.stdout.write(f'  📧 Email: {user.email}')
                self.stdout.write(f'  🔒 Password: {"*" * len(password)}')
                self.stdout.write('')
            else:
                self.stdout.write(self.style.SUCCESS(f'Superuser created: {email}'))

        except Exception as e:
            raise CommandError(f'Error creating superuser: {str(e)}')

