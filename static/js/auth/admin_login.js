/**
 * Admin login page JavaScript
 */

$(document).ready(function() {
    // Toggle password visibility
    $('#togglePassword').on('click', function() {
        var passwordField = $('#password');
        var icon = $(this).find('i');

        if (passwordField.attr('type') === 'password') {
            passwordField.attr('type', 'text');
            icon.removeClass('fa-eye').addClass('fa-eye-slash');
        } else {
            passwordField.attr('type', 'password');
            icon.removeClass('fa-eye-slash').addClass('fa-eye');
        }
    });

    // Email validation
    function isValidEmail(email) {
        var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    // Form validation
    $('#adminLoginForm').on('submit', function(e) {
        var email = $('#email').val().trim();
        var password = $('#password').val();

        // Validate email
        if (!email) {
            e.preventDefault();
            alert('Please enter your email address');
            return false;
        }

        if (!isValidEmail(email)) {
            e.preventDefault();
            alert('Please enter a valid email address');
            return false;
        }

        // Validate password
        if (!password) {
            e.preventDefault();
            alert('Please enter your password');
            return false;
        }

        if (password.length < 6) {
            e.preventDefault();
            alert('Password must be at least 6 characters long');
            return false;
        }
    });
});

