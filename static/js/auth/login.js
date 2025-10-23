/**
 * Authentication forms JavaScript - Login, Signup, Delivery Signup
 * Handles country code selection, mobile number validation, and form validation
 */

$(document).ready(function() {
    // Country code patterns for validation
    const countryPatterns = {
        '+1': { pattern: /^\d{10}$/, placeholder: '2025551234', length: 10 },
        '+44': { pattern: /^\d{10}$/, placeholder: '7911123456', length: 10 },
        '+91': { pattern: /^\d{10}$/, placeholder: '9876543210', length: 10 },
        '+86': { pattern: /^\d{11}$/, placeholder: '13812345678', length: 11 },
        '+81': { pattern: /^\d{10}$/, placeholder: '9012345678', length: 10 },
        '+49': { pattern: /^\d{10,11}$/, placeholder: '15112345678', length: '10-11' },
        '+33': { pattern: /^\d{9}$/, placeholder: '612345678', length: 9 },
        '+61': { pattern: /^\d{9}$/, placeholder: '412345678', length: 9 },
        '+7': { pattern: /^\d{10}$/, placeholder: '9123456789', length: 10 },
        '+55': { pattern: /^\d{11}$/, placeholder: '11987654321', length: 11 },
        '+52': { pattern: /^\d{10}$/, placeholder: '5512345678', length: 10 },
        '+34': { pattern: /^\d{9}$/, placeholder: '612345678', length: 9 },
        '+39': { pattern: /^\d{10}$/, placeholder: '3123456789', length: 10 },
        '+82': { pattern: /^\d{10}$/, placeholder: '1012345678', length: 10 },
        '+65': { pattern: /^\d{8}$/, placeholder: '81234567', length: 8 },
        '+60': { pattern: /^\d{9,10}$/, placeholder: '123456789', length: '9-10' },
        '+66': { pattern: /^\d{9}$/, placeholder: '812345678', length: 9 },
        '+63': { pattern: /^\d{10}$/, placeholder: '9171234567', length: 10 },
        '+62': { pattern: /^\d{10,12}$/, placeholder: '81234567890', length: '10-12' },
        '+84': { pattern: /^\d{9,10}$/, placeholder: '912345678', length: '9-10' },
        '+971': { pattern: /^\d{9}$/, placeholder: '501234567', length: 9 },
        '+966': { pattern: /^\d{9}$/, placeholder: '501234567', length: 9 },
        '+27': { pattern: /^\d{9}$/, placeholder: '712345678', length: 9 },
        '+234': { pattern: /^\d{10}$/, placeholder: '8012345678', length: 10 },
        '+20': { pattern: /^\d{10}$/, placeholder: '1001234567', length: 10 }
    };

    // Update mobile number placeholder based on country code
    function updateMobilePlaceholder() {
        var countryCode = $('#country_code').val();
        var pattern = countryPatterns[countryCode];
        if (pattern) {
            $('#mobile_number').attr('placeholder', pattern.placeholder);
            $('#mobile_number_help').text('Example: ' + pattern.placeholder + ' (' + pattern.length + ' digits)');
        }
    }

    // Country code change handler
    $('#country_code').on('change', function() {
        updateMobilePlaceholder();
        $('#mobile_number').val(''); // Clear mobile number when country changes
        $('#mobile_number').removeClass('is-valid is-invalid');
    });

    // Initialize placeholder on page load
    updateMobilePlaceholder();

    // Validate mobile number on input
    $('#mobile_number').on('input', function() {
        // Only allow digits
        this.value = this.value.replace(/[^0-9]/g, '');

        // Real-time validation
        var countryCode = $('#country_code').val();
        var mobileNumber = $(this).val();
        var pattern = countryPatterns[countryCode];

        if (mobileNumber.length > 0 && pattern) {
            if (pattern.pattern.test(mobileNumber)) {
                $(this).removeClass('is-invalid').addClass('is-valid');
                $('#mobile_number_error').hide();
            } else {
                $(this).removeClass('is-valid').addClass('is-invalid');
                $('#mobile_number_error').text('Invalid format. Example: ' + pattern.placeholder).show();
            }
        } else {
            $(this).removeClass('is-valid is-invalid');
            $('#mobile_number_error').hide();
        }
    });

    // Validate first name
    $('#first_name').on('input', function() {
        var value = $(this).val().trim();
        if (value.length >= 2 && /^[a-zA-Z\s\-']+$/.test(value)) {
            $(this).removeClass('is-invalid').addClass('is-valid');
            $('#first_name_error').hide();
        } else if (value.length > 0) {
            $(this).removeClass('is-valid').addClass('is-invalid');
            $('#first_name_error').text('Must be at least 2 letters').show();
        } else {
            $(this).removeClass('is-valid is-invalid');
            $('#first_name_error').hide();
        }
    });

    // Validate last name
    $('#last_name').on('input', function() {
        var value = $(this).val().trim();
        if (value.length === 0) {
            $(this).removeClass('is-valid is-invalid');
            $('#last_name_error').hide();
        } else if (value.length >= 2 && /^[a-zA-Z\s\-']+$/.test(value)) {
            $(this).removeClass('is-invalid').addClass('is-valid');
            $('#last_name_error').hide();
        } else {
            $(this).removeClass('is-valid').addClass('is-invalid');
            $('#last_name_error').text('Must be at least 2 letters').show();
        }
    });

    // Validate email
    $('#email').on('input', function() {
        var value = $(this).val().trim();
        var emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

        if (value.length === 0) {
            $(this).removeClass('is-valid is-invalid');
            $('#email_error').hide();
        } else if (emailPattern.test(value)) {
            $(this).removeClass('is-invalid').addClass('is-valid');
            $('#email_error').hide();
        } else {
            $(this).removeClass('is-valid').addClass('is-invalid');
            $('#email_error').text('Invalid email format').show();
        }
    });

    // OTP input validation (auto-submit disabled)
    $('#otp').on('input', function() {
        // Only allow digits
        this.value = this.value.replace(/[^0-9]/g, '');

        // Validate OTP format
        var otp = $(this).val();
        if (otp.length === 4) {
            $(this).removeClass('is-invalid').addClass('is-valid');
            $('#otp_error').hide();
        } else if (otp.length > 0) {
            $(this).removeClass('is-valid').addClass('is-invalid');
            $('#otp_error').text('OTP must be 4 digits').show();
        } else {
            $(this).removeClass('is-valid is-invalid');
            $('#otp_error').hide();
        }
    });

    // Form validation on submit
    $('#loginForm, #signupForm, #deliverySignupForm').on('submit', function(e) {
        var isValid = true;
        var step = $('input[name="step"]').val();

        if (step === 'send_otp') {
            // Validate mobile number
            var countryCode = $('#country_code').val();
            var mobileNumber = $('#mobile_number').val();
            var pattern = countryPatterns[countryCode];

            if (!mobileNumber) {
                $('#mobile_number').addClass('is-invalid');
                $('#mobile_number_error').text('Mobile number is required').show();
                isValid = false;
            } else if (pattern && !pattern.pattern.test(mobileNumber)) {
                $('#mobile_number').addClass('is-invalid');
                $('#mobile_number_error').text('Invalid format. Example: ' + pattern.placeholder).show();
                isValid = false;
            }

            // Validate first name (for signup forms)
            var firstName = $('#first_name').val();
            if ($('#first_name').length && (!firstName || firstName.trim().length < 2)) {
                $('#first_name').addClass('is-invalid');
                $('#first_name_error').text('First name is required (min 2 letters)').show();
                isValid = false;
            }

            // Validate email if provided (for signup forms)
            var email = $('#email').val();
            if ($('#email').length && email && !/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(email)) {
                $('#email').addClass('is-invalid');
                $('#email_error').text('Invalid email format').show();
                isValid = false;
            }
        } else if (step === 'verify_otp') {
            // Validate OTP
            var otp = $('#otp').val();
            if (!otp || otp.length !== 4) {
                $('#otp').addClass('is-invalid');
                $('#otp_error').text('Please enter 4-digit OTP').show();
                isValid = false;
            }
        }

        if (!isValid) {
            e.preventDefault();
            return false;
        }
    });

    // Make country code dropdown searchable (if Select2 is available)
    if ($.fn.select2) {
        $('#country_code').select2({
            width: '100%',
            placeholder: 'Select country code',
            allowClear: false
        });
    }
});

