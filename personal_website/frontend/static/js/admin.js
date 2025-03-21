/**
 * JavaScript for Admin Panel
 */

document.addEventListener('DOMContentLoaded', () => {
    // Responsive sidebar toggle
    const sidebarToggle = document.createElement('button');
    sidebarToggle.classList.add('sidebar-toggle');
    sidebarToggle.innerHTML = '<i class="icon-menu"></i>';
    document.querySelector('.admin-header')?.prepend(sidebarToggle);
    
    sidebarToggle.addEventListener('click', () => {
      document.querySelector('.admin-container')?.classList.toggle('sidebar-collapsed');
    });
    
    // Custom file upload
    const fileInputs = document.querySelectorAll('.custom-file-input');
    
    fileInputs.forEach(input => {
      const label = input.nextElementSibling;
      
      input.addEventListener('change', (e) => {
        let fileName = '';
        
        if (input.files && input.files.length > 1) {
          fileName = `${input.files.length} files selected`;
        } else {
          fileName = e.target.value.split('\\').pop();
        }
        
        if (fileName) {
          label.innerHTML = `<i class="icon-file"></i> ${fileName}`;
        } else {
          label.innerHTML = '<i class="icon-upload"></i> Choose File';
        }
      });
    });
    
    // Data table search and filter
    const dataTableSearch = document.querySelector('.data-table-search');
    const dataTable = document.querySelector('.data-table');
    
    if (dataTableSearch && dataTable) {
      dataTableSearch.addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase();
        const rows = dataTable.querySelectorAll('tbody tr');
        
        rows.forEach(row => {
          const text = row.textContent.toLowerCase();
          if (text.includes(searchTerm)) {
            row.style.display = '';
          } else {
            row.style.display = 'none';
          }
        });
      });
    }
    
    // Select all functionality
    const selectAllCheckbox = document.querySelector('.select-all');
    
    if (selectAllCheckbox) {
      selectAllCheckbox.addEventListener('change', () => {
        const checkboxes = document.querySelectorAll('.row-checkbox');
        checkboxes.forEach(checkbox => {
          checkbox.checked = selectAllCheckbox.checked;
        });
        
        updateBulkActionsVisibility();
      });
      
      // Individual checkbox changes
      const rowCheckboxes = document.querySelectorAll('.row-checkbox');
      rowCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', () => {
          updateSelectAllState();
          updateBulkActionsVisibility();
        });
      });
      
      function updateSelectAllState() {
        const checkboxes = document.querySelectorAll('.row-checkbox');
        const checkedBoxes = document.querySelectorAll('.row-checkbox:checked');
        
        if (checkboxes.length === checkedBoxes.length) {
          selectAllCheckbox.checked = true;
          selectAllCheckbox.indeterminate = false;
        } else if (checkedBoxes.length === 0) {
          selectAllCheckbox.checked = false;
          selectAllCheckbox.indeterminate = false;
        } else {
          selectAllCheckbox.checked = false;
          selectAllCheckbox.indeterminate = true;
        }
      }
      
      function updateBulkActionsVisibility() {
        const bulkActions = document.querySelector('.bulk-actions');
        const checkedBoxes = document.querySelectorAll('.row-checkbox:checked');
        
        if (bulkActions) {
          if (checkedBoxes.length > 0) {
            bulkActions.classList.add('show');
            bulkActions.querySelector('.selected-count').textContent = checkedBoxes.length;
          } else {
            bulkActions.classList.remove('show');
          }
        }
      }
    }
    
    // Delete confirmation
    const deleteButtons = document.querySelectorAll('.delete-btn');
    
    deleteButtons.forEach(button => {
      button.addEventListener('click', (e) => {
        e.preventDefault();
        
        const itemId = button.dataset.id;
        const itemType = button.dataset.type || 'item';
        
        if (confirm(`Are you sure you want to delete this ${itemType}?`)) {
          // In production, use AJAX to delete the item
          /*
          fetch(`/api/${itemType}s/${itemId}`, {
            method: 'DELETE',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content
            }
          })
          .then(response => response.json())
          .then(data => {
            if (data.success) {
              // Remove the item from the DOM
              const row = button.closest('tr') || button.closest('.item-row');
              if (row) {
                row.remove();
              }
              
              // Show success message
              showNotification('success', `${itemType.charAt(0).toUpperCase() + itemType.slice(1)} deleted successfully.`);
            } else {
              showNotification('error', data.message || `Failed to delete ${itemType}.`);
            }
          })
          .catch(error => {
            showNotification('error', `Failed to delete ${itemType}.`);
          });
          */
          
          // Simulate successful deletion for demo
          const row = button.closest('tr') || button.closest('.item-row');
          if (row) {
            row.style.opacity = '0';
            setTimeout(() => {
              row.remove();
            }, 300);
          }
          
          showNotification('success', `${itemType.charAt(0).toUpperCase() + itemType.slice(1)} deleted successfully.`);
        }
      });
    });
    
    // Approve comments
    const approveButtons = document.querySelectorAll('.approve-btn');
    
    approveButtons.forEach(button => {
      button.addEventListener('click', () => {
        const commentId = button.dataset.id;
        const isApproved = button.classList.contains('active');
        
        // In production, use AJAX to update the comment status
        /*
        fetch(`/api/comments/${commentId}/approve`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content
          },
          body: JSON.stringify({ approved: !isApproved })
        })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            // Update the button state
            button.classList.toggle('active');
            button.innerHTML = `<i class="icon-check"></i> ${isApproved ? 'Approve' : 'Approved'}`;
            
            // Show success message
            showNotification('success', `Comment ${isApproved ? 'unapproved' : 'approved'} successfully.`);
          } else {
            showNotification('error', data.message || 'Failed to update comment status.');
          }
        })
        .catch(error => {
          showNotification('error', 'Failed to update comment status.');
        });
        */
        
        // Simulate successful update for demo
        button.classList.toggle('active');
        button.innerHTML = `<i class="icon-check"></i> ${isApproved ? 'Approve' : 'Approved'}`;
        
        showNotification('success', `Comment ${isApproved ? 'unapproved' : 'approved'} successfully.`);
      });
    });
    
    // User role change
    const roleSelects = document.querySelectorAll('.role-select');
    
    roleSelects.forEach(select => {
      select.addEventListener('change', () => {
        const userId = select.dataset.id;
        const newRole = select.value;
        
        // In production, use AJAX to update the user role
        /*
        fetch(`/api/users/${userId}/role`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content
          },
          body: JSON.stringify({ role: newRole })
        })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            // Show success message
            showNotification('success', `User role updated to ${newRole}.`);
          } else {
            // Revert the select value
            select.value = select.dataset.originalValue;
            showNotification('error', data.message || 'Failed to update user role.');
          }
        })
        .catch(error => {
          // Revert the select value
          select.value = select.dataset.originalValue;
          showNotification('error', 'Failed to update user role.');
        });
        */
        
        // Simulate successful update for demo
        select.dataset.originalValue = newRole;
        showNotification('success', `User role updated to ${newRole}.`);
      });
    });
    
    // User status toggle
    const statusToggles = document.querySelectorAll('.status-toggle');
    
    statusToggles.forEach(toggle => {
      toggle.addEventListener('change', () => {
        const userId = toggle.dataset.id;
        const isActive = toggle.checked;
        
        // In production, use AJAX to update the user status
        /*
        fetch(`/api/users/${userId}/status`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content
          },
          body: JSON.stringify({ active: isActive })
        })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            // Show success message
            showNotification('success', `User ${isActive ? 'activated' : 'deactivated'} successfully.`);
          } else {
            // Revert the toggle state
            toggle.checked = !isActive;
            showNotification('error', data.message || 'Failed to update user status.');
          }
        })
        .catch(error => {
          // Revert the toggle state
          toggle.checked = !isActive;
          showNotification('error', 'Failed to update user status.');
        });
        */
        
        // Simulate successful update for demo
        showNotification('success', `User ${isActive ? 'activated' : 'deactivated'} successfully.`);
      });
    });
    
    // Show notifications
    function showNotification(type, message) {
      const notification = document.createElement('div');
      notification.classList.add('admin-notification', `notification-${type}`);
      
      const icon = document.createElement('i');
      icon.classList.add(`icon-${type === 'success' ? 'check' : 'alert'}`);
      
      const messageElement = document.createElement('span');
      messageElement.textContent = message;
      
      const closeBtn = document.createElement('button');
      closeBtn.classList.add('notification-close');
      closeBtn.innerHTML = '&times;';
      closeBtn.addEventListener('click', () => {
        notification.classList.add('hide');
        setTimeout(() => {
          notification.remove();
        }, 300);
      });
      
      notification.appendChild(icon);
      notification.appendChild(messageElement);
      notification.appendChild(closeBtn);
      
      const notificationsContainer = document.querySelector('.admin-notifications');
      if (!notificationsContainer) {
        const container = document.createElement('div');
        container.classList.add('admin-notifications');
        document.body.appendChild(container);
      }
      
      document.querySelector('.admin-notifications').appendChild(notification);
      
      // Auto-hide notification after 5 seconds
      setTimeout(() => {
        notification.classList.add('hide');
        setTimeout(() => {
          notification.remove();
        }, 300);
      }, 5000);
    }
    
    // Settings form save
    const settingsForm = document.querySelector('.settings-form');
    
    if (settingsForm) {
      settingsForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const submitBtn = settingsForm.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Saving...';
        submitBtn.disabled = true;
        
        // In production, use AJAX to save the settings
        /*
        const formData = new FormData(settingsForm);
        
        fetch('/api/settings', {
          method: 'POST',
          body: formData,
          headers: {
            'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content
          }
        })
        .then(response => response.json())
        .then(data => {
          submitBtn.textContent = originalText;
          submitBtn.disabled = false;
          
          if (data.success) {
            showNotification('success', 'Settings saved successfully.');
          } else {
            showNotification('error', data.message || 'Failed to save settings.');
          }
        })
        .catch(error => {
          submitBtn.textContent = originalText;
          submitBtn.disabled = false;
          showNotification('error', 'Failed to save settings.');
        });
        */
        
        // Simulate successful save for demo
        setTimeout(() => {
          submitBtn.textContent = originalText;
          submitBtn.disabled = false;
          showNotification('success', 'Settings saved successfully.');
        }, 1500);
      });
    }
    
    // Initialize date pickers
    const datePickers = document.querySelectorAll('.date-picker');
    
    datePickers.forEach(input => {
      // In production, use a date picker library
      // Here we're just adding a placeholder
      input.type = 'date';
    });
    
    // Initialize rich text editors
    const richTextEditors = document.querySelectorAll('.rich-text-editor');
    
    richTextEditors.forEach(textarea => {
      // In production, use a rich text editor library like TinyMCE or Quill
      // Here we're just adding a simple toolbar placeholder
      const editorContainer = document.createElement('div');
      editorContainer.classList.add('editor-container');
      
      const toolbar = document.createElement('div');
      toolbar.classList.add('editor-toolbar');
      toolbar.innerHTML = `
        <button type="button" class="toolbar-btn"><i class="icon-bold"></i></button>
        <button type="button" class="toolbar-btn"><i class="icon-italic"></i></button>
        <button type="button" class="toolbar-btn"><i class="icon-underline"></i></button>
        <button type="button" class="toolbar-btn"><i class="icon-list"></i></button>
        <button type="button" class="toolbar-btn"><i class="icon-link"></i></button>
        <button type="button" class="toolbar-btn"><i class="icon-image"></i></button>
      `;
      
      textarea.parentNode.insertBefore(editorContainer, textarea);
      editorContainer.appendChild(toolbar);
      editorContainer.appendChild(textarea);
    });
  });