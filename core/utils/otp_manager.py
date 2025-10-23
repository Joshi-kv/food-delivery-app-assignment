"""
Redis-based OTP Manager
Handles OTP generation, storage, and verification using Redis cache
"""
import random
import string
from django.core.cache import caches
from django.conf import settings


class OTPManager:
    """
    OTP Manager using Redis for temporary storage
    Following industrial standards - no database storage for OTPs
    """
    
    # OTP Configuration
    OTP_LENGTH = 4
    OTP_EXPIRY = 300  # 5 minutes in seconds
    MAX_ATTEMPTS = 3
    STATIC_OTP = "1234"  # For development as per requirements
    
    def __init__(self):
        """Initialize OTP manager with Redis cache"""
        self.cache = caches['otp_cache']
    
    def _get_otp_key(self, mobile_number):
        """Generate Redis key for OTP"""
        return f"otp:{mobile_number}"
    
    def _get_attempts_key(self, mobile_number):
        """Generate Redis key for OTP attempts"""
        return f"otp_attempts:{mobile_number}"
    
    def _get_verified_key(self, mobile_number):
        """Generate Redis key for verified OTP"""
        return f"otp_verified:{mobile_number}"
    
    def generate_otp(self):
        """
        Generate OTP
        For development: always returns 1234
        For production: generates random 4-digit OTP
        """
        if settings.DEBUG:
            return self.STATIC_OTP
        
        # Generate random 4-digit OTP
        return ''.join(random.choices(string.digits, k=self.OTP_LENGTH))
    
    def create_otp(self, mobile_number):
        """
        Create and store OTP for a mobile number
        
        Args:
            mobile_number (str): Mobile number to send OTP to
            
        Returns:
            dict: {
                'success': bool,
                'otp': str,
                'message': str,
                'expires_in': int (seconds)
            }
        """
        # Check if OTP already exists and is still valid
        existing_otp = self.cache.get(self._get_otp_key(mobile_number))
        if existing_otp:
            return {
                'success': False,
                'otp': None,
                'message': 'OTP already sent. Please wait before requesting a new one.',
                'expires_in': self.cache.ttl(self._get_otp_key(mobile_number))
            }
        
        # Generate new OTP
        otp = self.generate_otp()
        
        # Store OTP in Redis with expiry
        self.cache.set(
            self._get_otp_key(mobile_number),
            otp,
            timeout=self.OTP_EXPIRY
        )
        
        # Reset attempts counter
        self.cache.delete(self._get_attempts_key(mobile_number))
        
        # Delete any previous verification status
        self.cache.delete(self._get_verified_key(mobile_number))
        
        return {
            'success': True,
            'otp': otp,
            'message': 'OTP generated successfully',
            'expires_in': self.OTP_EXPIRY
        }
    
    def verify_otp(self, mobile_number, otp):
        """
        Verify OTP for a mobile number
        
        Args:
            mobile_number (str): Mobile number
            otp (str): OTP to verify
            
        Returns:
            dict: {
                'success': bool,
                'message': str,
                'attempts_left': int
            }
        """
        # Get stored OTP
        stored_otp = self.cache.get(self._get_otp_key(mobile_number))
        
        if not stored_otp:
            return {
                'success': False,
                'message': 'OTP expired or not found. Please request a new OTP.',
                'attempts_left': 0
            }
        
        # Get current attempts
        attempts_key = self._get_attempts_key(mobile_number)
        attempts = self.cache.get(attempts_key, 0)
        
        # Check if max attempts exceeded
        if attempts >= self.MAX_ATTEMPTS:
            # Delete OTP to prevent further attempts
            self.cache.delete(self._get_otp_key(mobile_number))
            self.cache.delete(attempts_key)
            return {
                'success': False,
                'message': 'Maximum verification attempts exceeded. Please request a new OTP.',
                'attempts_left': 0
            }
        
        # Verify OTP
        if str(otp).strip() == str(stored_otp).strip():
            # OTP is correct
            # Mark as verified
            self.cache.set(
                self._get_verified_key(mobile_number),
                True,
                timeout=600  # 10 minutes to complete registration/login
            )
            
            # Delete OTP and attempts
            self.cache.delete(self._get_otp_key(mobile_number))
            self.cache.delete(attempts_key)
            
            return {
                'success': True,
                'message': 'OTP verified successfully',
                'attempts_left': self.MAX_ATTEMPTS
            }
        else:
            # OTP is incorrect
            attempts += 1
            self.cache.set(attempts_key, attempts, timeout=self.OTP_EXPIRY)
            
            return {
                'success': False,
                'message': f'Invalid OTP. {self.MAX_ATTEMPTS - attempts} attempts remaining.',
                'attempts_left': self.MAX_ATTEMPTS - attempts
            }
    
    def is_verified(self, mobile_number):
        """
        Check if mobile number has been verified
        
        Args:
            mobile_number (str): Mobile number to check
            
        Returns:
            bool: True if verified, False otherwise
        """
        return self.cache.get(self._get_verified_key(mobile_number), False)
    
    def clear_verification(self, mobile_number):
        """
        Clear verification status for a mobile number
        
        Args:
            mobile_number (str): Mobile number
        """
        self.cache.delete(self._get_verified_key(mobile_number))
    
    def get_otp_status(self, mobile_number):
        """
        Get OTP status for a mobile number
        
        Args:
            mobile_number (str): Mobile number
            
        Returns:
            dict: {
                'exists': bool,
                'verified': bool,
                'attempts': int,
                'expires_in': int (seconds)
            }
        """
        otp_key = self._get_otp_key(mobile_number)
        exists = self.cache.get(otp_key) is not None
        verified = self.is_verified(mobile_number)
        attempts = self.cache.get(self._get_attempts_key(mobile_number), 0)
        expires_in = self.cache.ttl(otp_key) if exists else 0
        
        return {
            'exists': exists,
            'verified': verified,
            'attempts': attempts,
            'expires_in': expires_in
        }


# Singleton instance
otp_manager = OTPManager()

