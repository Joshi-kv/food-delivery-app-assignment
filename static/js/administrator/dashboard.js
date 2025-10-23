/**
 * Administrator dashboard JavaScript
 */

$(document).ready(function() {
    // Refresh statistics periodically
    function refreshStatistics() {
        // This can be implemented to fetch latest statistics via AJAX
        console.log('Refreshing statistics...');
    }
    
    // Auto-refresh every 60 seconds
    setInterval(refreshStatistics, 60000);
    
    // Handle table row clicks
    $('.admin-table tbody tr').on('click', function() {
        var url = $(this).data('url');
        if (url) {
            window.location.href = url;
        }
    });
    
    // Confirm delete actions
    $('.btn-delete').on('click', function(e) {
        if (!confirm('Are you sure you want to delete this item?')) {
            e.preventDefault();
            return false;
        }
    });
});

