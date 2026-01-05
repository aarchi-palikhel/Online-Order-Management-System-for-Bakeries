// static/js/product_detail.js - UPDATED VERSION

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
        
        console.log('Submitting add to cart form...');
        
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
            console.log('=== CART ADD RESPONSE ===');
            console.log('Full response:', data);
            console.log('Cart count keys:', {
                cart_item_count: data.cart_item_count,
                cart_count: data.cart_count,
                cart_total_items: data.cart_total_items
            });
            console.log('==================');
            
            // Get cart count from any possible key
            const cartCount = data.cart_item_count || data.cart_count || data.cart_total_items || 0;
            console.log('Determined cart count:', cartCount);
            
            // Show notification
            if (typeof showGlobalNotification === 'function') {
                console.log('Using global notification');
                showGlobalNotification(
                    data.message || (data.success ? 'Item added to cart!' : 'Failed to add item to cart'),
                    data.success ? 'success' : 'error'
                );
            } else {
                console.log('Using local notification');
                // Fallback to local notification
                showNotification(
                    data.success ? 'success' : 'error',
                    data.message || (data.success ? 'Item added to cart!' : 'Failed to add item to cart')
                );
            }
            
            if (data.success) {
                console.log('Cart add successful');
                
                // UPDATE CART COUNT - FIXED SECTION
                console.log('Attempting to update cart count...');
                console.log('updateCartCount function exists:', typeof updateCartCount);
                
                // Method 1: Try global function first
                if (typeof updateCartCount === 'function') {
                    console.log('Calling global updateCartCount with:', cartCount);
                    updateCartCount(cartCount);
                } else {
                    console.log('Global function not found, using local update');
                    // Method 2: Update directly
                    updateCartCountDirect(cartCount);
                }
                
                // Method 3: Dispatch event for cart.js to listen
                console.log('Dispatching cartUpdated event');
                const cartUpdatedEvent = new CustomEvent('cartUpdated', {
                    detail: { 
                        count: cartCount,
                        item: data.item_added || true,
                        source: 'product_detail'
                    }
                });
                document.dispatchEvent(cartUpdatedEvent);
                
                // Reset quantity after successful add
                const quantityInput = document.getElementById('quantity');
                if (quantityInput) {
                    quantityInput.value = 1;
                    // Trigger price update
                    const event = new Event('input');
                    quantityInput.dispatchEvent(event);
                }
                
                console.log('Cart update completed');
            } else {
                console.log('Cart add failed:', data.message);
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

// Direct cart count update function
function updateCartCountDirect(count) {
    console.log('Updating cart count directly:', count);
    
    // Look for cart count element - check multiple possible selectors
    const cartCountElement = document.getElementById('cart-count');
    if (cartCountElement) {
        console.log('Found cart-count element');
        const currentCount = parseInt(cartCountElement.textContent) || 0;
        console.log('Current count:', currentCount, 'New count:', count);
        
        cartCountElement.textContent = count;
        
        // Add bounce animation when count increases
        if (count > currentCount) {
            cartCountElement.classList.add('animate-bounce');
            setTimeout(() => {
                cartCountElement.classList.remove('animate-bounce');
            }, 1000);
        }
        
        // Show/hide based on count
        if (count > 0) {
            cartCountElement.classList.remove('hidden');
        } else {
            cartCountElement.classList.add('hidden');
        }
    } else {
        console.log('cart-count element not found, checking other elements...');
        // Try other possible cart count elements
        const cartBadges = document.querySelectorAll('[class*="cart"], [id*="cart"]');
        console.log('Other cart elements found:', cartBadges.length);
    }
}

// Local notification function (fallback if global function doesn't exist)
function showNotification(type, message) {
    console.log('Local notification:', type, message);
    
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

// Listen for cart updates from other pages (like cart.js)
document.addEventListener('cartUpdated', function(event) {
    console.log('Product detail received cartUpdated event:', event.detail);
    if (event.detail && event.detail.count !== undefined) {
        // Update our local display
        updateCartCountDirect(event.detail.count);
    }
});

// Export for debugging
window.productDetailModule = {
    initProductDetailPage,
    initQuantityControls,
    initAddToCartAJAX,
    updateCartCountDirect,
    showNotification
};