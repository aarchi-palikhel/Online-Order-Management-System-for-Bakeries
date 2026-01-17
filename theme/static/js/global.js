// static/js/global.js

// Global function to update cart count
function updateCartCount(count) {
    const cartCountElement = document.getElementById('cart-count');
    if (cartCountElement) {
        cartCountElement.textContent = count;
        if (count > 0) {
            cartCountElement.classList.remove('hidden');
            // Add bounce animation
            cartCountElement.classList.add('animate-bounce');
            setTimeout(() => {
                cartCountElement.classList.remove('animate-bounce');
            }, 1000);
        } else {
            cartCountElement.classList.add('hidden');
        }
    }
}

// Global function to show notifications
function showGlobalNotification(message, type = 'success') {
    // Create notification container if it doesn't exist
    let notificationContainer = document.getElementById('global-notification-container');
    if (!notificationContainer) {
        notificationContainer = document.createElement('div');
        notificationContainer.id = 'global-notification-container';
        notificationContainer.className = 'fixed top-4 right-4 z-50 space-y-2';
        document.body.appendChild(notificationContainer);
    }
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `p-4 rounded-lg shadow-lg transform transition-all duration-300 ${
        type === 'success' 
            ? 'bg-green-500 text-white' 
            : 'bg-red-500 text-white'
    }`;
    notification.innerHTML = `
        <div class="flex items-center">
            ${type === 'success' ? '✓' : '✗'}
            <span class="ml-2">${message}</span>
        </div>
    `;
    
    // Add to container
    notificationContainer.appendChild(notification);
    
    // Show with animation
    setTimeout(() => {
        notification.classList.remove('opacity-0');
    }, 10);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

// Get CSRF token for AJAX requests
function getCSRFToken() {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    return csrfToken ? csrfToken.value : '';
}

// Set up CSRF token for AJAX requests globally
const csrftoken = getCSRFToken();

// Add CSRF token to all AJAX requests if using jQuery
if (typeof jQuery !== 'undefined') {
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
}

// For Fetch API
function fetchWithCSRF(url, options = {}) {
    const defaultOptions = {
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json',
        }
    };
    
    const mergedOptions = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers
        }
    };
    
    
    return fetch(url, mergedOptions);
}

// Mobile Menu Toggle
document.addEventListener('DOMContentLoaded', function() {
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');

    if (mobileMenuBtn && mobileMenu) {
        mobileMenuBtn.addEventListener('click', function() {
            // Toggle visibility
            mobileMenu.classList.toggle('hidden');
        });
    }
});