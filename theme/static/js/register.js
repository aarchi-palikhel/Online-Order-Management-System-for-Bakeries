document.addEventListener('DOMContentLoaded', function() {
    initPasswordToggle();
    initFormErrorNotifications();
});

function initPasswordToggle() {
    // Handle individual password toggle buttons
    document.querySelectorAll('.password-toggle').forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('data-target');
            const passwordInput = document.getElementById(targetId);
            
            if (!passwordInput) return;
            
            // Toggle password visibility
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                // Change icon to eye-slash
                this.innerHTML = `
                    <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L6.59 6.59m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"></path>
                    </svg>`;
            } else {
                passwordInput.type = 'password';
                // Change icon back to eye
                this.innerHTML = `
                    <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                    </svg>`;
            }
        });
    });
    
    // Handle checkbox toggle if it exists (alternative method)
    const showPasswordsCheckbox = document.getElementById('showPasswords');
    if (showPasswordsCheckbox) {
        showPasswordsCheckbox.addEventListener('change', function() {
            const type = this.checked ? 'text' : 'password';
            const password1Input = document.getElementById('password1');
            const password2Input = document.getElementById('password2');
            
            if (password1Input) {
                password1Input.setAttribute('type', type);
            }
            
            if (password2Input) {
                password2Input.setAttribute('type', type);
            }
        });
    }
}

function initFormErrorNotifications() {
    // Check for form errors and show notifications
    const formErrors = document.querySelectorAll('.text-red-600');
    if (formErrors.length > 0) {
        formErrors.forEach(error => {
            const errorText = error.textContent.trim();
            if (errorText && typeof showError === 'function') {
                showError(errorText);
            }
        });
    }
    
    // Show Django messages as notifications
    const messages = document.querySelectorAll('[data-message-type]');
    messages.forEach(msgElement => {
        const type = msgElement.getAttribute('data-message-type');
        const text = msgElement.getAttribute('data-message-text');
        if (text) {
            const functionName = `show${type.charAt(0).toUpperCase() + type.slice(1)}`;
            if (typeof window[functionName] === 'function') {
                window[functionName](text);
            }
        }
    });
}

// Keyboard shortcut: Alt + P to toggle password visibility
document.addEventListener('keydown', function(event) {
    if (event.altKey && event.key === 'p') {
        event.preventDefault();
        const showPasswordsCheckbox = document.getElementById('showPasswords');
        if (showPasswordsCheckbox) {
            showPasswordsCheckbox.checked = !showPasswordsCheckbox.checked;
            showPasswordsCheckbox.dispatchEvent(new Event('change'));
        }
    }
});

// Export for debugging
window.registerModule = {
    initPasswordToggle,
    initFormErrorNotifications
};