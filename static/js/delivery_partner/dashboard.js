/**
 * Delivery Partner dashboard JavaScript
 */

$(document).ready(function() {
    // Refresh delivery status periodically
    function refreshDeliveryStatus() {
        // This can be implemented to fetch latest delivery status via AJAX
        console.log('Refreshing delivery status...');
    }
    
    // Auto-refresh every 30 seconds
    setInterval(refreshDeliveryStatus, 30000);
    
    // Handle delivery card clicks
    $('.delivery-card').on('click', function() {
        var deliveryId = $(this).data('delivery-id');
        if (deliveryId) {
            window.location.href = '/delivery-partner/delivery/' + deliveryId + '/';
        }
    });
});

