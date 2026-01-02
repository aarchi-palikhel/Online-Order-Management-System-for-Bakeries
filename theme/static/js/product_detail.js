// static/js/prod_details.js

// Product Detail Page JavaScript
document.addEventListener('DOMContentLoaded', function() {
    initProductDetailPage();
});

function initProductDetailPage() {
    // Initialize quantity controls
    initQuantityControls();
    
    // Initialize AJAX add to cart
    initAddToCartAJAX();
}

function initQuantityControls() {
    const quantityInput = document.getElementById('quantity');
    const totalPriceElement = document.getElementById('total-price');
    
    if (!quantityInput || !totalPriceElement) return;
    
    // Extract base price from the initial total price text
    const initialTotalText = totalPriceElement.textContent.trim();
    const basePrice = parseFloat(initialTotalText.replace(/[^0-9.-]+/g, "")) || 0;
    
    function updateTotalPrice() {
        const quantity = parseInt(quantityInput.value) || 1;
        const total = basePrice * quantity;
        totalPriceElement.textContent = "Rs. " + total.toFixed(2);
    }
    
    // Increase quantity button
    const increaseBtn = document.querySelector('.increase-quantity');
    if (increaseBtn) {
        increaseBtn.addEventListener('click', function(e) {
            e.preventDefault();
            let currentValue = parseInt(quantityInput.value) || 1;
            if (currentValue < 10) {
                quantityInput.value = currentValue + 1;
                updateTotalPrice();
            }
        });
    }
    
    // Decrease quantity button
    const decreaseBtn = document.querySelector('.decrease-quantity');
    if (decreaseBtn) {
        decreaseBtn.addEventListener('click', function(e) {
            e.preventDefault();
            let currentValue = parseInt(quantityInput.value) || 1;
            if (currentValue > 1) {
                quantityInput.value = currentValue - 1;
                updateTotalPrice();
            }
        });
    }
    
    // Update on direct input
    quantityInput.addEventListener('input', updateTotalPrice);
    
    // Initial price update
    updateTotalPrice();
}

function initAddToCartAJAX() {
    const addToCartForm = document.getElementById('add-to-cart-form');
    if (!addToCartForm) return;
    
    addToCartForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const submitBtn = this.querySelector('button[type="submit"]');
        const addToCartText = document.getElementById('add-to-cart-text');
        const addToCartSpinner = document.getElementById('add-to-cart-spinner');
        
        if (!submitBtn || !addToCartText) return;
        
        const originalText = addToCartText.textContent;
        
        // Show loading state
        submitBtn.disabled = true;
        addToCartText.textContent = 'Adding...';
        if (addToCartSpinner) {
            addToCartSpinner.classList.remove('hidden');
        }
        
        // Submit via AJAX
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
            // Use global notification function from base.html
            if (typeof showGlobalNotification === 'function') {
                showGlobalNotification(
                    data.message || (data.success ? 'Item added to cart!' : 'Failed to add item to cart'),
                    data.success ? 'success' : 'error'
                );
            } else {
                // Fallback to local notification
                showNotification(
                    data.success ? 'success' : 'error',
                    data.message || (data.success ? 'Item added to cart!' : 'Failed to add item to cart')
                );
            }
            
            if (data.success) {
                // Update cart count in navbar
                if (typeof updateCartCount === 'function') {
                    updateCartCount(data.cart_item_count || 0);
                }
                
                // Reset quantity after successful add
                const quantityInput = document.getElementById('quantity');
                if (quantityInput) {
                    quantityInput.value = 1;
                    // Trigger price update
                    const event = new Event('input');
                    quantityInput.dispatchEvent(event);
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            if (typeof showGlobalNotification === 'function') {
                showGlobalNotification('An error occurred. Please try again.', 'error');
            } else {
                showNotification('error', 'An error occurred. Please try again.');
            }
        })
        .finally(() => {
            // Restore button state
            submitBtn.disabled = false;
            addToCartText.textContent = originalText;
            if (addToCartSpinner) {
                addToCartSpinner.classList.add('hidden');
            }
        });
    });
}

// Local notification function (fallback if global function doesn't exist)
function showNotification(type, message) {
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