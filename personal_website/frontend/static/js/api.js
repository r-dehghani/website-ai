/**
 * API Interaction JavaScript
 * Handles all frontend API calls to the backend
 */

class API {
    /**
     * Initialize API with base URL and headers
     */
    constructor() {
      this.baseUrl = '/api';
      this.headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      };
      
      // Add CSRF token if available
      const csrfToken = document.querySelector('meta[name="csrf-token"]');
      if (csrfToken) {
        this.headers['X-CSRF-TOKEN'] = csrfToken.content;
      }
    }
    
    /**
     * Make a request to the API
     * @param {string} endpoint - API endpoint
     * @param {string} method - HTTP method (GET, POST, PUT, DELETE)
     * @param {object} data - Request data (for POST and PUT)
     * @param {boolean} useFormData - Whether to use FormData for file uploads
     * @returns {Promise} - API response
     */
    async request(endpoint, method = 'GET', data = null, useFormData = false) {
      const url = `${this.baseUrl}${endpoint}`;
      const options = {
        method,
        headers: useFormData ? {} : this.headers,
        credentials: 'same-origin'
      };
      
      if (data) {
        if (useFormData) {
          // Use FormData for file uploads
          options.body = data;
        } else {
          options.body = JSON.stringify(data);
        }
      }
      
      try {
        const response = await fetch(url, options);
        
        // Check for HTTP errors
        if (!response.ok) {
          const error = await response.json();
          throw new Error(error.message || 'API request failed');
        }
        
        // Parse and return JSON response
        return await response.json();
      } catch (error) {
        console.error('API Error:', error);
        throw error;
      }
    }
    
    /**
     * GET request
     * @param {string} endpoint - API endpoint
     * @returns {Promise} - API response
     */
    async get(endpoint) {
      return this.request(endpoint, 'GET');
    }
    
    /**
     * POST request
     * @param {string} endpoint - API endpoint
     * @param {object} data - Request data
     * @param {boolean} useFormData - Whether to use FormData
     * @returns {Promise} - API response
     */
    async post(endpoint, data, useFormData = false) {
      return this.request(endpoint, 'POST', data, useFormData);
    }
    
    /**
     * PUT request
     * @param {string} endpoint - API endpoint
     * @param {object} data - Request data
     * @param {boolean} useFormData - Whether to use FormData
     * @returns {Promise} - API response
     */
    async put(endpoint, data, useFormData = false) {
      return this.request(endpoint, 'PUT', data, useFormData);
    }
    
    /**
     * DELETE request
     * @param {string} endpoint - API endpoint
     * @returns {Promise} - API response
     */
    async delete(endpoint) {
      return this.request(endpoint, 'DELETE');
    }
    
    /**
     * Upload a file
     * @param {string} endpoint - API endpoint
     * @param {File} file - File to upload
     * @param {object} additionalData - Additional form data
     * @returns {Promise} - API response
     */
    async uploadFile(endpoint, file, additionalData = {}) {
      const formData = new FormData();
      formData.append('file', file);
      
      // Add any additional data
      for (const [key, value] of Object.entries(additionalData)) {
        formData.append(key, value);
      }
      
      return this.post(endpoint, formData, true);
    }
    
    // Authentication API methods
    
    /**
     * Log in a user
     * @param {string} email - User email
     * @param {string} password - User password
     * @param {boolean} remember - Remember me
     * @returns {Promise} - API response with user data
     */
    async login(email, password, remember = false) {
      return this.post('/auth/login', { email, password, remember });
    }
    
    /**
     * Register a new user
     * @param {object} userData - User registration data
     * @returns {Promise} - API response with user data
     */
    async register(userData) {
      return this.post('/auth/register', userData);
    }
    
    /**
     * Log out the current user
     * @returns {Promise} - API response
     */
    async logout() {
      return this.post('/auth/logout');
    }
    
    /**
     * Request password reset
     * @param {string} email - User email
     * @returns {Promise} - API response
     */
    async forgotPassword(email) {
      return this.post('/auth/forgot-password', { email });
    }
    
    /**
     * Reset password with token
     * @param {string} token - Reset token
     * @param {string} password - New password
     * @param {string} passwordConfirmation - Confirm new password
     * @returns {Promise} - API response
     */
    async resetPassword(token, password, passwordConfirmation) {
      return this.post('/auth/reset-password', { 
        token, 
        password, 
        password_confirmation: passwordConfirmation 
      });
    }
    
    // User API methods
    
    /**
     * Get current user data
     * @returns {Promise} - API response with user data
     */
    async getCurrentUser() {
      return this.get('/user');
    }
    
    /**
     * Update user profile
     * @param {object} userData - User profile data
     * @returns {Promise} - API response with updated user data
     */
    async updateProfile(userData) {
      return this.put('/user/profile', userData);
    }
    
    /**
     * Update user password
     * @param {string} currentPassword - Current password
     * @param {string} newPassword - New password
     * @param {string} newPasswordConfirmation - Confirm new password
     * @returns {Promise} - API response
     */
    async updatePassword(currentPassword, newPassword, newPasswordConfirmation) {
      return this.put('/user/password', {
        current_password: currentPassword,
        password: newPassword,
        password_confirmation: newPasswordConfirmation
      });
    }
    
    /**
     * Upload user avatar
     * @param {File} avatarFile - Avatar image file
     * @returns {Promise} - API response with avatar URL
     */
    async uploadAvatar(avatarFile) {
      return this.uploadFile('/user/avatar', avatarFile);
    }
    
    // Article API methods
    
    /**
     * Get articles list with optional filters
     * @param {object} filters - Filter parameters
     * @returns {Promise} - API response with articles data
     */
    async getArticles(filters = {}) {
      const params = new URLSearchParams();
      
      for (const [key, value] of Object.entries(filters)) {
        if (value) {
          params.append(key, value);
        }
      }
      
      const query = params.toString() ? `?${params.toString()}` : '';
      return this.get(`/articles${query}`);
    }
    
    /**
     * Get a single article by slug
     * @param {string} slug - Article slug
     * @returns {Promise} - API response with article data
     */
    async getArticle(slug) {
      return this.get(`/articles/${slug}`);
    }
    
    /**
     * Create a new article
     * @param {object} articleData - Article data
     * @returns {Promise} - API response with created article
     */
    async createArticle(articleData) {
      return this.post('/articles', articleData);
    }
    
    /**
     * Update an existing article
     * @param {number} id - Article ID
     * @param {object} articleData - Updated article data
     * @returns {Promise} - API response with updated article
     */
    async updateArticle(id, articleData) {
      return this.put(`/articles/${id}`, articleData);
    }
    
    /**
     * Delete an article
     * @param {number} id - Article ID
     * @returns {Promise} - API response
     */
    async deleteArticle(id) {
      return this.delete(`/articles/${id}`);
    }
    
    /**
     * Save article as draft
     * @param {object} articleData - Article draft data
     * @returns {Promise} - API response with saved draft
     */
    async saveDraft(articleData) {
      return this.post('/articles/draft', articleData);
    }
    
    /**
     * Publish a draft article
     * @param {number} id - Draft article ID
     * @returns {Promise} - API response with published article
     */
    async publishDraft(id) {
      return this.put(`/articles/${id}/publish`);
    }
    
    /**
     * Upload article featured image
     * @param {File} imageFile - Image file
     * @returns {Promise} - API response with image URL
     */
    async uploadArticleImage(imageFile) {
      return this.uploadFile('/articles/image', imageFile);
    }
    
    // Comment API methods
    
    /**
     * Get comments for an article
     * @param {string} articleSlug - Article slug
     * @returns {Promise} - API response with comments data
     */
    async getComments(articleSlug) {
      return this.get(`/articles/${articleSlug}/comments`);
    }
    
    /**
     * Add a comment to an article
     * @param {string} articleSlug - Article slug
     * @param {string} content - Comment content
     * @returns {Promise} - API response with created comment
     */
    async addComment(articleSlug, content) {
      return this.post(`/articles/${articleSlug}/comments`, { content });
    }
    
    /**
     * Update a comment
     * @param {number} id - Comment ID
     * @param {string} content - Updated comment content
     * @returns {Promise} - API response with updated comment
     */
    async updateComment(id, content) {
      return this.put(`/comments/${id}`, { content });
    }
    
    /**
     * Delete a comment
     * @param {number} id - Comment ID
     * @returns {Promise} - API response
     */
    async deleteComment(id) {
      return this.delete(`/comments/${id}`);
    }
    
    /**
     * Reply to a comment
     * @param {number} commentId - Parent comment ID
     * @param {string} content - Reply content
     * @returns {Promise} - API response with created reply
     */
    async replyToComment(commentId, content) {
      return this.post(`/comments/${commentId}/reply`, { content });
    }
    
    // Admin API methods
    
    /**
     * Get all users (admin only)
     * @param {object} filters - Filter parameters
     * @returns {Promise} - API response with users data
     */
    async getUsers(filters = {}) {
      const params = new URLSearchParams();
      
      for (const [key, value] of Object.entries(filters)) {
        if (value) {
          params.append(key, value);
        }
      }
      
      const query = params.toString() ? `?${params.toString()}` : '';
      return this.get(`/admin/users${query}`);
    }
    
    /**
     * Get a single user (admin only)
     * @param {number} id - User ID
     * @returns {Promise} - API response with user data
     */
    async getUser(id) {
      return this.get(`/admin/users/${id}`);
    }
    
    /**
     * Update a user (admin only)
     * @param {number} id - User ID
     * @param {object} userData - Updated user data
     * @returns {Promise} - API response with updated user
     */
    async updateUser(id, userData) {
      return this.put(`/admin/users/${id}`, userData);
    }
    
    /**
     * Delete a user (admin only)
     * @param {number} id - User ID
     * @returns {Promise} - API response
     */
    async deleteUser(id) {
      return this.delete(`/admin/users/${id}`);
    }
    
    /**
     * Update user role (admin only)
     * @param {number} id - User ID
     * @param {string} role - New role
     * @returns {Promise} - API response
     */
    async updateUserRole(id, role) {
      return this.put(`/admin/users/${id}/role`, { role });
    }
    
    /**
     * Update site settings (admin only)
     * @param {object} settings - Site settings
     * @returns {Promise} - API response with updated settings
     */
    async updateSettings(settings) {
      return this.put('/admin/settings', settings);
    }
    
    /**
     * Get site statistics (admin only)
     * @returns {Promise} - API response with site statistics
     */
    async getStatistics() {
      return this.get('/admin/statistics');
    }
  }
  
  // Create and export API instance
  const api = new API();
  export default api;