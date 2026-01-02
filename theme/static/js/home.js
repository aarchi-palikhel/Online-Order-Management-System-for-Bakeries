// static/js/home.js

document.addEventListener('DOMContentLoaded', function() {
    initHomePageAJAX();
});

function initHomePageAJAX() {
    // Add to Cart functionality for home page featured products
    const addToCartForms = document.querySelectorAll('.add-to-cart-form-home');
    
    addToCartForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const productId = this.getAttribute('data-product-id');
            const submitBtn = this.querySelector('.add-to-cart-btn-home');
            const productCard = this.closest('.featured-product');
            const productName = productCard.querySelector('h3').textContent.trim();
            
            // Save original button text
            const originalText = submitBtn.textContent;
            
            // Show loading state
            submitBtn.textContent = 'Adding...';
            submitBtn.disabled = true;
            submitBtn.classList.add('opacity-75', 'cursor-not-allowed');
            
            // Submit form via AJAX
            fetch(this.action, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': this.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: new FormData(this)
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    // Show success notification
                    if (typeof showGlobalNotification === 'function') {
                        showGlobalNotification(`${productName} added to cart!`, 'success');
                    } else {
                        showLocalNotification('success', `${productName} added to cart!`);
                    }
                    
                    // Update cart count in navbar
                    if (typeof updateCartCount === 'function') {
                        updateCartCount(data.cart_count);
                    }
                    
                } else {
                    // Show error notification
                    if (typeof showGlobalNotification === 'function') {
                        showGlobalNotification(data.message || 'Could not add item to cart', 'error');
                    } else {
                        showLocalNotification('error', data.message || 'Could not add item to cart');
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                if (typeof showGlobalNotification === 'function') {
                    showGlobalNotification('An error occurred. Please try again.', 'error');
                } else {
                    showLocalNotification('error', 'An error occurred. Please try again.');
                }
            })
            .finally(() => {
                // Restore button state
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
                submitBtn.classList.remove('opacity-75', 'cursor-not-allowed');
            });
        });
    });
}

// Local notification function for home page
function showLocalNotification(type, message) {
    const notificationsContainer = document.getElementById('ajax-notifications');
    if (!notificationsContainer) return;
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `p-4 rounded-lg shadow-lg transform transition-all duration-300 animate-slide-in ${
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
    notificationsContainer.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.classList.add('opacity-0');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}