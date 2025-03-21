/**
 * JavaScript for Contributor Panel
 */

document.addEventListener('DOMContentLoaded', () => {
    // Mobile sidebar toggle
    const sidebarToggle = document.createElement('button');
    sidebarToggle.classList.add('sidebar-toggle');
    sidebarToggle.innerHTML = '<i class="icon-menu"></i>';
    document.querySelector('.dashboard-header')?.prepend(sidebarToggle);
    
    sidebarToggle.addEventListener('click', () => {
      document.querySelector('.dashboard-container')?.classList.toggle('sidebar-collapsed');
    });
    
    // Article form submission
    const articleForm = document.querySelector('.article-form');
    
    if (articleForm) {
      articleForm.addEventListener('submit', (e) => {
        const titleInput = articleForm.querySelector('#title');
        const contentInput = articleForm.querySelector('#content');
        
        if (titleInput && !titleInput.value.trim()) {
          e.preventDefault();
          showFormError(titleInput, 'Please enter a title');
          titleInput.focus();
          return;
        }
        
        if (contentInput && !contentInput.value.trim()) {
          e.preventDefault();
          showFormError(contentInput, 'Please enter content');
          contentInput.focus();
          return;
        }
      });
      
      // Draft autosave
      let autosaveTimeout;
      const autosaveIndicator = document.createElement('div');
      autosaveIndicator.classList.add('autosave-indicator');
      articleForm.appendChild(autosaveIndicator);
      
      // Autosave when title or content changes
      const titleInput = articleForm.querySelector('#title');
      const contentInput = articleForm.querySelector('#content');
      
      if (titleInput && contentInput) {
        [titleInput, contentInput].forEach(input => {
          input.addEventListener('input', () => {
            clearTimeout(autosaveTimeout);
            
            autosaveIndicator.textContent = 'Saving draft...';
            autosaveIndicator.classList.add('show');
            
            autosaveTimeout = setTimeout(() => {
              autosaveDraft();
            }, 2000); // Wait for 2 seconds of inactivity before saving
          });
        });
      }
      
      function autosaveDraft() {
        // Get form data
        const formData = new FormData(articleForm);
        formData.append('is_draft', true);
        
        // In production, use AJAX to save the draft
        /*
        fetch('/api/articles/draft', {
          method: 'POST',
          body: formData,
          headers: {
            'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content
          }
        })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            autosaveIndicator.textContent = 'Draft saved';
            setTimeout(() => {
              autosaveIndicator.classList.remove('show');
            }, 2000);
            
            // Update the article ID if it's a new article
            if (data.article_id && !articleForm.querySelector('#article_id').value) {
              articleForm.querySelector('#article_id').value = data.article_id;
              
              // Update the form action URL
              articleForm.action = articleForm.action.replace('/create', `/edit/${data.article_id}`);
              
              // Update the browser URL without reloading the page
              history.replaceState(null, document.title, `/contributor/edit-article/${data.article_id}`);
            }
          } else {
            autosaveIndicator.textContent = 'Failed to save draft';
            autosaveIndicator.classList.add('error');
            setTimeout(() => {
              autosaveIndicator.classList.remove('show', 'error');
            }, 3000);
          }
        })
        .catch(error => {
          autosaveIndicator.textContent = 'Failed to save draft';
          autosaveIndicator.classList.add('error');
          setTimeout(() => {
            autosaveIndicator.classList.remove('show', 'error');
          }, 3000);
        });
        */
        
        // Simulate successful autosave for demo
        setTimeout(() => {
          autosaveIndicator.textContent = 'Draft saved';
          setTimeout(() => {
            autosaveIndicator.classList.remove('show');
          }, 2000);
        }, 1000);
      }
    }
    
    // Show form error
    function showFormError(input, message) {
      input.classList.add('is-invalid');
      
      const formGroup = input.closest('.form-group');
      if (formGroup) {
        let errorElement = formGroup.querySelector('.error-message');
        
        if (!errorElement) {
          errorElement = document.createElement('div');
          errorElement.classList.add('error-message');
          formGroup.appendChild(errorElement);
        }
        
        errorElement.textContent = message;
      }
    }
    
    // Featured image upload preview
    const featuredImageInput = document.querySelector('#featured_image');
    const featuredImagePreview = document.querySelector('.featured-image-preview');
    
    if (featuredImageInput && featuredImagePreview) {
      featuredImageInput.addEventListener('change', (e) => {
        if (featuredImageInput.files && featuredImageInput.files[0]) {
          const reader = new FileReader();
          
          reader.onload = (e) => {
            featuredImagePreview.innerHTML = `<img src="${e.target.result}" alt="Featured Image Preview">`;
          };
          
          reader.readAsDataURL(featuredImageInput.files[0]);
        } else {
          featuredImagePreview.innerHTML = 'No image selected';
        }
      });
    }
    
    // Tags input
    const tagInput = document.querySelector('.tag-input input');
    const tagContainer = document.querySelector('.tag-input');
    const hiddenTagsInput = document.querySelector('#tags');
    
    if (tagInput && tagContainer && hiddenTagsInput) {
      const tags = [];
      
      // Initialize existing tags if any
      if (hiddenTagsInput.value) {
        hiddenTagsInput.value.split(',').forEach(tag => {
          tag = tag.trim();
          if (tag) {
            addTag(tag);
          }
        });
      }
      
      tagInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ',') {
          e.preventDefault();
          
          const tagText = tagInput.value.trim();
          
          if (tagText) {
            addTag(tagText);
            tagInput.value = '';
          }
        }
      });
      
      function addTag(text) {
        // Don't add duplicates
        if (tags.includes(text)) {
          return;
        }
        
        tags.push(text);
        updateHiddenInput();
        
        const tagElement = document.createElement('span');
        tagElement.classList.add('tag');
        tagElement.textContent = text;
        
        const removeBtn = document.createElement('span');
        removeBtn.classList.add('tag-remove');
        removeBtn.innerHTML = '&times;';
        removeBtn.addEventListener('click', () => {
          tagElement.remove();
          tags.splice(tags.indexOf(text), 1);
          updateHiddenInput();
        });
        
        tagElement.appendChild(removeBtn);
        tagContainer.insertBefore(tagElement, tagInput);
      }
      
      function updateHiddenInput() {
        hiddenTagsInput.value = tags.join(',');
      }
    }
    
    // Rich text editor
    const contentEditor = document.querySelector('#content');
    
    if (contentEditor) {
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
      
      contentEditor.parentNode.insertBefore(editorContainer, contentEditor);
      editorContainer.appendChild(toolbar);
      editorContainer.appendChild(contentEditor);
      
      // Make textarea higher
      contentEditor.style.minHeight = '300px';
    }
    
    // Publish confirmation
    const publishButton = document.querySelector('.publish-btn');
    
    if (publishButton) {
      publishButton.addEventListener('click', (e) => {
        if (!confirm('Are you sure you want to publish this article?')) {
          e.preventDefault();
        }
      });
    }
    
    // Delete article confirmation
    const deleteArticleButtons = document.querySelectorAll('.delete-btn');
    
    deleteArticleButtons.forEach(button => {
      button.addEventListener('click', (e) => {
        if (!confirm('Are you sure you want to delete this article? This action cannot be undone.')) {
          e.preventDefault();
        }
      });
    });
    
    // Reply to comment functionality
    const replyButtons = document.querySelectorAll('.reply-btn');
    
    replyButtons.forEach(button => {
      button.addEventListener('click', () => {
        const commentId = button.dataset.id;
        const commentElement = button.closest('.comment');
        
        // If reply form already exists, remove it
        const existingForm = document.querySelector('.reply-form');
        if (existingForm) {
          existingForm.remove();
        }
        
        // Create reply form
        const replyForm = document.createElement('form');
        replyForm.classList.add('reply-form');
        replyForm.action = `/api/comments/${commentId}/reply`;
        replyForm.method = 'post';
        
        replyForm.innerHTML = `
          <div class="form-group">
            <label for="reply-${commentId}">Reply to this comment</label>
            <textarea id="reply-${commentId}" name="content" rows="3" required></textarea>
          </div>
          <div class="form-actions">
            <button type="submit" class="btn btn-primary">Submit Reply</button>
            <button type="button" class="btn btn-secondary cancel-reply">Cancel</button>
          </div>
        `;
        
        commentElement.appendChild(replyForm);
        
        // Focus the textarea
        replyForm.querySelector('textarea').focus();
        
        // Cancel reply
        replyForm.querySelector('.cancel-reply').addEventListener('click', () => {
          replyForm.remove();
        });
        
        // Handle submit
        replyForm.addEventListener('submit', (e) => {
          e.preventDefault();
          
          const content = replyForm.querySelector('textarea').value.trim();
          
          if (!content) {
            return;
          }
          
          // In production, use AJAX to submit the reply
          /*
          fetch(replyForm.action, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content
            },
            body: JSON.stringify({ content })
          })
          .then(response => response.json())
          .then(data => {
            if (data.success) {
              // Add the reply to the page
              const replyElement = document.createElement('div');
              replyElement.classList.add('comment', 'comment-reply');
              replyElement.innerHTML = `
                <div class="comment-header">
                  <img src="${data.user.avatar}" alt="${data.user.name}" class="commenter-avatar">
                  <div class="comment-meta">
                    <span class="commenter-name">${data.user.name}</span>
                    <span class="comment-date">Just now</span>
                  </div>
                </div>
                <div class="comment-body">
                  <p>${data.content}</p>
                </div>
              `;
              
              commentElement.parentNode.insertBefore(replyElement, commentElement.nextSibling);
              
              // Remove the form
              replyForm.remove();
            } else {
              alert(data.message || 'Failed to submit reply.');
            }
          })
          .catch(error => {
            alert('Failed to submit reply.');
          });
          */
          
          // Simulate successful reply for demo
          const replyElement = document.createElement('div');
          replyElement.classList.add('comment', 'comment-reply');
          replyElement.innerHTML = `
            <div class="comment-header">
              <img src="/static/assets/images/avatar-placeholder.jpg" alt="Your Name" class="commenter-avatar">
              <div class="comment-meta">
                <span class="commenter-name">Your Name</span>
                <span class="comment-date">Just now</span>
              </div>
            </div>
            <div class="comment-body">
              <p>${content}</p>
            </div>
          `;
          
          commentElement.parentNode.insertBefore(replyElement, commentElement.nextSibling);
          
          // Remove the form
          replyForm.remove();
        });
      });
    });
  });