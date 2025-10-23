"""
Customer-specific views - Class-Based Views
Following hisense-hiconnect pattern with Django's PermissionRequiredMixin
"""
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.utils import timezone
from django.views.generic import TemplateView, ListView, DetailView, View

from core.models import Booking, ChatMessage, BookingStatusLog
from core.mixins import MessageMixin, ActivityLogMixin, AjaxResponseMixin
from core.helpers import can_cancel_booking, can_access_booking


class CustomerDashboardView(PermissionRequiredMixin, TemplateView):
    """Customer dashboard - requires view_booking permission"""
    permission_required = 'core.view_booking'
    template_name = 'customer/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get customer's bookings
        bookings = Booking.objects.filter(customer=self.request.user).order_by('-created_at')

        # Get statistics
        context['bookings'] = bookings[:10]  # Latest 10 bookings
        context['total_bookings'] = bookings.count()
        context['pending_bookings'] = bookings.filter(status='pending').count()
        context['active_bookings'] = bookings.filter(status__in=['assigned', 'started', 'reached', 'collected']).count()
        context['completed_bookings'] = bookings.filter(status='delivered').count()
        context['cancelled_bookings'] = bookings.filter(status='cancelled').count()

        return context


class CreateBookingView(PermissionRequiredMixin, MessageMixin, ActivityLogMixin, TemplateView):
    """Create new booking - requires add_booking permission"""
    permission_required = 'core.add_booking'
    template_name = 'customer/create_booking.html'
    success_message = 'Booking created successfully!'
    activity_action = 'Create Booking'

    def post(self, request, *args, **kwargs):
        pickup_address = request.POST.get('pickup_address', '').strip()
        delivery_address = request.POST.get('delivery_address', '').strip()
        customer_notes = request.POST.get('customer_notes', '').strip()

        if not pickup_address or not delivery_address:
            messages.error(request, 'Please provide both pickup and delivery addresses')
            return self.get(request, *args, **kwargs)

        # Create booking
        booking = Booking.objects.create(
            customer=request.user,
            pickup_address=pickup_address,
            delivery_address=delivery_address,
            customer_notes=customer_notes,
            status='pending'
        )


        # Log status
        BookingStatusLog.objects.create(
            booking=booking,
            status='pending',
            changed_by=request.user,
            notes='Booking created'
        )

        self.log_activity(description=f'Created booking #{booking.id}')
        self.add_success_message()

        return redirect('customer:view_booking', booking_id=booking.id)


class BookingListView(PermissionRequiredMixin, ListView):
    """List customer's bookings - requires view_booking permission"""
    permission_required = 'core.view_booking'
    model = Booking
    template_name = 'customer/booking_list.html'
    context_object_name = 'bookings'
    paginate_by = 20

    def get_queryset(self):
        queryset = Booking.objects.filter(customer=self.request.user)

        # Filter by status if provided
        status_filter = self.request.GET.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_filter'] = self.request.GET.get('status')
        return context


class ViewBookingView(PermissionRequiredMixin, DetailView):
    """View booking details - requires view_booking permission"""
    permission_required = 'core.view_booking'
    model = Booking
    template_name = 'customer/booking_detail.html'
    context_object_name = 'booking'
    pk_url_kwarg = 'booking_id'

    def dispatch(self, request, *args, **kwargs):
        """Check if user can access this booking"""
        booking_id = kwargs.get('booking_id')
        booking = get_object_or_404(Booking, id=booking_id)
        if not can_access_booking(request.user, booking):
            messages.error(request, 'Access denied to this booking')
            return redirect('core:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        booking = self.object

        # Get status logs
        context['status_logs'] = booking.status_logs.all().order_by('-created_at')

        # Get chat messages if chat is enabled
        chat_messages = []
        if booking.can_chat():
            chat_messages = booking.chat_messages.all().order_by('created_at')

            # Mark messages as read
            ChatMessage.objects.filter(
                booking=booking,
                receiver=self.request.user,
                is_read=False
            ).update(is_read=True)

        context['chat_messages'] = chat_messages
        context['can_cancel'] = can_cancel_booking(self.request.user, booking)

        return context


class CancelBookingView(PermissionRequiredMixin, MessageMixin, ActivityLogMixin, View):
    """Cancel a booking - requires change_booking permission"""
    permission_required = 'core.change_booking'
    success_message = 'Booking cancelled successfully'
    activity_action = 'Cancel Booking'

    def post(self, request, *args, **kwargs):
        booking_id = kwargs.get('booking_id')
        booking = get_object_or_404(Booking, id=booking_id)

        # Check if user can cancel
        if not can_cancel_booking(request.user, booking):
            messages.error(request, 'You cannot cancel this booking')
            return redirect('customer:view_booking', booking_id=booking_id)

        cancellation_reason = request.POST.get('cancellation_reason', '').strip()

        # Update booking
        booking.status = 'cancelled'
        booking.cancelled_at = timezone.now()
        booking.cancellation_reason = cancellation_reason
        booking.save()

        # Log status change
        BookingStatusLog.objects.create(
            booking=booking,
            status='cancelled',
            changed_by=request.user,
            notes=cancellation_reason
        )

        self.log_activity(description=f'Cancelled booking #{booking.id}')
        self.add_success_message()

        return redirect('customer:view_booking', booking_id=booking_id)


class ChatView(PermissionRequiredMixin, TemplateView):
    """Chat view for customer - requires view_chatmessage permission"""
    permission_required = 'core.view_chatmessage'
    template_name = 'chat/chat_room.html'

    def dispatch(self, request, *args, **kwargs):
        """Check if user can access this booking's chat"""
        booking_id = kwargs.get('booking_id')
        booking = get_object_or_404(Booking, id=booking_id)

        if not can_access_booking(request.user, booking):
            messages.error(request, 'Access denied')
            return redirect('core:dashboard')

        if not booking.can_chat():
            messages.error(request, 'Chat is not available for this booking')
            return redirect('customer:view_booking', booking_id=booking_id)

        self.booking = booking
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get chat messages
        chat_messages = self.booking.chat_messages.all().order_by('created_at')

        # Mark messages as read
        ChatMessage.objects.filter(
            booking=self.booking,
            receiver=self.request.user,
            is_read=False
        ).update(is_read=True)

        # Other user is delivery partner
        other_user = self.booking.delivery_partner

        context['booking'] = self.booking
        context['chat_messages'] = chat_messages
        context['other_user'] = other_user

        return context


class ProfileView(PermissionRequiredMixin, MessageMixin, ActivityLogMixin, TemplateView):
    """View and edit customer profile - requires change_user permission"""
    permission_required = 'core.change_user'
    template_name = 'customer/profile.html'
    success_message = 'Profile updated successfully'
    activity_action = 'Update Profile'

    def post(self, request, *args, **kwargs):
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        address = request.POST.get('address', '').strip()

        # Update user
        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.email = email
        request.user.address = address

        # Handle profile picture
        if 'profile_pic' in request.FILES:
            request.user.profile_pic = request.FILES['profile_pic']

        request.user.save()

        self.log_activity(description='Profile updated')
        self.add_success_message()

        return redirect('customer:profile')


# ============================================================================
# API VIEWS (for AJAX requests)
# ============================================================================

class GetBookingStatusAPIView(PermissionRequiredMixin, AjaxResponseMixin, View):
    """Get booking status API - requires view_booking permission"""
    permission_required = 'core.view_booking'

    def get(self, request, *args, **kwargs):
        booking_id = kwargs.get('booking_id')
        booking = get_object_or_404(Booking, id=booking_id)

        # Check access
        if not can_access_booking(request.user, booking):
            return self.json_response({'error': 'Access denied'}, status=403)

        data = {
            'id': booking.id,
            'status': booking.status,
            'status_display': booking.get_status_display(),
            'updated_at': booking.updated_at.isoformat(),
        }

        return self.json_response(data)


class GetUnreadMessagesCountAPIView(PermissionRequiredMixin, AjaxResponseMixin, View):
    """Get count of unread messages API - requires view_chatmessage permission"""
    permission_required = 'core.view_chatmessage'

    def get(self, request, *args, **kwargs):
        booking_id = kwargs.get('booking_id')
        booking = get_object_or_404(Booking, id=booking_id)

        # Check access
        if not can_access_booking(request.user, booking):
            return self.json_response({'error': 'Access denied'}, status=403)

        count = ChatMessage.objects.filter(
            booking=booking,
            receiver=request.user,
            is_read=False
        ).count()

        return self.json_response({'count': count})
