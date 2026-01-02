document.addEventListener('DOMContentLoaded', function() {
    const showPasswordsCheckbox = document.getElementById('showPasswords');
    const password1Input = document.getElementById('password1');
    const password2Input = document.getElementById('password2');
    
    showPasswordsCheckbox.addEventListener('change', function() {
        // Toggle password visibility for both fields
        const type = this.checked ? 'text' : 'password';
        
        if (password1Input) {
            password1Input.setAttribute('type', type);
        }
        
        if (password2Input) {
            password2Input.setAttribute('type', type);
        }
    });
    
    // Optional: Add a keyboard shortcut for toggling password visibility
    document.addEventListener('keydown', function(event) {
        // Alt + P to toggle password visibility
        if (event.altKey && event.key === 'p') {
            event.preventDefault();
            showPasswordsCheckbox.checked = !showPasswordsCheckbox.checked;
            showPasswordsCheckbox.dispatchEvent(new Event('change'));
        }
    });
});