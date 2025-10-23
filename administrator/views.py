"""
Administrator-specific views - Class-Based Views
Following hisense-hiconnect pattern with Django's PermissionRequiredMixin
"""
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.utils import timezone
from django.db.models import Count, Q
from django.views.generic import TemplateView, ListView, DetailView, View

from core.models import User, Booking, BookingStatusLog
from core.mixins import MessageMixin, ActivityLogMixin, AjaxResponseMixin
from core.helpers import get_available_delivery_partners


class AdminDashboardView(PermissionRequiredMixin, TemplateView):
    """Admin dashboard - requires view_booking permission"""
    permission_required = 'core.view_booking'
    template_name = 'administrator/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get all bookings
        bookings = Booking.objects.all().order_by('-created_at')

        # Get statistics
        total_bookings = bookings.count()
        pending_bookings = bookings.filter(status='pending').count()
        assigned_bookings = bookings.filter(status='assigned').count()
        active_bookings = bookings.filter(status__in=['started', 'reached', 'collected']).count()
        completed_bookings = bookings.filter(status='delivered').count()
        cancelled_bookings = bookings.filter(status='cancelled').count()

        # Get user statistics
        total_customers = User.objects.filter(role='customer').count()
        total_delivery_partners = User.objects.filter(role='delivery_partner').count()
        total_admins = User.objects.filter(role='admin').count()

        # Today's statistics
        today = timezone.now().date()
        today_bookings = bookings.filter(created_at__date=today).count()
        today_completed = bookings.filter(delivered_at__date=today).count()

        context['bookings'] = bookings[:10]  # Latest 10 bookings
        context['total_bookings'] = total_bookings
        context['pending_bookings'] = pending_bookings
        context['assigned_bookings'] = assigned_bookings
        context['active_bookings'] = active_bookings
        context['completed_bookings'] = completed_bookings
        context['cancelled_bookings'] = cancelled_bookings
        context['total_customers'] = total_customers
        context['total_delivery_partners'] = total_delivery_partners
        context['total_admins'] = total_admins
        context['today_bookings'] = today_bookings
        context['today_completed'] = today_completed

        return context


class BookingListView(PermissionRequiredMixin, ListView):
    """List all bookings - requires view_booking permission"""
    permission_required = 'core.view_booking'
    model = Booking
    template_name = 'administrator/booking_list.html'
    context_object_name = 'bookings'
    paginate_by = 20

    def get_queryset(self):
        queryset = Booking.objects.all()

        # Filter by status if provided
        status_filter = self.request.GET.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Search by booking ID or customer mobile
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(id__icontains=search_query) |
                Q(customer__mobile_number__icontains=search_query) |
                Q(delivery_partner__mobile_number__icontains=search_query)
            )

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_filter'] = self.request.GET.get('status')
        context['search_query'] = self.request.GET.get('search')
        return context


class ViewBookingView(PermissionRequiredMixin, DetailView):
    """View booking details - requires view_booking permission"""
    permission_required = 'core.view_booking'
    model = Booking
    template_name = 'administrator/booking_detail.html'
    context_object_name = 'booking'
    pk_url_kwarg = 'booking_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        booking = self.object

        # Get status logs
        context['status_logs'] = booking.status_logs.all().order_by('-created_at')

        # Get available delivery partners for assignment
        context['available_delivery_partners'] = get_available_delivery_partners()

        return context


class AssignBookingView(PermissionRequiredMixin, MessageMixin, ActivityLogMixin, View):
    """Assign booking to delivery partner - requires change_booking permission"""
    permission_required = 'core.change_booking'
    activity_action = 'Assign Booking'

    def post(self, request, *args, **kwargs):
        booking_id = kwargs.get('booking_id')
        booking = get_object_or_404(Booking, id=booking_id)
        delivery_partner_id = request.POST.get('delivery_partner_id')

        if not delivery_partner_id:
            messages.error(request, 'Please select a delivery partner')
            return redirect('administrator:view_booking', booking_id=booking_id)

        delivery_partner = get_object_or_404(User, id=delivery_partner_id, role='delivery_partner')

        # Assign booking
        booking.delivery_partner = delivery_partner
        booking.status = 'assigned'
        booking.assigned_at = timezone.now()
        booking.save()

        # Log status change
        BookingStatusLog.objects.create(
            booking=booking,
            status='assigned',
            changed_by=request.user,
            notes=f'Assigned to {delivery_partner.get_full_name()}'
        )

        self.log_activity(description=f'Assigned booking #{booking.id} to {delivery_partner.mobile_number}')
        messages.success(request, f'Booking assigned to {delivery_partner.get_full_name()}')

        return redirect('administrator:view_booking', booking_id=booking_id)


class UserListView(PermissionRequiredMixin, ListView):
    """List all users - requires view_user permission"""
    permission_required = 'core.view_user'
    model = User
    template_name = 'administrator/user_list.html'
    context_object_name = 'users'
    paginate_by = 20

    def get_queryset(self):
        # Filter by role
        role_filter = self.request.GET.get('role', 'all')

        if role_filter == 'all':
            queryset = User.objects.all()
        else:
            queryset = User.objects.filter(role=role_filter)

        # Search by mobile number or name
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(mobile_number__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query)
            )

        return queryset.order_by('-date_joined')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['role_filter'] = self.request.GET.get('role', 'all')
        context['search_query'] = self.request.GET.get('search')
        return context


class UserDetailView(PermissionRequiredMixin, DetailView):
    """View user details - requires view_user permission"""
    permission_required = 'core.view_user'
    model = User
    template_name = 'administrator/user_detail.html'
    context_object_name = 'user_obj'
    pk_url_kwarg = 'user_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object

        # Get user's bookings
        if user.role == 'customer':
            bookings = Booking.objects.filter(customer=user)
        elif user.role == 'delivery_partner':
            bookings = Booking.objects.filter(delivery_partner=user)
        else:
            bookings = Booking.objects.none()

        context['bookings'] = bookings.order_by('-created_at')[:10]

        return context


class ReportsView(PermissionRequiredMixin, TemplateView):
    """Reports and analytics - requires view_booking permission"""
    permission_required = 'core.view_booking'
    template_name = 'administrator/reports.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Date range filter
        from_date = self.request.GET.get('from_date')
        to_date = self.request.GET.get('to_date')

        bookings = Booking.objects.all()

        if from_date:
            bookings = bookings.filter(created_at__date__gte=from_date)
        if to_date:
            bookings = bookings.filter(created_at__date__lte=to_date)

        # Statistics
        total_bookings = bookings.count()
        completed_bookings = bookings.filter(status='delivered').count()
        cancelled_bookings = bookings.filter(status='cancelled').count()
        pending_bookings = bookings.filter(status='pending').count()

        # Delivery partner performance
        delivery_partner_stats = User.objects.filter(role='delivery_partner').annotate(
            total_deliveries=Count('assigned_bookings'),
            completed_deliveries=Count('assigned_bookings', filter=Q(assigned_bookings__status='delivered'))
        ).order_by('-completed_deliveries')[:10]

        # Customer statistics
        customer_stats = User.objects.filter(role='customer').annotate(
            total_bookings=Count('customer_bookings')
        ).order_by('-total_bookings')[:10]

        context['total_bookings'] = total_bookings
        context['completed_bookings'] = completed_bookings
        context['cancelled_bookings'] = cancelled_bookings
        context['pending_bookings'] = pending_bookings
        context['delivery_partner_stats'] = delivery_partner_stats
        context['customer_stats'] = customer_stats
        context['from_date'] = from_date
        context['to_date'] = to_date

        return context


# ============================================================================
# API VIEWS (for AJAX requests)
# ============================================================================

class GetDeliveryPartnersAPIView(PermissionRequiredMixin, AjaxResponseMixin, View):
    """Get list of available delivery partners API - requires view_user permission"""
    permission_required = 'core.view_user'

    def get(self, request, *args, **kwargs):
        delivery_partners = get_available_delivery_partners()

        data = [{
            'id': dp.id,
            'name': dp.get_full_name(),
            'mobile_number': dp.mobile_number,
        } for dp in delivery_partners]

        return self.json_response({'delivery_partners': data})


class GetBookingStatusAPIView(PermissionRequiredMixin, AjaxResponseMixin, View):
    """Get booking status API - requires view_booking permission"""
    permission_required = 'core.view_booking'

    def get(self, request, *args, **kwargs):
        booking_id = kwargs.get('booking_id')
        booking = get_object_or_404(Booking, id=booking_id)

        data = {
            'id': booking.id,
            'status': booking.status,
            'status_display': booking.get_status_display(),
            'updated_at': booking.updated_at.isoformat(),
        }

        return self.json_response(data)
