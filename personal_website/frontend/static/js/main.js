/**
 * Main JavaScript for Personal Website
 */

document.addEventListener('DOMContentLoaded', () => {
    // Mobile menu toggle
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const mainNav = document.querySelector('.main-nav');
    
    if (mobileMenuToggle && mainNav) {
      mobileMenuToggle.addEventListener('click', () => {
        mobileMenuToggle.classList.toggle('active');
        mainNav.classList.toggle('active');
      });
    }
    
    // Close mobile menu when clicking outside
    document.addEventListener('click', (event) => {
      if (mainNav && mainNav.classList.contains('active') && 
          !mainNav.contains(event.target) && 
          !mobileMenuToggle.contains(event.target)) {
        mainNav.classList.remove('active');
        mobileMenuToggle.classList.remove('active');
      }
    });
    
    // Scroll to top button
    const scrollTopBtn = document.createElement('button');
    scrollTopBtn.classList.add('scroll-top-btn');
    scrollTopBtn.innerHTML = '<i class="icon-arrow-up"></i>';
    document.body.appendChild(scrollTopBtn);
    
    window.addEventListener('scroll', () => {
      if (window.pageYOffset > 300) {
        scrollTopBtn.classList.add('show');
      } else {
        scrollTopBtn.classList.remove('show');
      }
    });
    
    scrollTopBtn.addEventListener('click', () => {
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
    });
    
    // Form validation
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
      const requiredInputs = form.querySelectorAll('[required]');
      const submitBtn = form.querySelector('button[type="submit"]');
      
      if (requiredInputs.length && submitBtn) {
        form.addEventListener('submit', (event) => {
          let isValid = true;
          
          requiredInputs.forEach(input => {
            if (!input.value.trim()) {
              isValid = false;
              markInvalid(input);
            } else {
              markValid(input);
            }
            
            // Email validation
            if (input.type === 'email' && input.value.trim()) {
              if (!validateEmail(input.value.trim())) {
                isValid = false;
                markInvalid(input, 'Please enter a valid email address');
              }
            }
            
            // Password validation
            if (input.type === 'password' && input.id === 'password' && input.value.trim()) {
              if (!validatePassword(input.value.trim())) {
                isValid = false;
                markInvalid(input, 'Password must be at least 8 characters and include a number and special character');
              }
            }
            
            // Password confirmation validation
            if (input.id === 'confirm_password' && input.value.trim()) {
              const passwordInput = document.getElementById('password');
              if (passwordInput && input.value !== passwordInput.value) {
                isValid = false;
                markInvalid(input, 'Passwords do not match');
              }
            }
          });
          
          if (!isValid) {
            event.preventDefault();
          }
        });
      }
    });
    
    function markInvalid(input, message) {
      input.classList.add('is-invalid');
      const parent = input.closest('.form-group');
      if (parent) {
        let errorElement = parent.querySelector('.error-message');
        if (!errorElement) {
          errorElement = document.createElement('div');
          errorElement.classList.add('error-message');
          parent.appendChild(errorElement);
        }
        errorElement.textContent = message || 'This field is required';
      }
    }
    
    function markValid(input) {
      input.classList.remove('is-invalid');
      const parent = input.closest('.form-group');
      if (parent) {
        const errorElement = parent.querySelector('.error-message');
        if (errorElement) {
          errorElement.remove();
        }
      }
    }
    
    function validateEmail(email) {
      const re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
      return re.test(email);
    }
    
    function validatePassword(password) {
      // At least 8 characters, contain at least 1 number and 1 special character
      const re = /^(?=.*[0-9])(?=.*[!@#$%^&*])[a-zA-Z0-9!@#$%^&*]{8,}$/;
      return re.test(password);
    }
    
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    
    alerts.forEach(alert => {
      setTimeout(() => {
        alert.style.opacity = '0';
        setTimeout(() => {
          alert.style.display = 'none';
        }, 500);
      }, 5000);
    });
    
    // Newsletter form submission with AJAX
    const newsletterForm = document.querySelector('.newsletter-form');
    
    if (newsletterForm) {
      newsletterForm.addEventListener('submit', (event) => {
        event.preventDefault();
        
        const emailInput = newsletterForm.querySelector('input[type="email"]');
        const submitBtn = newsletterForm.querySelector('button[type="submit"]');
        
        if (emailInput && submitBtn) {
          const email = emailInput.value.trim();
          
          if (!email || !validateEmail(email)) {
            markInvalid(emailInput, 'Please enter a valid email address');
            return;
          }
          
          markValid(emailInput);
          
          // Disable button and show loading state
          submitBtn.disabled = true;
          const originalBtnText = submitBtn.textContent;
          submitBtn.innerHTML = 'Subscribing...';
          
          // Simulate AJAX request (replace with actual AJAX call in production)
          setTimeout(() => {
            // Success state
            newsletterForm.innerHTML = '<div class="success-message"><i class="icon-check"></i><p>Thank you for subscribing to our newsletter!</p></div>';
            
            // In production, use AJAX to submit the form
            /*
            fetch('/subscribe', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({ email }),
            })
            .then(response => response.json())
            .then(data => {
              if (data.success) {
                newsletterForm.innerHTML = '<div class="success-message"><i class="icon-check"></i><p>Thank you for subscribing to our newsletter!</p></div>';
              } else {
                submitBtn.disabled = false;
                submitBtn.textContent = originalBtnText;
                markInvalid(emailInput, data.message || 'Something went wrong. Please try again.');
              }
            })
            .catch(error => {
              submitBtn.disabled = false;
              submitBtn.textContent = originalBtnText;
              markInvalid(emailInput, 'Something went wrong. Please try again.');
            });
            */
          }, 1500);
        }
      });
    }
    
    // Lazy loading images
    if ('loading' in HTMLImageElement.prototype) {
      const lazyImages = document.querySelectorAll('img[loading="lazy"]');
      lazyImages.forEach(img => {
        img.src = img.dataset.src;
      });
    } else {
      // Fallback for browsers that don't support lazy loading
      const lazyImageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            const lazyImage = entry.target;
            lazyImage.src = lazyImage.dataset.src;
            lazyImageObserver.unobserve(lazyImage);
          }
        });
      });
      
      const lazyImages = document.querySelectorAll('img[data-src]');
      lazyImages.forEach(img => {
        lazyImageObserver.observe(img);
      });
    }
  });