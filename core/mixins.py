"""
Utility mixins for common functionality
Following hisense-hiconnect pattern - NO custom permission mixins
Use Django's PermissionRequiredMixin directly in views
"""
from django.contrib import messages
from django.contrib.auth.mixins import AccessMixin
from django.http import JsonResponse
from django.shortcuts import redirect


class MessageMixin:
    """
    Mixin to add success/error messages
    Provides convenient methods for adding messages
    
    Usage:
        class CreateBookingView(MessageMixin, CreateView):
            success_message = 'Booking created successfully!'
            
            def form_valid(self, form):
                response = super().form_valid(form)
                self.add_success_message()
                return response
    """
    success_message = None
    error_message = None

    def get_success_message(self):
        """Get success message - can be overridden"""
        return self.success_message

    def get_error_message(self):
        """Get error message - can be overridden"""
        return self.error_message

    def add_success_message(self, message=None):
        """Add success message"""
        msg = message or self.get_success_message()
        if msg:
            messages.success(self.request, msg)

    def add_error_message(self, message=None):
        """Add error message"""
        msg = message or self.get_error_message()
        if msg:
            messages.error(self.request, msg)

    def add_info_message(self, message):
        """Add info message"""
        if message:
            messages.info(self.request, message)

    def add_warning_message(self, message):
        """Add warning message"""
        if message:
            messages.warning(self.request, message)


class ActivityLogMixin:
    """
    Mixin to log user activities
    Similar to ActivityLogMixin in hisense-hiconnect
    
    Usage:
        class CreateBookingView(ActivityLogMixin, CreateView):
            activity_action = 'Create Booking'
            
            def form_valid(self, form):
                response = super().form_valid(form)
                self.log_activity(description=f'Created booking #{self.object.id}')
                return response
    """
    activity_action = None
    
    def log_activity(self, action=None, description=''):
        """
        Log user activity
        
        Args:
            action: Action name (defaults to self.activity_action)
            description: Description of the activity
        """
        from .helpers import log_activity
        action_name = action or self.activity_action
        if action_name:
            log_activity(self.request.user, action_name, description, self.request)
    
    def get_activity_action(self):
        """Get activity action - can be overridden"""
        return self.activity_action
    
    def get_activity_description(self):
        """Get activity description - can be overridden"""
        return ''


class AjaxResponseMixin:
    """
    Mixin to handle AJAX requests
    Provides utility methods for AJAX views
    
    Usage:
        class GetBookingStatusAPI(AjaxResponseMixin, View):
            def get(self, request, *args, **kwargs):
                return self.json_response({'status': 'success'})
    """
    def is_ajax(self):
        """Check if request is AJAX"""
        return self.request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    def json_response(self, data, status=200):
        """Return JSON response"""
        return JsonResponse(data, status=status)

