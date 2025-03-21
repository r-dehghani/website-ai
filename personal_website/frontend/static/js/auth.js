/**
 * JavaScript for Authentication Pages
 */

document.addEventListener('DOMContentLoaded', () => {
    // Login form validation
    const loginForm = document.querySelector('form[action="/login"]');
    
    if (loginForm) {
      loginForm.addEventListener('submit', (e) => {
        let isValid = true;
        
        const emailInput = loginForm.querySelector('#email');
        const passwordInput = loginForm.querySelector('#password');
        
        // Validate email
        if (emailInput && !validateEmail(emailInput.value.trim())) {
          isValid = false;
          showError(emailInput, 'Please enter a valid email address');
        } else {
          removeError(emailInput);
        }
        
        // Validate password
        if (passwordInput && !passwordInput.value.trim()) {
          isValid = false;
          showError(passwordInput, 'Please enter your password');
        } else {
          removeError(passwordInput);
        }
        
        if (!isValid) {
          e.preventDefault();
        }
      });
    }
    
    // Registration form validation
    const registerForm = document.querySelector('form[action="/register"]');
    
    if (registerForm) {
      registerForm.addEventListener('submit', (e) => {
        let isValid = true;
        
        const nameInput = registerForm.querySelector('#name');
        const emailInput = registerForm.querySelector('#email');
        const passwordInput = registerForm.querySelector('#password');
        const confirmPasswordInput = registerForm.querySelector('#confirm_password');
        const termsCheckbox = registerForm.querySelector('#terms');
        
        // Validate name
        if (nameInput && !nameInput.value.trim()) {
          isValid = false;
          showError(nameInput, 'Please enter your name');
        } else {
          removeError(nameInput);
        }
        
        // Validate email
        if (emailInput && !validateEmail(emailInput.value.trim())) {
          isValid = false;
          showError(emailInput, 'Please enter a valid email address');
        } else {
          removeError(emailInput);
        }
        
        // Validate password
        if (passwordInput && !validatePassword(passwordInput.value.trim())) {
          isValid = false;
          showError(passwordInput, 'Password must be at least 8 characters and include a number and special character');
        } else {
          removeError(passwordInput);
        }
        
        // Validate confirm password
        if (confirmPasswordInput && passwordInput && confirmPasswordInput.value !== passwordInput.value) {
          isValid = false;
          showError(confirmPasswordInput, 'Passwords do not match');
        } else {
          removeError(confirmPasswordInput);
        }
        
        // Validate terms agreement
        if (termsCheckbox && !termsCheckbox.checked) {
          isValid = false;
          showError(termsCheckbox, 'You must agree to the Terms of Service and Privacy Policy');
        } else {
          removeError(termsCheckbox);
        }
        
        if (!isValid) {
          e.preventDefault();
        }
      });
    }
    
    // Reset password form validation
    const resetPasswordForm = document.querySelector('form[action="/reset-password"]');
    
    if (resetPasswordForm) {
      resetPasswordForm.addEventListener('submit', (e) => {
        let isValid = true;
        
        const emailInput = resetPasswordForm.querySelector('#email');
        
        // Validate email
        if (emailInput && !validateEmail(emailInput.value.trim())) {
          isValid = false;
          showError(emailInput, 'Please enter a valid email address');
        } else {
          removeError(emailInput);
        }
        
        if (!isValid) {
          e.preventDefault();
        }
      });
    }
    
    // New password form validation
    const newPasswordForm = document.querySelector('form[action="/new-password"]');
    
    if (newPasswordForm) {
      newPasswordForm.addEventListener('submit', (e) => {
        let isValid = true;
        
        const passwordInput = newPasswordForm.querySelector('#password');
        const confirmPasswordInput = newPasswordForm.querySelector('#confirm_password');
        
        // Validate password
        if (passwordInput && !validatePassword(passwordInput.value.trim())) {
          isValid = false;
          showError(passwordInput, 'Password must be at least 8 characters and include a number and special character');
        } else {
          removeError(passwordInput);
        }
        
        // Validate confirm password
        if (confirmPasswordInput && passwordInput && confirmPasswordInput.value !== passwordInput.value) {
          isValid = false;
          showError(confirmPasswordInput, 'Passwords do not match');
        } else {
          removeError(confirmPasswordInput);
        }
        
        if (!isValid) {
          e.preventDefault();
        }
      });
    }
    
    // Password visibility toggle
    const passwordToggles = document.querySelectorAll('.password-toggle');
    
    passwordToggles.forEach(toggle => {
      toggle.addEventListener('click', () => {
        const passwordInput = toggle.previousElementSibling;
        
        if (passwordInput.type === 'password') {
          passwordInput.type = 'text';
          toggle.innerHTML = '<i class="icon-eye-off"></i>';
        } else {
          passwordInput.type = 'password';
          toggle.innerHTML = '<i class="icon-eye"></i>';
        }
      });
    });
    
    // Social login buttons
    const socialButtons = document.querySelectorAll('.btn-social');
    
    socialButtons.forEach(button => {
      button.addEventListener('click', (e) => {
        e.preventDefault();
        
        const provider = button.dataset.provider;
        
        // Redirect to social login endpoint
        window.location.href = `/auth/${provider}`;
      });
    });
    
    // Helper functions
    function validateEmail(email) {
      const re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
      return re.test(email);
    }
    
    function validatePassword(password) {
      // At least 8 characters, one number, and one special character
      const re = /^(?=.*[0-9])(?=.*[!@#$%^&*])[a-zA-Z0-9!@#$%^&*]{8,}$/;
      return re.test(password);
    }
    
    function showError(input, message) {
      input.classList.add('is-invalid');
      
      // Find or create error message element
      const formGroup = input.closest('.form-group') || input.parentNode;
      let errorElement = formGroup.querySelector('.error-message');
      
      if (!errorElement) {
        errorElement = document.createElement('div');
        errorElement.classList.add('error-message');
        formGroup.appendChild(errorElement);
      }
      
      errorElement.textContent = message;
    }
    
    function removeError(input) {
      if (!input) return;
      
      input.classList.remove('is-invalid');
      
      const formGroup = input.closest('.form-group') || input.parentNode;
      const errorElement = formGroup.querySelector('.error-message');
      
      if (errorElement) {
        errorElement.remove();
      }
    }
  });