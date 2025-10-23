"""
Custom authentication backends for the food delivery application
"""

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class EmailOrMobileBackend(ModelBackend):
    """
    Custom authentication backend that allows authentication with:
    - Email + Password (for administrators)
    - Mobile Number + Password (for all users)
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate user with email or mobile number
        
        Args:
            request: HTTP request object
            username: Can be email or mobile number
            password: User password
            
        Returns:
            User object if authentication successful, None otherwise
        """
        if username is None or password is None:
            return None

        try:
            # Try to get user by email first
            if '@' in username:
                user = User.objects.get(email=username)
            else:
                # Try to get user by mobile number
                user = User.objects.get(mobile_number=username)
                
        except User.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user
            User().set_password(password)
            return None
        except User.MultipleObjectsReturned:
            # If multiple users found, return None for security
            return None

        # Check password and if user can authenticate
        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None

