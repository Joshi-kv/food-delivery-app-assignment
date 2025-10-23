"""
Delivery Partner-specific views - Class-Based Views
Following hisense-hiconnect pattern with Django's PermissionRequiredMixin
"""
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.utils import timezone
from django.views.generic import TemplateView, ListView, DetailView, View

from core.models import Booking, ChatMessage, BookingStatusLog
from core.mixins import MessageMixin, ActivityLogMixin, AjaxResponseMixin
from core.helpers import can_access_booking, can_update_booking_status


class DeliveryDashboardView(PermissionRequiredMixin, TemplateView):
    """Delivery partner dashboard - requires view_booking permission"""
    permission_required = 'core.view_booking'
    template_name = 'delivery_partner/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get delivery partner's bookings
        bookings = Booking.objects.filter(delivery_partner=self.request.user).order_by('-created_at')

        # Get statistics
        total_bookings = bookings.count()
        active_bookings = bookings.filter(status__in=['assigned', 'started', 'reached', 'collected']).count()
        completed_bookings = bookings.filter(status='delivered').count()

        # Today's deliveries
        today_bookings = bookings.filter(created_at__date=timezone.now().date())

        context['bookings'] = bookings[:10]  # Latest 10 bookings
        context['total_bookings'] = total_bookings
        context['active_bookings'] = active_bookings
        context['completed_bookings'] = completed_bookings
        context['today_bookings'] = today_bookings.count()

        return context


class DeliveryListView(PermissionRequiredMixin, ListView):
    """List delivery partner's assigned deliveries - requires view_booking permission"""
    permission_required = 'core.view_booking'
    model = Booking
    template_name = 'delivery_partner/delivery_list.html'
    context_object_name = 'bookings'
    paginate_by = 20

    def get_queryset(self):
        queryset = Booking.objects.filter(delivery_partner=self.request.user)

        # Filter by status if provided
        status_filter = self.request.GET.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_filter'] = self.request.GET.get('status')
        return context


class ViewDeliveryView(PermissionRequiredMixin, DetailView):
    """View delivery details - requires view_booking permission"""
    permission_required = 'core.view_booking'
    model = Booking
    template_name = 'delivery_partner/delivery_detail.html'
    context_object_name = 'booking'
    pk_url_kwarg = 'booking_id'

    def dispatch(self, request, *args, **kwargs):
        """Check if user can access this booking"""
        booking_id = kwargs.get('booking_id')
        booking = get_object_or_404(Booking, id=booking_id)

        if not can_access_booking(request.user, booking):
            messages.error(request, 'Access denied')
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
        context['can_update_status'] = can_update_booking_status(self.request.user, booking)

        return context


class UpdateBookingStatusView(PermissionRequiredMixin, MessageMixin, ActivityLogMixin, View):
    """Update booking status - requires change_booking permission"""
    permission_required = 'core.change_booking'
    activity_action = 'Update Booking Status'

    def post(self, request, *args, **kwargs):
        booking_id = kwargs.get('booking_id')
        booking = get_object_or_404(Booking, id=booking_id)

        # Check if user can update status
        if not can_update_booking_status(request.user, booking):
            messages.error(request, 'You cannot update this booking status')
            return redirect('delivery_partner:view_delivery', booking_id=booking_id)

        new_status = request.POST.get('status', '').strip()
        notes = request.POST.get('notes', '').strip()

        # Validate status transition
        valid_statuses = ['started', 'reached', 'collected', 'delivered']
        if new_status not in valid_statuses:
            messages.error(request, 'Invalid status')
            return redirect('delivery_partner:view_delivery', booking_id=booking_id)

        # Update booking
        booking.status = new_status

        # Update timestamp based on status
        if new_status == 'started':
            booking.started_at = timezone.now()
        elif new_status == 'reached':
            booking.reached_at = timezone.now()
        elif new_status == 'collected':
            booking.collected_at = timezone.now()
        elif new_status == 'delivered':
            booking.delivered_at = timezone.now()

        booking.save()

        # Log status change
        BookingStatusLog.objects.create(
            booking=booking,
            status=new_status,
            changed_by=request.user,
            notes=notes
        )

        self.log_activity(description=f'Updated booking #{booking.id} to {new_status}')
        messages.success(request, f'Booking status updated to {new_status}')

        return redirect('delivery_partner:view_delivery', booking_id=booking_id)


class ChatView(PermissionRequiredMixin, TemplateView):
    """Chat view for delivery partner - requires view_chatmessage permission"""
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
            return redirect('delivery_partner:view_delivery', booking_id=booking_id)

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

        # Other user is customer
        other_user = self.booking.customer

        context['booking'] = self.booking
        context['chat_messages'] = chat_messages
        context['other_user'] = other_user

        return context


class ProfileView(PermissionRequiredMixin, MessageMixin, ActivityLogMixin, TemplateView):
    """View and edit delivery partner profile - requires change_user permission"""
    permission_required = 'core.change_user'
    template_name = 'delivery_partner/profile.html'
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

        return redirect('delivery_partner:profile')


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
