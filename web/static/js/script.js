// Handle JWT token for all requests
$(document).ready(function() {
    // Function to get JWT token
    function getJwtToken() {
        // Try to get token from meta tag first (most reliable)
        let jwtToken = $('meta[name="jwt-token"]').attr('content');
        
        // If not found, try sessionStorage
        if (!jwtToken) {
            jwtToken = sessionStorage.getItem('jwt_token');
        }
        
        // If still not found, try cookie
        if (!jwtToken) {
            jwtToken = document.cookie.replace(/(?:(?:^|.*;)*\s*jwt_token\s*\=\s*([^;]*).*$)|^.*$/, "$1");
            if (jwtToken) {
                // Store in sessionStorage for future use
                sessionStorage.setItem('jwt_token', jwtToken);
            }
        }
        
        return jwtToken;
    }

    // Add token to AJAX requests
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            const jwtToken = getJwtToken();
            if (jwtToken && settings.type === 'POST') {
                xhr.setRequestHeader('Authorization', 'Bearer ' + jwtToken);
            }
        }
    });

    // Handle form submissions
    $('form').on('submit', function(e) {
        const $form = $(this);
        const action = $form.attr('action');
        
        // Add JWT token to form data for non-AJAX submissions
        const jwtToken = getJwtToken();
        if (jwtToken && !$form.hasClass('ajax-form')) {
            $form.append('<input type="hidden" name="jwt_token" value="' + jwtToken + '">');
        }
    });

    // Generic form validation
    function validateForm($form) {
        let errors = [];
        let hasInvalidFields = $form.find('.is-invalid').length > 0;
        
        // Validate all required fields
        $form.find('[required]').each(function() {
            const $field = $(this);
            const fieldName = $field.attr('name');
            const fieldValue = $field.val().trim();
            const fieldLabel = $field.prev('label').text() || fieldName;
            
            if (!fieldValue) {
                errors.push(`${fieldLabel} is required`);
                $field.addClass('is-invalid');
                hasInvalidFields = true;
            }
        });
        
        // Validate field lengths
        $form.find('[maxlength]').each(function() {
            const $field = $(this);
            const fieldValue = $field.val().trim();
            const maxLength = parseInt($field.attr('maxlength'));
            const fieldLabel = $field.prev('label').text() || $field.attr('name');
            
            if (fieldValue && fieldValue.length > maxLength) {
                errors.push(`${fieldLabel} must be ${maxLength} characters or less`);
                $field.addClass('is-invalid');
                hasInvalidFields = true;
            }
        });
        
        // Update submit button state
        const $submitBtn = $form.find('button[type="submit"]');
        $submitBtn.prop('disabled', hasInvalidFields);
        
        return errors;
    }
    
    // Device form specific validation (extends generic validation)
    function validateDeviceForm($form) {
        let errors = validateForm($form);
        let hasInvalidFields = $form.find('.is-invalid').length > 0;
        
        // Device-specific validations
        const ip = $form.find('[name="ip_address"]').val().trim();
        
        if (ip) {
            // IP validation already handled by validateIpAddress function
            // This is just a fallback
            const ipv4Pattern = /^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/;
            const match = ip.match(ipv4Pattern);
            
            if (!match) {
                errors.push('Invalid IP Address format');
                $form.find('[name="ip_address"]').addClass('is-invalid');
                hasInvalidFields = true;
            }
        }
        
        // Update submit button state
        const $submitBtn = $form.find('button[type="submit"]');
        $submitBtn.prop('disabled', hasInvalidFields);
        
        return errors;
    }
    
    // Environment form specific validation
    function validateEnvironmentForm($form) {
        let errors = validateForm($form);
        let hasInvalidFields = $form.find('.is-invalid').length > 0;
        
        // Environment-specific validations
        const port = $form.find('[name="port"]').val().trim();
        
        if (port && (isNaN(port) || port < 1 || port > 65535)) {
            errors.push('Port must be a number between 1 and 65535');
            $form.find('[name="port"]').addClass('is-invalid');
            hasInvalidFields = true;
        }
        
        // Update submit button state
        const $submitBtn = $form.find('button[type="submit"]');
        $submitBtn.prop('disabled', hasInvalidFields);
        
        return errors;
    }
    
    // Test config form specific validation
    function validateTestConfigForm($form) {
        let errors = validateForm($form);
        
        // No specific validations beyond the generic ones yet
        
        return errors;
    }
    
    // Display form errors in modal
    function displayFormErrors($form, errors) {
        // Remove any existing error messages
        $form.find('.form-error').remove();
        $form.find('.is-invalid').removeClass('is-invalid');
        
        if (errors.length === 0) return false;
        
        // Add error header
        const $errorDiv = $('<div class="alert alert-danger form-error mt-3"><ul class="mb-0"></ul></div>');
        const $errorList = $errorDiv.find('ul');
        
        errors.forEach(error => {
            $errorList.append(`<li>${error}</li>`);
            
            // Highlight fields that might be related to the error
            if (error.toLowerCase().includes('name')) {
                $form.find('[name="name"]').addClass('is-invalid');
            }
            if (error.toLowerCase().includes('ip')) {
                $form.find('[name="ip_address"]').addClass('is-invalid');
            }
            if (error.toLowerCase().includes('type')) {
                $form.find('[name="device_type"]').addClass('is-invalid');
            }
        });
        
        // Insert the error div at the top of the form
        $form.prepend($errorDiv);
        return true;
    }

    // Handle AJAX form submissions
    $('.ajax-form').on('submit', function(e) {
        e.preventDefault();
        const $form = $(this);
        const url = $form.attr('action');
        const method = $form.attr('method') || 'POST';
        const $modal = $form.closest('.modal');
        const jwtToken = getJwtToken();
        const isDeleteForm = url.includes('/delete');
        
        if (!jwtToken) {
            alert('Not logged in. Please log in to continue.');
            window.location.href = '/login';
            return;
        }
        
        // Skip validation for delete forms
        if (!isDeleteForm) {
            let errors = [];
            
            // Choose validation based on form type
            if (url.includes('/devices')) {
                errors = validateDeviceForm($form);
            } else if (url.includes('/environments')) {
                errors = validateEnvironmentForm($form);
            } else if (url.includes('/test-configs')) {
                errors = validateTestConfigForm($form);
            } else {
                // Generic validation for other forms
                errors = validateForm($form);
            }
            
            if (errors.length > 0) {
                displayFormErrors($form, errors);
                return;
            }
        }
        
        console.log('Sending request with JWT token:', jwtToken);
        
        // Show loading indicator
        const $submitBtn = $form.find('button[type="submit"]');
        const originalBtnText = $submitBtn.html();
        $submitBtn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Processing...');
        
        $.ajax({
            url: url,
            type: method,
            data: $form.serialize(),
            headers: {
                'Authorization': 'Bearer ' + jwtToken
            },
            beforeSend: function(xhr) {
                // Ensure the Authorization header is set
                xhr.setRequestHeader('Authorization', 'Bearer ' + jwtToken);
            },
            success: function(response) {
                // If the response is HTML (indicating the server didn't return JSON)
                if (typeof response === 'string' && response.includes('<!DOCTYPE html>')) {
                    console.log("Received HTML response instead of JSON, reloading page");
                    location.reload();
                    return;
                }
                
                if (response.redirect) {
                    window.location.href = response.redirect;
                } else if (response.success) {
                    // Handle successful updates
                    if ($modal.length) {
                        $modal.modal('hide');
                    }
                    
                    // Always reload for delete operations
                    if (isDeleteForm) {
                        console.log("Delete operation completed, refreshing page...");
                        setTimeout(function() {
                            location.reload();
                        }, 500); // Short delay to ensure modal is hidden first
                    } else {
                        // Refresh the table for other operations if needed
                        setTimeout(function() {
                            location.reload();
                        }, 500);
                    }
                } else {
                    console.log('Success:', response);
                    // Reload page for delete operations even if response doesn't indicate success
                    if (isDeleteForm) {
                        location.reload();
                    } else {
                        location.reload();
                    }
                }
            },
            error: function(xhr, status, error) {
                // Handle error response
                console.error('Status:', status);
                console.error('Error:', error);
                console.error('Response:', xhr.responseText);
                
                // Restore submit button
                $submitBtn.prop('disabled', false).html(originalBtnText);
                
                const errorData = xhr.responseJSON;
                if (errorData && errorData.error) {
                    if (Array.isArray(errorData.error)) {
                        // Display multiple errors in the form
                        displayFormErrors($form, errorData.error);
                    } else {
                        // Display single error
                        displayFormErrors($form, [errorData.error]);
                    }
                } else if (errorData && errorData.msg) {
                    displayFormErrors($form, [errorData.msg]);
                } else {
                    displayFormErrors($form, ['An error occurred: ' + error]);
                }
            },
            complete: function() {
                // Ensure button is restored if success handler doesn't execute
                setTimeout(function() {
                    $submitBtn.prop('disabled', false).html(originalBtnText);
                }, 1000);
            }
        });
    });

    // Handle AJAX button clicks (for actions like stop test, delete, etc.)
    $('.ajax-button').on('click', function(e) {
        e.preventDefault();
        const $button = $(this);
        const url = $button.data('url');
        const method = $button.data('method') || 'POST';
        const $modal = $button.closest('.modal');
        const jwtToken = getJwtToken();
        
        if (!jwtToken) {
            alert('Not logged in. Please log in to continue.');
            window.location.href = '/login';
            return;
        }
        
        if (!$button.data('confirm') || confirm($button.data('confirm'))) {
            $.ajax({
                url: url,
                method: method,
                headers: {
                    'Authorization': 'Bearer ' + jwtToken
                },
                success: function(response) {
                    if (response.redirect) {
                        window.location.href = response.redirect;
                    } else if (response.success) {
                        // Handle successful updates
                        if ($modal.length) {
                            $modal.modal('hide');
                        }
                        // Refresh the table if needed
                        const $table = $('.table-responsive table');
                        if ($table.length) {
                            location.reload();
                        }
                    } else {
                        console.log('Success:', response);
                    }
                },
                error: function(xhr, status, error) {
                    // Handle error response
                    const errorData = xhr.responseJSON;
                    if (errorData && errorData.error) {
                        alert(errorData.error);
                    } else {
                        console.error('Error:', error);
                    }
                }
            });
        }
    });

    // Check for JWT token on page load for protected pages
    function checkForToken() {
        // Only check on dashboard pages
        if (window.location.pathname.includes('/dashboard')) {
            const jwtToken = getJwtToken();
            if (!jwtToken) {
                console.log('No JWT token found, redirecting to login');
                // If no token, redirect to login
                window.location.href = '/login';
            }
        }
    }

    // Theme toggle functionality
    function toggleTheme() {
        const body = document.body;
        const themeToggle = document.getElementById('theme-toggle');
        
        if (body.classList.contains('dark-theme')) {
            body.classList.remove('dark-theme');
            themeToggle.innerHTML = '🌙 Dark Mode';
            localStorage.setItem('theme', 'light');
        } else {
            body.classList.add('dark-theme');
            themeToggle.innerHTML = '☀️ Light Mode';
            localStorage.setItem('theme', 'dark');
        }
    }

    // No need to add theme toggle button anymore since it's in the menu

    // Check for token on page load
    checkForToken();
});

// Theme toggle functionality
window.toggleTheme = function() {
    const body = document.body;
    const themeToggleText = document.getElementById('theme-toggle-text');
    
    if (body.classList.contains('dark-theme')) {
        body.classList.remove('dark-theme');
        themeToggleText.textContent = 'Toggle Dark Mode';
        localStorage.setItem('theme', 'light');
    } else {
        body.classList.add('dark-theme');
        themeToggleText.textContent = 'Toggle Light Mode';
        localStorage.setItem('theme', 'dark');
    }
}

// Initialize theme based on user preference
document.addEventListener('DOMContentLoaded', function() {
    const savedTheme = localStorage.getItem('theme');
    const themeToggleText = document.getElementById('theme-toggle-text');
    
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-theme');
        if (themeToggleText) {
            themeToggleText.textContent = 'Toggle Light Mode';
        }
    }
    
    // Add specific handler for delete forms to ensure refresh
    $('.delete-form').on('submit', function(e) {
        console.log("Delete form submitted");
        // The ajax-form handler will handle the actual submission
        // This just adds an extra guarantee that the page will refresh
        setTimeout(function() {
            location.reload();
        }, 1000);
    });
    
    // Live validation for device name
    setupDeviceNameValidation();
});

// Entity name real-time validation setup
function setupDeviceNameValidation() {
    // Device validation
    setupEntityNameValidation(
        '#createDeviceModal', 
        'editDeviceModal', 
        window.routes ? window.routes.checkDeviceName : '/dashboard/devices/check-name',
        'Device'
    );
    
    // Environment validation (if on environments page)
    if ($('#createEnvironmentModal').length) {
        setupEntityNameValidation(
            '#createEnvironmentModal', 
            'editEnvironmentModal', 
            window.routes ? window.routes.checkEnvironmentName : '/dashboard/environments/check-name',
            'Environment'
        );
    }
    
    // Test configuration validation (if on test configs page)
    if ($('#createTestConfigModal').length) {
        setupEntityNameValidation(
            '#createTestConfigModal', 
            'editTestConfigModal', 
            window.routes ? window.routes.checkTestConfigName : '/dashboard/test-configs/check-name',
            'Test configuration'
        );
    }
    
    // Validate IP address fields
    $('[name="ip_address"]').on('blur', function() {
        validateIpAddress($(this));
    });
    
    // Validate numeric fields
    $('input[type="number"]').on('blur', function() {
        validateNumericField($(this));
    });
    
    // Add input event listeners to check form validity on any change
    $('.modal form input, .modal form select').on('input change', function() {
        updateSubmitButtonState($(this).closest('form'));
    });
}

// Setup validation for any entity type
function setupEntityNameValidation(createModalSelector, editModalPrefix, checkUrl, entityName) {
    // For create entity form
    $(`${createModalSelector} [name="name"]`).on('blur', function() {
        validateEntityName($(this), null, checkUrl, entityName);
    });
    
    // For edit entity forms
    $(`[id^="${editModalPrefix}"] [name="name"]`).each(function() {
        const $input = $(this);
        const entityId = $input.closest('.modal').attr('id').replace(editModalPrefix, '');
        
        $input.on('blur', function() {
            validateEntityName($input, entityId, checkUrl, entityName);
        });
    });
}

// Validate IP address
function validateIpAddress($input) {
    const ip = $input.val().trim();
    const $formGroup = $input.closest('.mb-3');
    const $form = $input.closest('form');
    
    // Remove any existing feedback
    $formGroup.find('.invalid-feedback, .valid-feedback').remove();
    
    // Create feedback elements
    const $invalidFeedback = $('<div class="invalid-feedback" style="display: block;"></div>');
    
    if (!ip) {
        $input.addClass('is-invalid');
        $invalidFeedback.text('IP Address is required');
        $formGroup.append($invalidFeedback);
    } else {
        // Simple IPv4 validation regex
        const ipv4Pattern = /^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/;
        const match = ip.match(ipv4Pattern);
        
        if (!match) {
            $input.addClass('is-invalid');
            $invalidFeedback.text('Invalid IP Address format');
            $formGroup.append($invalidFeedback);
        } else {
            // Check each octet is between 0 and 255
            const octets = ip.split('.');
            let valid = true;
            
            for (let octet of octets) {
                if (parseInt(octet) > 255) {
                    valid = false;
                    $input.addClass('is-invalid');
                    $invalidFeedback.text('IP Address octets must be between 0 and 255');
                    $formGroup.append($invalidFeedback);
                    break;
                }
            }
            
            if (valid) {
                $input.removeClass('is-invalid');
                $input.addClass('is-valid');
            }
        }
    }
    
    // Update submit button state
    updateSubmitButtonState($form);
}

function validateEntityName($input, entityId = null, checkUrl, entityType = 'Entity') {
    const name = $input.val().trim();
    if (!name) return; // Skip empty values
    
    const $formGroup = $input.closest('.mb-3');
    const $form = $input.closest('form');
    
    // Remove any existing feedback
    $formGroup.find('.invalid-feedback, .valid-feedback').remove();
    
    // Create feedback elements
    const $invalidFeedback = $('<div class="invalid-feedback" style="display: block;"></div>');
    const $validFeedback = $('<div class="valid-feedback" style="display: block;"></div>');
    
    // Add loading indicator
    $input.removeClass('is-valid is-invalid');
    $input.addClass('is-validating');
    
    // Check if name exists
    $.ajax({
        url: checkUrl,
        type: 'GET',
        data: {
            name: name,
            id: entityId
        },
        success: function(response) {
            $input.removeClass('is-validating');
            
            if (!response.valid) {
                $input.removeClass('is-valid');
                $input.addClass('is-invalid');
                $invalidFeedback.text(response.message);
                $formGroup.append($invalidFeedback);
                console.log("Name exists: " + response.message);
            } else {
                $input.removeClass('is-invalid');
                $input.addClass('is-valid');
                $validFeedback.text(`${entityType} name is available`);
                $formGroup.append($validFeedback);
                console.log("Name is valid");
            }
            
            // Update submit button state
            updateSubmitButtonState($form);
        },
        error: function(xhr, status, error) {
            console.error("Validation error:", error);
            $input.removeClass('is-validating is-valid is-invalid');
            // Don't disable submit button on validation error
            updateSubmitButtonState($form);
        }
    });
}

// Function to validate numeric fields
function validateNumericField($input) {
    const value = $input.val().trim();
    const $formGroup = $input.closest('.mb-3');
    const $form = $input.closest('form');
    
    // Remove any existing feedback
    $formGroup.find('.invalid-feedback, .valid-feedback').remove();
    
    // Create feedback elements
    const $invalidFeedback = $('<div class="invalid-feedback" style="display: block;"></div>');
    
    if ($input.prop('required') && !value) {
        $input.addClass('is-invalid');
        $invalidFeedback.text('This field is required');
        $formGroup.append($invalidFeedback);
    } else if (value && isNaN(value)) {
        $input.addClass('is-invalid');
        $invalidFeedback.text('Please enter a valid number');
        $formGroup.append($invalidFeedback);
    } else if (value) {
        // Check min/max if specified
        const min = $input.attr('min');
        const max = $input.attr('max');
        
        if (min && parseFloat(value) < parseFloat(min)) {
            $input.addClass('is-invalid');
            $invalidFeedback.text(`Value must be at least ${min}`);
            $formGroup.append($invalidFeedback);
        } else if (max && parseFloat(value) > parseFloat(max)) {
            $input.addClass('is-invalid');
            $invalidFeedback.text(`Value must be at most ${max}`);
            $formGroup.append($invalidFeedback);
        } else {
            $input.removeClass('is-invalid');
            $input.addClass('is-valid');
        }
    }
    
    // Update submit button state
    updateSubmitButtonState($form);
}

// For backward compatibility
function validateDeviceName($input, deviceId = null) {
    validateEntityName(
        $input, 
        deviceId, 
        window.routes ? window.routes.checkDeviceName : '/dashboard/devices/check-name',
        'Device'
    );
}

// Function to update submit button state
function updateSubmitButtonState($form) {
    const $submitBtn = $form.find('button[type="submit"]');
    const hasInvalidFields = $form.find('.is-invalid').length > 0;
    const isValidating = $form.find('.is-validating').length > 0;
    
    if (hasInvalidFields || isValidating) {
        $submitBtn.prop('disabled', true);
    } else {
        $submitBtn.prop('disabled', false);
    }
}
