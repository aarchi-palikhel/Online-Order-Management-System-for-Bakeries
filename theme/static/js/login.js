document.addEventListener('DOMContentLoaded', function() {
    const togglePassword = document.getElementById('togglePassword');
    const passwordInput = document.getElementById('password');
    const eyeIcon = document.getElementById('eyeIcon');
    const eyeSlashIcon = document.getElementById('eyeSlashIcon');
    const toggleText = document.getElementById('toggleText');
    
    togglePassword.addEventListener('click', function() {
        // Toggle the type attribute
        const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordInput.setAttribute('type', type);
        
        // Toggle the icon and text
        if (type === 'text') {
            eyeIcon.classList.add('hidden');
            eyeSlashIcon.classList.remove('hidden');
            toggleText.textContent = 'Hide';
        } else {
            eyeIcon.classList.remove('hidden');
            eyeSlashIcon.classList.add('hidden');
            toggleText.textContent = 'Show';
        }
    });
});