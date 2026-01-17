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
            const productCard = this.closest('[data-product-id]');
            const productName = productCard ? productCard.querySelector('h3')?.textContent.trim() : 'Product';
            
            // Save original button state
            const originalText = submitBtn.textContent;
            const originalClass = submitBtn.className;
            
            // Show loading state
            submitBtn.textContent = 'Adding...';
            submitBtn.disabled = true;
            submitBtn.classList.add('opacity-75', 'cursor-not-allowed');
            
            // Submit form via AJAX
            fetch(this.action, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': this.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
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
                    showSuccess(`${productName} added to cart!`);
                    
                    // Update cart count
                    if (typeof updateCartCount === 'function') {
                        updateCartCount(data.cart_count);
                    }
                } else {
                    showError(data.message || 'Could not add item to cart');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showError('An error occurred. Please try again.');
            })
            .finally(() => {
                // Restore button state
                submitBtn.textContent = originalText;
                submitBtn.className = originalClass;
                submitBtn.disabled = false;
            });
        });
    });
}

// Export for debugging
window.homeModule = {
    initHomePageAJAX
};