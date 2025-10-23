"""
Core views - Authentication and shared functionality (Class-Based Views)
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View

from .models import User
from .helpers import (
    create_otp, verify_otp, log_activity, assign_user_to_role_group,
    is_admin_user, is_customer, is_delivery_partner
)
from .validators import (
    validate_mobile_number,
    validate_email_address,
    validate_otp as validate_otp_format,
    validate_name,
    sanitize_input,
    COUNTRY_CODES,
    DEFAULT_COUNTRY_CODE
)


# ============================================================================
# AUTHENTICATION VIEWS (Class-Based Views)
# ============================================================================

class BaseAuthView(View):
    """Base class for authentication views with common functionality"""

    template_name = None

    def get_context_data(self, **kwargs):
        """Get default context data for authentication templates"""
        context = {
            'country_codes': COUNTRY_CODES,
            'selected_country_code': kwargs.get('selected_country_code', DEFAULT_COUNTRY_CODE)
        }
        context.update(kwargs)
        return context

    def render_template(self, request, **kwargs):
        """Render template with context data"""
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context)


class LoginView(BaseAuthView):
    """Login view for existing customers and delivery partners"""

    template_name = 'auth/login.html'

    def get(self, request):
        """Handle GET request - show login form"""
        # If user is already authenticated, logout first to allow new login
        if request.user.is_authenticated:
            logout(request)
            messages.info(request, 'You have been logged out to login with a different account.')

        return self.render_template(request)

    def post(self, request):
        """Handle POST request - process login"""
        # If user is already authenticated, logout first to allow new login
        if request.user.is_authenticated:
            logout(request)
            messages.info(request, 'You have been logged out to login with a different account.')

        # Extract and sanitize form data
        country_code = sanitize_input(request.POST.get('country_code', DEFAULT_COUNTRY_CODE))
        mobile_number = sanitize_input(request.POST.get('mobile_number', ''))
        otp = sanitize_input(request.POST.get('otp', ''))
        role = request.POST.get('role', 'customer')
        step = request.POST.get('step', 'send_otp')

        if step == 'send_otp':
            return self.handle_send_otp(request, country_code, mobile_number, role)
        elif step == 'verify_otp':
            return self.handle_verify_otp(request, mobile_number, otp, role, country_code)

        return self.render_template(request)

    def handle_send_otp(self, request, country_code, mobile_number, role):
        """Handle OTP sending step"""
        # Validate mobile number
        validation_result = validate_mobile_number(country_code, mobile_number)
        if not validation_result['valid']:
            messages.error(request, validation_result['message'])
            return self.render_template(request, selected_country_code=country_code)

        full_number = validation_result['full_number']

        # Check if user exists
        try:
            user = User.objects.get(mobile_number=full_number)
        except User.DoesNotExist:
            messages.error(request, 'Account not found. Please sign up first.')
            return self.render_template(request, selected_country_code=country_code)

        # Create OTP
        result = create_otp(full_number)

        if result['success']:
            messages.success(request, f'OTP sent to {full_number}. Use 1234 to login.')
            return self.render_template(
                request,
                step='verify_otp',
                mobile_number=full_number,
                role=role,
                selected_country_code=country_code
            )
        else:
            messages.error(request, result['message'])
            return self.render_template(request, selected_country_code=country_code)

    def handle_verify_otp(self, request, mobile_number, otp, role, country_code):
        """Handle OTP verification step"""
        # Validate OTP format
        otp_validation = validate_otp_format(otp)
        if not otp_validation['valid']:
            messages.error(request, otp_validation['message'])
            return self.render_template(
                request,
                step='verify_otp',
                mobile_number=mobile_number,
                role=role,
                selected_country_code=country_code
            )

        # Verify OTP
        result = verify_otp(mobile_number, otp)

        if result['success']:
            # Get user
            try:
                user = User.objects.get(mobile_number=mobile_number)

                # Login user
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                log_activity(user, 'Login', 'User logged in', request)

                messages.success(request, 'Login successful!')
                return redirect('core:dashboard')
            except User.DoesNotExist:
                messages.error(request, 'Account not found. Please sign up first.')
                return self.render_template(request, selected_country_code=country_code)
        else:
            messages.error(request, result['message'])
            return self.render_template(
                request,
                step='verify_otp',
                mobile_number=mobile_number,
                role=role,
                selected_country_code=country_code
            )


class BaseSignupView(BaseAuthView):
    """Base class for signup views with common signup functionality"""

    user_role = None  # To be set by subclasses
    success_message = 'Account created successfully! Welcome aboard!'

    def get(self, request):
        """Handle GET request - show signup form"""
        # If user is already authenticated, logout first to allow new signup
        if request.user.is_authenticated:
            logout(request)
            messages.info(request, 'You have been logged out to create a new account.')

        return self.render_template(request)

    def post(self, request):
        """Handle POST request - process signup"""
        # If user is already authenticated, logout first to allow new signup
        if request.user.is_authenticated:
            logout(request)
            messages.info(request, 'You have been logged out to create a new account.')

        # Extract and sanitize form data
        country_code = sanitize_input(request.POST.get('country_code', DEFAULT_COUNTRY_CODE))
        mobile_number = sanitize_input(request.POST.get('mobile_number', ''))
        otp = sanitize_input(request.POST.get('otp', ''))
        first_name = sanitize_input(request.POST.get('first_name', ''))
        last_name = sanitize_input(request.POST.get('last_name', ''))
        email = sanitize_input(request.POST.get('email', ''))
        address = sanitize_input(request.POST.get('address', ''))
        step = request.POST.get('step', 'send_otp')

        if step == 'send_otp':
            return self.handle_send_otp(
                request, country_code, mobile_number,
                first_name, last_name, email, address
            )
        elif step == 'verify_otp':
            return self.handle_verify_otp(
                request, mobile_number, otp,
                first_name, last_name, email, address, country_code
            )

        return self.render_template(request)

    def handle_send_otp(self, request, country_code, mobile_number,
                        first_name, last_name, email, address):
        """Handle OTP sending step with validation"""
        form_data = {
            'selected_country_code': country_code,
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'address': address
        }

        # Validate mobile number
        mobile_validation = validate_mobile_number(country_code, mobile_number)
        if not mobile_validation['valid']:
            messages.error(request, mobile_validation['message'])
            return self.render_template(request, **form_data)

        full_number = mobile_validation['full_number']

        # Validate first name
        name_validation = validate_name(first_name, 'First name')
        if not name_validation['valid']:
            messages.error(request, name_validation['message'])
            return self.render_template(request, **form_data)

        # Validate last name if provided
        if last_name:
            last_name_validation = validate_name(last_name, 'Last name')
            if not last_name_validation['valid']:
                messages.error(request, last_name_validation['message'])
                return self.render_template(request, **form_data)

        # Validate email if provided
        if email:
            email_validation = validate_email_address(email)
            if not email_validation['valid']:
                messages.error(request, email_validation['message'])
                return self.render_template(request, **form_data)

        # Check if user already exists
        if User.objects.filter(mobile_number=full_number).exists():
            messages.error(request, 'Account already exists. Please login.')
            return self.render_template(request, selected_country_code=country_code)

        # Create OTP
        result = create_otp(full_number)

        if result['success']:
            messages.success(request, f'OTP sent to {full_number}. Use 1234 to verify.')
            return self.render_template(
                request,
                step='verify_otp',
                mobile_number=full_number,
                **form_data
            )
        else:
            messages.error(request, result['message'])
            return self.render_template(request, **form_data)

    def handle_verify_otp(self, request, mobile_number, otp,
                          first_name, last_name, email, address, country_code):
        """Handle OTP verification and user creation"""
        form_data = {
            'step': 'verify_otp',
            'mobile_number': mobile_number,
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'address': address,
            'selected_country_code': country_code
        }

        # Validate OTP format
        otp_validation = validate_otp_format(otp)
        if not otp_validation['valid']:
            messages.error(request, otp_validation['message'])
            return self.render_template(request, **form_data)

        # Verify OTP
        result = verify_otp(mobile_number, otp)

        if result['success']:
            # Create new user
            user = User.objects.create_user(
                mobile_number=mobile_number,
                role=self.user_role,
                first_name=first_name,
                last_name=last_name if last_name else '',
                email=email if email else None,
                address=address if address else None
            )
            assign_user_to_role_group(user)
            log_activity(user, 'User Registration', f'New {self.user_role} registered')

            # Login user
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            log_activity(user, 'Login', 'User logged in after signup', request)

            messages.success(request, self.success_message)
            return redirect('core:dashboard')
        else:
            messages.error(request, result['message'])
            return self.render_template(request, **form_data)


class CustomerSignupView(BaseSignupView):
    """Signup view for new customers"""

    template_name = 'auth/signup.html'
    user_role = 'customer'
    success_message = 'Account created successfully! Welcome aboard!'


class DeliveryPartnerSignupView(BaseSignupView):
    """Signup view for new delivery partners"""

    template_name = 'auth/delivery_signup.html'
    user_role = 'delivery_partner'
    success_message = 'Account created successfully! Welcome to our delivery team!'


class AdminLoginView(View):
    """Custom admin login view with email and password authentication"""

    template_name = 'auth/admin_login.html'

    def get(self, request):
        """Handle GET request - show admin login form"""
        if request.user.is_authenticated and is_admin_user(request.user):
            return redirect('administrator:dashboard')

        return render(request, self.template_name)

    def post(self, request):
        """Handle POST request - process admin login"""
        if request.user.is_authenticated and is_admin_user(request.user):
            return redirect('administrator:dashboard')

        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()

        if not email or not password:
            messages.error(request, 'Please enter email and password')
            return render(request, self.template_name)

        # Validate email format
        if '@' not in email:
            messages.error(request, 'Please enter a valid email address')
            return render(request, self.template_name)

        # Authenticate using custom backend (email + password)
        user = authenticate(request, username=email, password=password)

        if user is not None and is_admin_user(user):
            login(request, user)
            log_activity(user, 'Admin Login', 'Admin logged in', request)
            messages.success(request, 'Welcome back, Admin!')
            return redirect('administrator:dashboard')
        else:
            messages.error(request, 'Invalid email or password, or insufficient permissions')

        return render(request, self.template_name)


class LogoutView(LoginRequiredMixin, View):
    """Logout view for all users"""

    login_url = '/login/'

    def get(self, request):
        """Handle GET request - logout user"""
        log_activity(request.user, 'Logout', 'User logged out', request)
        logout(request)
        messages.success(request, 'Logged out successfully')
        return redirect('core:login')

    def post(self, request):
        """Handle POST request - logout user"""
        return self.get(request)


# ============================================================================
# DASHBOARD VIEW (Redirect based on role)
# ============================================================================

class DashboardView(LoginRequiredMixin, View):
    """Main dashboard view - redirects based on user role"""

    login_url = '/login/'

    def get(self, request):
        """Handle GET request - redirect to role-specific dashboard"""
        if is_admin_user(request.user):
            return redirect('administrator:dashboard')
        elif is_customer(request.user):
            return redirect('customer:dashboard')
        elif is_delivery_partner(request.user):
            return redirect('delivery_partner:dashboard')
        else:
            messages.error(request, 'Invalid user role')
            return redirect('core:login')

    def post(self, request):
        """Handle POST request - same as GET"""
        return self.get(request)


# ============================================================================
# HOME VIEW
# ============================================================================

class HomeView(View):
    """Home page - redirects to dashboard or login"""

    def get(self, request):
        """Handle GET request - redirect based on authentication status"""
        if request.user.is_authenticated:
            return redirect('core:dashboard')
        return redirect('core:login')

    def post(self, request):
        """Handle POST request - same as GET"""
        return self.get(request)
