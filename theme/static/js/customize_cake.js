document.addEventListener('DOMContentLoaded', function() {
    // Get elements
    const form = document.getElementById('customize-form');
    const weightSelect = document.querySelector('select[name="weight"]');
    const tiersSelect = document.querySelector('select[name="tiers"]');
    const customWeightContainer = document.getElementById('custom-weight-container');
    const quantityInput = document.querySelector('input[name="quantity"]');
    const messageInput = document.querySelector('input[name="message_on_cake"]');
    const imageInput = document.getElementById('reference-image-input');
    const imagePreview = document.getElementById('image-preview');
    const previewImage = document.getElementById('preview-image');
    const deliveryDateInput = document.querySelector('input[name="delivery_date"]');
    
    // Get base price from data attribute
    const basePriceElement = document.getElementById('base-price');
    const basePrice = parseFloat(basePriceElement ? basePriceElement.textContent : '0');
    
    // Multiplier configurations
    const weightMultipliers = {
        '0.5': 0.7,
        '1': 1.0,
        '2': 1.8,
        '3': 2.5,
        '4': 3.2,
        '5': 4.0,
        'custom': 1.0
    };
    
    const tierMultipliers = {
        '1': 1.0,
        '2': 1.5,
        '3': 2.0
    };
    
    const weightLabels = {
        '0.5': '0.5 lb',
        '1': '1 lb',
        '2': '2 lb',
        '3': '3 lb',
        '4': '4 lb',
        '5': '5 lb',
        'custom': 'Custom'
    };
    
    const tierLabels = {
        '1': 'Single Tier',
        '2': 'Two Tiers',
        '3': 'Three Tiers'
    };

    // Update preview and price calculation
    function updatePreview() {
        const selectedWeight = weightSelect.value;
        const selectedTiers = tiersSelect.value;
        const message = messageInput.value;
        const quantity = parseInt(quantityInput.value) || 1;
        
        // Get display values
        const weightLabel = weightLabels[selectedWeight] || selectedWeight;
        const tiersLabel = tierLabels[selectedTiers] || selectedTiers;
        
        // Update preview details
        const previewWeight = document.getElementById('preview-weight');
        const previewTiers = document.getElementById('preview-tiers');
        const previewQuantity = document.getElementById('preview-quantity');
        
        if (previewWeight) previewWeight.textContent = weightLabel;
        if (previewTiers) previewTiers.textContent = tiersLabel;
        if (previewQuantity) previewQuantity.textContent = `Quantity : ${quantity}`;
        
        // Update message preview
        const messagePreview = document.getElementById('preview-message');
        const messageText = document.getElementById('preview-message-text');
        if (message.trim() && messagePreview && messageText) {
            messageText.textContent = message;
            messagePreview.classList.remove('hidden');
        } else if (messagePreview) {
            messagePreview.classList.add('hidden');
        }
        
        // Calculate price
        let weightMultiplier = weightMultipliers[selectedWeight] || 1.0;
        let tierMultiplier = tierMultipliers[selectedTiers] || 1.0;
        
        // For custom weight, use entered value
        if (selectedWeight === 'custom') {
            const customWeightInput = document.querySelector('input[name="custom_weight"]');
            if (customWeightInput && customWeightInput.value) {
                const customWeight = parseFloat(customWeightInput.value);
                if (!isNaN(customWeight)) {
                    weightMultiplier = customWeight;
                }
            }
        }
        
        const price = basePrice * weightMultiplier * tierMultiplier * quantity;
        
        // Update price display
        const basePriceDisplay = document.getElementById('base-price');
        const weightMultiplierDisplay = document.getElementById('weight-multiplier');
        const tierMultiplierDisplay = document.getElementById('tier-multiplier');
        const estimatedPrice = document.getElementById('estimated-price');
        const finalPrice = document.getElementById('final-price');
        const finalQuantity = document.getElementById('final-quantity');
        const finalWeight = document.getElementById('final-weight');
        const finalTiers = document.getElementById('final-tiers');
        
        if (basePriceDisplay) basePriceDisplay.textContent = basePrice.toFixed(2);
        if (weightMultiplierDisplay) weightMultiplierDisplay.textContent = weightMultiplier.toFixed(1) + 'x';
        if (tierMultiplierDisplay) tierMultiplierDisplay.textContent = tierMultiplier.toFixed(1) + 'x';
        if (estimatedPrice) estimatedPrice.textContent = 'Rs. ' + price.toFixed(2);
        if (finalPrice) finalPrice.textContent = 'Rs. ' + price.toFixed(2);
        if (finalQuantity) finalQuantity.textContent = quantity;
        if (finalWeight) finalWeight.textContent = weightLabel;
        if (finalTiers) finalTiers.textContent = tiersLabel.toLowerCase();
    }

    // Show/hide custom weight input
    function toggleCustomWeight() {
        if (weightSelect.value === 'custom') {
            customWeightContainer.classList.remove('hidden');
            const customWeightInput = document.querySelector('input[name="custom_weight"]');
            if (customWeightInput) {
                customWeightInput.focus();
            }
        } else {
            customWeightContainer.classList.add('hidden');
        }
        updatePreview();
    }

    // Handle image preview
    function handleImagePreview(event) {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                if (previewImage) previewImage.src = e.target.result;
                if (imagePreview) imagePreview.classList.remove('hidden');
            };
            reader.readAsDataURL(file);
        } else {
            if (imagePreview) imagePreview.classList.add('hidden');
        }
    }

    // Set up delivery date
    function setupDeliveryDate() {
        if (deliveryDateInput) {
            const today = new Date();
            const minDate = new Date(today);
            minDate.setDate(today.getDate() + 2);
            
            const formattedMinDate = minDate.toISOString().split('T')[0];
            deliveryDateInput.min = formattedMinDate;
            
            // Set default to 3 days from today
            const defaultDate = new Date(today);
            defaultDate.setDate(today.getDate() + 3);
            const formattedDefaultDate = defaultDate.toISOString().split('T')[0];
            
            // Only set default if no value is already set
            if (!deliveryDateInput.value) {
                deliveryDateInput.value = formattedDefaultDate;
            }
        }
    }

    // Form validation
    function validateForm(event) {
        // Validate custom weight if selected
        if (weightSelect.value === 'custom') {
            const customWeightInput = document.querySelector('input[name="custom_weight"]');
            if (!customWeightInput || !customWeightInput.value.trim()) {
                event.preventDefault();
                alert('Please enter custom weight');
                if (customWeightInput) customWeightInput.focus();
                return false;
            }
        }
        return true;
    }

    // Initialize event listeners
    function initializeEventListeners() {
        // Weight selection
        if (weightSelect) {
            weightSelect.addEventListener('change', toggleCustomWeight);
        }
        
        // Other form elements
        if (tiersSelect) {
            tiersSelect.addEventListener('change', updatePreview);
        }
        
        if (quantityInput) {
            quantityInput.addEventListener('input', updatePreview);
        }
        
        if (messageInput) {
            messageInput.addEventListener('input', updatePreview);
        }
        
        // Custom weight input
        const customWeightInput = document.querySelector('input[name="custom_weight"]');
        if (customWeightInput) {
            customWeightInput.addEventListener('input', updatePreview);
        }
        
        // Image upload
        if (imageInput) {
            imageInput.addEventListener('change', handleImagePreview);
        }
        
        // Form submission
        if (form) {
            form.addEventListener('submit', validateForm);
        }
    }

    // Initialize everything
    function initialize() {
        setupDeliveryDate();
        toggleCustomWeight();
        updatePreview();
        initializeEventListeners();
    }

    // Start the initialization
    initialize();
});