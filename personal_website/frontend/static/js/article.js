/**
 * JavaScript for Article Pages
 */

document.addEventListener('DOMContentLoaded', () => {
    // Comment form submission
    const commentForm = document.querySelector('.comment-form');
    
    if (commentForm) {
      commentForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const commentTextarea = commentForm.querySelector('textarea');
        const submitButton = commentForm.querySelector('button[type="submit"]');
        
        if (!commentTextarea || !commentTextarea.value.trim()) {
          // Show error if comment is empty
          commentTextarea.classList.add('is-invalid');
          return;
        }
        
        // Clear error state
        commentTextarea.classList.remove('is-invalid');
        
        // Get comment data
        const articleSlug = window.location.pathname.split('/').pop();
        const commentContent = commentTextarea.value.trim();
        
        // Disable button and show loading state
        submitButton.disabled = true;
        const originalButtonText = submitButton.textContent;
        submitButton.textContent = 'Posting...';
        
        // In production, use AJAX to submit the comment
        /*
        fetch(`/api/articles/${articleSlug}/comments`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content
          },
          body: JSON.stringify({ comment: commentContent })
        })
        .then(response => response.json())
        .then(data => {
          // Re-enable button
          submitButton.disabled = false;
          submitButton.textContent = originalButtonText;
          
          if (data.success) {
            // Clear the textarea
            commentTextarea.value = '';
            
            // Add the comment to the page
            addCommentToPage(data.comment);
            
            // Update comment count
            updateCommentCount(1);
          } else {
            alert(data.message || 'Failed to post comment.');
          }
        })
        .catch(error => {
          // Re-enable button
          submitButton.disabled = false;
          submitButton.textContent = originalButtonText;
          
          alert('Failed to post comment.');
        });
        */
        
        // Simulate successful comment submission for demo
        setTimeout(() => {
          // Re-enable button
          submitButton.disabled = false;
          submitButton.textContent = originalButtonText;
          
          // Clear the textarea
          commentTextarea.value = '';
          
          // Add the comment to the page
          const demoComment = {
            id: Date.now(),
            content: commentContent,
            created_at: 'Just now',
            user: {
              name: 'Current User',
              avatar: '/static/assets/images/avatar-placeholder.jpg'
            }
          };
          
          addCommentToPage(demoComment);
          
          // Update comment count
          updateCommentCount(1);
        }, 1000);
      });
    }
    
    // Add comment to the page
    function addCommentToPage(comment) {
      const commentsList = document.querySelector('.comments-list');
      const noComments = document.querySelector('.no-comments');
      
      if (noComments) {
        noComments.remove();
      }
      
      const commentElement = document.createElement('div');
      commentElement.classList.add('comment');
      commentElement.id = `comment-${comment.id}`;
      
      commentElement.innerHTML = `
        <div class="comment-header">
          <img src="${comment.user.avatar}" alt="${comment.user.name}" class="commenter-avatar">
          <div class="comment-meta">
            <span class="commenter-name">${comment.user.name}</span>
            <span class="comment-date">${comment.created_at}</span>
          </div>
        </div>
        <div class="comment-body">
          <p>${comment.content}</p>
        </div>
        <div class="comment-actions">
          <button class="btn-text edit-comment" data-id="${comment.id}">Edit</button>
          <form action="/comments/${comment.id}/delete" method="post" class="delete-form">
            <button type="submit" class="btn-text delete-comment">Delete</button>
          </form>
        </div>
      `;
      
      // Add the new comment at the top of the list
      commentsList.prepend(commentElement);
      
      // Smooth scroll to the new comment
      commentElement.scrollIntoView({ behavior: 'smooth' });
    }
    
    // Update comment count
    function updateCommentCount(increment) {
      const countElement = document.querySelector('.article-comments h2');
      
      if (countElement) {
        const currentText = countElement.textContent;
        const regex = /Comments \((\d+)\)/;
        const match = currentText.match(regex);
        
        if (match) {
          const currentCount = parseInt(match[1], 10);
          const newCount = currentCount + increment;
          countElement.textContent = `Comments (${newCount})`;
        }
      }
    }
    
    // Edit comment functionality
    document.addEventListener('click', (e) => {
      if (e.target.classList.contains('edit-comment')) {
        const commentId = e.target.dataset.id;
        const commentElement = document.getElementById(`comment-${commentId}`);
        const commentBody = commentElement.querySelector('.comment-body');
        const commentContent = commentBody.querySelector('p').textContent;
        
        // Create edit form
        const editForm = document.createElement('form');
        editForm.classList.add('edit-comment-form');
        editForm.innerHTML = `
          <div class="form-group">
            <textarea rows="3" required>${commentContent}</textarea>
          </div>
          <div class="form-actions">
            <button type="submit" class="btn btn-primary">Save</button>
            <button type="button" class="btn btn-text cancel-edit">Cancel</button>
          </div>
        `;
        
        // Replace comment body with edit form
        commentBody.innerHTML = '';
        commentBody.appendChild(editForm);
        
        // Focus textarea
        const textarea = editForm.querySelector('textarea');
        textarea.focus();
        
        // Cancel edit
        editForm.querySelector('.cancel-edit').addEventListener('click', () => {
          commentBody.innerHTML = `<p>${commentContent}</p>`;
        });
        
        // Submit edit form
        editForm.addEventListener('submit', (e) => {
          e.preventDefault();
          
          const updatedContent = textarea.value.trim();
          
          if (!updatedContent) {
            textarea.classList.add('is-invalid');
            return;
          }
          
          // In production, use AJAX to update the comment
          /*
          fetch(`/api/comments/${commentId}`, {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content
            },
            body: JSON.stringify({ content: updatedContent })
          })
          .then(response => response.json())
          .then(data => {
            if (data.success) {
              // Update the comment content
              commentBody.innerHTML = `<p>${updatedContent}</p>`;
            } else {
              alert(data.message || 'Failed to update comment.');
              commentBody.innerHTML = `<p>${commentContent}</p>`;
            }
          })
          .catch(error => {
            alert('Failed to update comment.');
            commentBody.innerHTML = `<p>${commentContent}</p>`;
          });
          */
          
          // Simulate successful edit for demo
          commentBody.innerHTML = `<p>${updatedContent}</p>`;
        });
      }
    });
    
    // Delete comment confirmation
    const deleteCommentForms = document.querySelectorAll('.delete-form');
    
    deleteCommentForms.forEach(form => {
      form.addEventListener('submit', (e) => {
        if (!confirm('Are you sure you want to delete this comment?')) {
          e.preventDefault();
        }
      });
    });
    
    // Social sharing functionality
    const shareButtons = document.querySelectorAll('.share-button');
    
    shareButtons.forEach(button => {
      button.addEventListener('click', (e) => {
        e.preventDefault();
        
        const url = button.getAttribute('href');
        
        // Open share dialog in a popup window
        window.open(url, 'share-dialog', 'width=600,height=400');
      });
    });
    
    // Reading time calculation
    const articleBody = document.querySelector('.article-body');
    const readTimeSpan = document.querySelector('.read-time');
    
    if (articleBody && readTimeSpan && !readTimeSpan.textContent.includes('min read')) {
      // Get article text content
      const text = articleBody.textContent.trim();
      
      // Calculate reading time based on average reading speed (200 words per minute)
      const wordCount = text.split(/\s+/).length;
      const readTimeMinutes = Math.ceil(wordCount / 200);
      
      // Update the reading time
      readTimeSpan.textContent = `${readTimeMinutes} min read`;
    }
    
    // Table of contents generation
    const articleContent = document.querySelector('.article-body');
    const tocContainer = document.querySelector('.table-of-contents');
    
    if (articleContent && tocContainer) {
      const headings = articleContent.querySelectorAll('h2, h3');
      
      if (headings.length > 0) {
        const tocList = document.createElement('ul');
        tocList.classList.add('toc-list');
        
        headings.forEach((heading, index) => {
          // Add ID to heading if it doesn't have one
          if (!heading.id) {
            heading.id = `heading-${index}`;
          }
          
          const listItem = document.createElement('li');
          listItem.classList.add(`toc-${heading.tagName.toLowerCase()}`);
          
          const link = document.createElement('a');
          link.href = `#${heading.id}`;
          link.textContent = heading.textContent;
          
          listItem.appendChild(link);
          tocList.appendChild(listItem);
          
          // Add click event to scroll smoothly
          link.addEventListener('click', (e) => {
            e.preventDefault();
            
            document.querySelector(link.getAttribute('href')).scrollIntoView({
              behavior: 'smooth'
            });
          });
        });
        
        tocContainer.appendChild(tocList);
      } else {
        // Hide the TOC container if no headings found
        tocContainer.style.display = 'none';
      }
    }
    
    // Syntax highlighting for code blocks
    const codeBlocks = document.querySelectorAll('pre code');
    
    if (codeBlocks.length > 0) {
      // In production, use a syntax highlighting library like Prism.js or Highlight.js
      codeBlocks.forEach(block => {
        block.classList.add('syntax-highlighted');
      });
    }
    
    // Image lightbox
    const articleImages = document.querySelectorAll('.article-body img');
    
    articleImages.forEach(img => {
      // Make images clickable for lightbox view
      img.style.cursor = 'pointer';
      
      img.addEventListener('click', () => {
        // Create lightbox overlay
        const lightbox = document.createElement('div');
        lightbox.classList.add('lightbox-overlay');
        
        const lightboxImg = document.createElement('img');
        lightboxImg.src = img.src;
        lightboxImg.alt = img.alt;
        
        const closeBtn = document.createElement('button');
        closeBtn.classList.add('lightbox-close');
        closeBtn.innerHTML = '&times;';
        
        lightbox.appendChild(lightboxImg);
        lightbox.appendChild(closeBtn);
        document.body.appendChild(lightbox);
        
        // Prevent scrolling on body when lightbox is open
        document.body.style.overflow = 'hidden';
        
        // Add animation class after a brief delay (for transition effect)
        setTimeout(() => {
          lightbox.classList.add('active');
        }, 10);
        
        // Close lightbox on button click
        closeBtn.addEventListener('click', closeLightbox);
        
        // Close lightbox on overlay click
        lightbox.addEventListener('click', (e) => {
          if (e.target === lightbox) {
            closeLightbox();
          }
        });
        
        // Close lightbox on ESC key press
        document.addEventListener('keydown', (e) => {
          if (e.key === 'Escape') {
            closeLightbox();
          }
        });
        
        function closeLightbox() {
          lightbox.classList.remove('active');
          
          // Remove lightbox after animation
          setTimeout(() => {
            document.body.removeChild(lightbox);
            document.body.style.overflow = '';
          }, 300);
        }
      });
    });
  });