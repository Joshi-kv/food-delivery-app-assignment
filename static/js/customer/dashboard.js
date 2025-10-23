/**
 * Customer dashboard JavaScript
 */

$(document).ready(function() {
    // Refresh booking status periodically
    function refreshBookingStatus() {
        // This can be implemented to fetch latest booking status via AJAX
        console.log('Refreshing booking status...');
    }
    
    // Auto-refresh every 30 seconds
    setInterval(refreshBookingStatus, 30000);
    
    // Handle booking card clicks
    $('.booking-card').on('click', function() {
        var bookingId = $(this).data('booking-id');
        if (bookingId) {
            window.location.href = '/customer/booking/' + bookingId + '/';
        }
    });
});

