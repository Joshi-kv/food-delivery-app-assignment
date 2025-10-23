"""
Validation utilities for authentication forms
"""
import re
from django.core.validators import validate_email as django_validate_email
from django.core.exceptions import ValidationError


# Country codes with their validation patterns
COUNTRY_CODES = [
    {'code': '+1', 'name': 'United States/Canada', 'flag': '🇺🇸', 'pattern': r'^\d{10}$', 'placeholder': '2025551234'},
    {'code': '+44', 'name': 'United Kingdom', 'flag': '🇬🇧', 'pattern': r'^\d{10}$', 'placeholder': '7911123456'},
    {'code': '+91', 'name': 'India', 'flag': '🇮🇳', 'pattern': r'^\d{10}$', 'placeholder': '9876543210'},
    {'code': '+86', 'name': 'China', 'flag': '🇨🇳', 'pattern': r'^\d{11}$', 'placeholder': '13812345678'},
    {'code': '+81', 'name': 'Japan', 'flag': '🇯🇵', 'pattern': r'^\d{10}$', 'placeholder': '9012345678'},
    {'code': '+49', 'name': 'Germany', 'flag': '🇩🇪', 'pattern': r'^\d{10,11}$', 'placeholder': '15112345678'},
    {'code': '+33', 'name': 'France', 'flag': '🇫🇷', 'pattern': r'^\d{9}$', 'placeholder': '612345678'},
    {'code': '+61', 'name': 'Australia', 'flag': '🇦🇺', 'pattern': r'^\d{9}$', 'placeholder': '412345678'},
    {'code': '+7', 'name': 'Russia', 'flag': '🇷🇺', 'pattern': r'^\d{10}$', 'placeholder': '9123456789'},
    {'code': '+55', 'name': 'Brazil', 'flag': '🇧🇷', 'pattern': r'^\d{11}$', 'placeholder': '11987654321'},
    {'code': '+52', 'name': 'Mexico', 'flag': '🇲🇽', 'pattern': r'^\d{10}$', 'placeholder': '5512345678'},
    {'code': '+34', 'name': 'Spain', 'flag': '🇪🇸', 'pattern': r'^\d{9}$', 'placeholder': '612345678'},
    {'code': '+39', 'name': 'Italy', 'flag': '🇮🇹', 'pattern': r'^\d{10}$', 'placeholder': '3123456789'},
    {'code': '+82', 'name': 'South Korea', 'flag': '🇰🇷', 'pattern': r'^\d{10}$', 'placeholder': '1012345678'},
    {'code': '+65', 'name': 'Singapore', 'flag': '🇸🇬', 'pattern': r'^\d{8}$', 'placeholder': '81234567'},
    {'code': '+60', 'name': 'Malaysia', 'flag': '🇲🇾', 'pattern': r'^\d{9,10}$', 'placeholder': '123456789'},
    {'code': '+66', 'name': 'Thailand', 'flag': '🇹🇭', 'pattern': r'^\d{9}$', 'placeholder': '812345678'},
    {'code': '+63', 'name': 'Philippines', 'flag': '🇵🇭', 'pattern': r'^\d{10}$', 'placeholder': '9171234567'},
    {'code': '+62', 'name': 'Indonesia', 'flag': '🇮🇩', 'pattern': r'^\d{10,12}$', 'placeholder': '81234567890'},
    {'code': '+84', 'name': 'Vietnam', 'flag': '🇻🇳', 'pattern': r'^\d{9,10}$', 'placeholder': '912345678'},
    {'code': '+971', 'name': 'UAE', 'flag': '🇦🇪', 'pattern': r'^\d{9}$', 'placeholder': '501234567'},
    {'code': '+966', 'name': 'Saudi Arabia', 'flag': '🇸🇦', 'pattern': r'^\d{9}$', 'placeholder': '501234567'},
    {'code': '+27', 'name': 'South Africa', 'flag': '🇿🇦', 'pattern': r'^\d{9}$', 'placeholder': '712345678'},
    {'code': '+234', 'name': 'Nigeria', 'flag': '🇳🇬', 'pattern': r'^\d{10}$', 'placeholder': '8012345678'},
    {'code': '+20', 'name': 'Egypt', 'flag': '🇪🇬', 'pattern': r'^\d{10}$', 'placeholder': '1001234567'},
]

# Default country code
DEFAULT_COUNTRY_CODE = '+91'


def get_country_code_data(country_code):
    """Get country code data by code"""
    for cc in COUNTRY_CODES:
        if cc['code'] == country_code:
            return cc
    return None


def validate_mobile_number(country_code, mobile_number):
    """
    Validate mobile number based on country code
    
    Args:
        country_code (str): Country code (e.g., '+91')
        mobile_number (str): Mobile number without country code
        
    Returns:
        dict: {'valid': bool, 'message': str, 'full_number': str}
    """
    # Remove any spaces, dashes, or special characters
    mobile_number = re.sub(r'[^\d]', '', mobile_number)
    
    # Check if mobile number is empty
    if not mobile_number:
        return {
            'valid': False,
            'message': 'Mobile number is required',
            'full_number': None
        }
    
    # Get country code data
    cc_data = get_country_code_data(country_code)
    if not cc_data:
        return {
            'valid': False,
            'message': 'Invalid country code',
            'full_number': None
        }
    
    # Validate against country-specific pattern
    pattern = cc_data['pattern']
    if not re.match(pattern, mobile_number):
        return {
            'valid': False,
            'message': f'Invalid mobile number format for {cc_data["name"]}. Example: {cc_data["placeholder"]}',
            'full_number': None
        }
    
    # Create full number with country code
    full_number = f"{country_code}{mobile_number}"
    
    return {
        'valid': True,
        'message': 'Valid mobile number',
        'full_number': full_number
    }


def validate_email_address(email):
    """
    Validate email address
    
    Args:
        email (str): Email address
        
    Returns:
        dict: {'valid': bool, 'message': str}
    """
    if not email:
        return {
            'valid': True,  # Email is optional
            'message': 'Email is optional'
        }
    
    # Remove whitespace
    email = email.strip()
    
    # Basic format check
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return {
            'valid': False,
            'message': 'Invalid email format. Example: user@example.com'
        }
    
    # Use Django's email validator
    try:
        django_validate_email(email)
        return {
            'valid': True,
            'message': 'Valid email address'
        }
    except ValidationError:
        return {
            'valid': False,
            'message': 'Invalid email address'
        }


def validate_otp(otp):
    """
    Validate OTP format
    
    Args:
        otp (str): OTP code
        
    Returns:
        dict: {'valid': bool, 'message': str}
    """
    if not otp:
        return {
            'valid': False,
            'message': 'OTP is required'
        }
    
    # Remove whitespace
    otp = otp.strip()
    
    # Check if OTP is exactly 4 digits
    if not re.match(r'^\d{4}$', otp):
        return {
            'valid': False,
            'message': 'OTP must be exactly 4 digits'
        }
    
    return {
        'valid': True,
        'message': 'Valid OTP format'
    }


def validate_name(name, field_name='Name'):
    """
    Validate name fields
    
    Args:
        name (str): Name to validate
        field_name (str): Field name for error messages
        
    Returns:
        dict: {'valid': bool, 'message': str}
    """
    if not name:
        return {
            'valid': False,
            'message': f'{field_name} is required'
        }
    
    # Remove leading/trailing whitespace
    name = name.strip()
    
    # Check minimum length
    if len(name) < 2:
        return {
            'valid': False,
            'message': f'{field_name} must be at least 2 characters'
        }
    
    # Check maximum length
    if len(name) > 150:
        return {
            'valid': False,
            'message': f'{field_name} must be less than 150 characters'
        }
    
    # Check for valid characters (letters, spaces, hyphens, apostrophes)
    if not re.match(r"^[a-zA-Z\s\-']+$", name):
        return {
            'valid': False,
            'message': f'{field_name} can only contain letters, spaces, hyphens, and apostrophes'
        }
    
    return {
        'valid': True,
        'message': f'Valid {field_name.lower()}'
    }


def sanitize_input(value):
    """
    Sanitize user input to prevent injection attacks
    
    Args:
        value (str): Input value
        
    Returns:
        str: Sanitized value
    """
    if not value:
        return ''
    
    # Remove leading/trailing whitespace
    value = value.strip()
    
    # Remove any HTML tags
    value = re.sub(r'<[^>]*>', '', value)
    
    # Remove any script tags
    value = re.sub(r'<script[^>]*>.*?</script>', '', value, flags=re.DOTALL | re.IGNORECASE)
    
    return value

