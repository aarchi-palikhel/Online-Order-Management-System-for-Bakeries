// static/js/cart.js - FIXED VERSION WITH SMOOTH ANIMATION

console.log('Cart JS loaded - version 1');

// Listen for cart updates from product_detail.js
document.addEventListener('cartUpdated', function(event) {
    console.log('Cart update event received:', event.detail);
    
    if (event.detail && event.detail.count !== undefined) {
        if (typeof updateCartCount === 'function') {
            updateCartCount(event.detail.count);
        } else {
            console.warn('updateCartCount function not available in cart.js');
        }
    }
});

// Simple notification
function showNotification(message, type = 'success') {
    const container = document.getElementById('ajax-notifications');
    if (!container) return;
    
    const notification = document.createElement('div');
    notification.className = `p-4 rounded-lg shadow-lg animate-slide-in-right ${
        type === 'success' ? 'bg-green-500' : 'bg-red-500'
    } text-white`;
    notification.textContent = message;
    
    container.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Update cart quantity with smoother animation
async function updateQuantity(form, change) {
    // Check if already updating
    if (window.cartIsUpdating) return;
    window.cartIsUpdating = true;
    
    const quantitySpan = form.querySelector('.quantity-display');
    const currentQty = parseInt(quantitySpan.textContent);
    const newQty = currentQty + change;
    
    if (newQty < 1 || newQty > 20) {
        window.cartIsUpdating = false;
        return;
    }
    
    // Visual feedback with smooth animation
    const minusBtn = form.querySelector('.quantity-minus');
    const plusBtn = form.querySelector('.quantity-plus');
    
    // Add click animation
    if (change > 0) {
        plusBtn.style.transform = 'scale(0.95)';
    } else {
        minusBtn.style.transform = 'scale(0.95)';
    }
    
    // Smooth transition for quantity display
    quantitySpan.style.opacity = '0.5';
    quantitySpan.style.transform = 'translateY(-2px)';
    quantitySpan.textContent = newQty;
    
    setTimeout(() => {
        quantitySpan.style.opacity = '1';
        quantitySpan.style.transform = 'translateY(0)';
    }, 150);
    
    // Re-enable button animation
    setTimeout(() => {
        if (minusBtn) minusBtn.style.transform = '';
        if (plusBtn) plusBtn.style.transform = '';
    }, 100);
    
    const formData = new FormData(form);
    formData.set('quantity', newQty);
    
    try {
        const response = await fetch(form.action, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': formData.get('csrfmiddlewaretoken')
            },
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Update cart totals with animation
            if (data.total_price !== undefined) {
                // Animate price updates
                const priceElements = document.querySelectorAll('.flex.justify-between span');
                priceElements.forEach(span => {
                    if (span.textContent.includes('Rs.')) {
                        const parent = span.closest('.flex.justify-between');
                        if (parent) {
                            const text = parent.textContent;
                            if (text.includes('Items') || text.includes('Total')) {
                                // Animate the price change
                                span.style.opacity = '0.5';
                                span.style.transform = 'translateY(-2px)';
                                setTimeout(() => {
                                    span.textContent = `Rs. ${data.total_price}`;
                                    span.style.opacity = '1';
                                    span.style.transform = 'translateY(0)';
                                }, 50);
                            }
                        }
                    }
                });
                
                // Update item total if provided
                if (data.item_total !== undefined) {
                    const itemElement = form.closest('.cart-item');
                    const itemTotal = itemElement.querySelector('.text-lg.font-bold.text-gray-800');
                    if (itemTotal) {
                        itemTotal.style.opacity = '0.5';
                        itemTotal.style.transform = 'translateY(-2px)';
                        setTimeout(() => {
                            itemTotal.textContent = `Rs. ${data.item_total}`;
                            itemTotal.style.opacity = '1';
                            itemTotal.style.transform = 'translateY(0)';
                        }, 50);
                    }
                }
            }
            
            // Update navbar cart count
            if (typeof updateCartCount === 'function' && data.cart_count !== undefined) {
                updateCartCount(data.cart_count);
            }
            
            showNotification(data.message || 'Cart updated!', 'success');
        } else {
            // Revert quantity on error with animation
            quantitySpan.style.opacity = '0.5';
            quantitySpan.style.transform = 'translateY(-2px)';
            setTimeout(() => {
                quantitySpan.textContent = currentQty;
                quantitySpan.style.opacity = '1';
                quantitySpan.style.transform = 'translateY(0)';
            }, 50);
            showNotification(data.message || 'Update failed', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        // Revert quantity on error
        quantitySpan.style.opacity = '0.5';
        quantitySpan.style.transform = 'translateY(-2px)';
        setTimeout(() => {
            quantitySpan.textContent = currentQty;
            quantitySpan.style.opacity = '1';
            quantitySpan.style.transform = 'translateY(0)';
        }, 50);
        showNotification('An error occurred', 'error');
    } finally {
        // Update button states
        if (minusBtn) {
            minusBtn.disabled = newQty <= 1;
        }
        if (plusBtn) {
            plusBtn.disabled = newQty >= 20;
        }
        window.cartIsUpdating = false;
    }
}

// Remove item with smooth animation
async function removeItem(form) {
    const button = form.querySelector('[type="submit"]');
    const originalHTML = button.innerHTML;
    button.innerHTML = '<span class="animate-spin">⟳</span>';
    button.disabled = true;
    
    try {
        const response = await fetch(form.action, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': new FormData(form).get('csrfmiddlewaretoken')
            },
            body: new FormData(form)
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Smooth remove animation
            const item = form.closest('.cart-item');
            item.style.transition = 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)';
            item.style.opacity = '0';
            item.style.transform = 'translateX(-100px)';
            item.style.maxHeight = item.offsetHeight + 'px';
            
            setTimeout(() => {
                item.style.maxHeight = '0';
                item.style.margin = '0';
                item.style.padding = '0';
                item.style.overflow = 'hidden';
                
                setTimeout(() => {
                    item.remove();
                    
                    // Reload if cart is empty
                    if (document.querySelectorAll('.cart-item').length === 0) {
                        window.location.reload();
                    } else if (data.total_price !== undefined) {
                        // Update remaining totals with animation
                        const priceElements = document.querySelectorAll('.flex.justify-between span');
                        priceElements.forEach(span => {
                            if (span.textContent.includes('Rs.')) {
                                const parent = span.closest('.flex.justify-between');
                                if (parent) {
                                    const text = parent.textContent;
                                    if (text.includes('Items') || text.includes('Total')) {
                                        span.style.opacity = '0.5';
                                        span.style.transform = 'translateY(-2px)';
                                        setTimeout(() => {
                                            span.textContent = `Rs. ${data.total_price}`;
                                            span.style.opacity = '1';
                                            span.style.transform = 'translateY(0)';
                                        }, 100);
                                    }
                                }
                            }
                        });
                    }
                    
                    // Update navbar
                    if (typeof updateCartCount === 'function' && data.cart_count !== undefined) {
                        updateCartCount(data.cart_count);
                    }
                }, 400);
            }, 400);
            
            showNotification(data.message || 'Item removed', 'success');
        } else {
            showNotification(data.message || 'Remove failed', 'error');
            button.disabled = false;
            button.innerHTML = originalHTML;
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('An error occurred', 'error');
        button.disabled = false;
        button.innerHTML = originalHTML;
    }
}

// Clear cart
async function clearCart(form) {
    const button = form.querySelector('[type="submit"]');
    const originalText = button.textContent;
    button.textContent = 'Clearing...';
    button.disabled = true;
    
    try {
        const response = await fetch(form.action, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': new FormData(form).get('csrfmiddlewaretoken')
            },
            body: new FormData(form)
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification(data.message || 'Cart cleared', 'success');
            if (typeof updateCartCount === 'function' && data.cart_count !== undefined) {
                updateCartCount(data.cart_count);
            }
            setTimeout(() => window.location.reload(), 800);
        } else {
            showNotification(data.message || 'Clear failed', 'error');
            button.disabled = false;
            button.textContent = originalText;
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('An error occurred', 'error');
        button.disabled = false;
        button.textContent = originalText;
    }
}

// Setup event listeners - simplified approach
function setupCart() {
    console.log('Setting up cart - fresh setup');
    
    // Quantity buttons - direct event listeners
    document.querySelectorAll('.quantity-minus').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            if (window.cartIsUpdating) return;
            const form = this.closest('.update-cart-form');
            if (form) {
                updateQuantity(form, -1);
            }
        });
    });
    
    document.querySelectorAll('.quantity-plus').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            if (window.cartIsUpdating) return;
            const form = this.closest('.update-cart-form');
            if (form) {
                updateQuantity(form, 1);
            }
        });
    });
    
    // Remove buttons
    document.querySelectorAll('.remove-cart-form').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            removeItem(this);
        });
    });
    
    // Clear cart
    document.querySelectorAll('#clear-cart-form').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            clearCart(this);
        });
    });
}

// Initialize
if (!window.cartInitialized) {
    window.cartInitialized = true;
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', setupCart);
    } else {
        setupCart();
    }
} else {
    console.log('Cart already initialized, skipping');
}