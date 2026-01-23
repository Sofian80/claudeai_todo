/* ================================
   Main JavaScript File
   ================================ */

/**
 * Password Toggle Functionality
 * Toggles password visibility and updates the eye icon
 */
function setupPasswordToggle(toggleButtonId, passwordInputId, iconId) {
    const toggleButton = document.getElementById(toggleButtonId);
    const passwordInput = document.getElementById(passwordInputId);
    const icon = document.getElementById(iconId);

    if (toggleButton && passwordInput && icon) {
        toggleButton.addEventListener('click', function() {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);

            if (type === 'password') {
                icon.classList.remove('bi-eye-slash');
                icon.classList.add('bi-eye');
            } else {
                icon.classList.remove('bi-eye');
                icon.classList.add('bi-eye-slash');
            }
        });
    }
}

/**
 * Auto-initialize password toggles on page load
 * Searches for common password toggle patterns
 */
document.addEventListener('DOMContentLoaded', function() {
    // Login page
    setupPasswordToggle('togglePassword', 'id_password', 'passwordIcon');

    // Register page
    setupPasswordToggle('togglePassword1', 'id_password1', 'passwordIcon1');
    setupPasswordToggle('togglePassword2', 'id_password2', 'passwordIcon2');

    // Profile page - Change password
    setupPasswordToggle('toggleOldPassword', 'id_old_password', 'oldPasswordIcon');
    setupPasswordToggle('toggleNewPassword1', 'id_new_password1', 'newPasswordIcon1');
    setupPasswordToggle('toggleNewPassword2', 'id_new_password2', 'newPasswordIcon2');
});
