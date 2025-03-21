"""
User role definitions and permissions for the personal website.
"""

# Define all permissions
PERMISSIONS = {
    # Article permissions
    'can_view_articles': 'Can view published articles',
    'can_create_articles': 'Can create new articles',
    'can_edit_own_articles': 'Can edit own articles',
    'can_delete_own_articles': 'Can delete own articles',
    'can_edit_any_article': 'Can edit any article',
    'can_delete_any_article': 'Can delete any article', 
    'can_publish_articles': 'Can publish articles',
    'can_feature_articles': 'Can feature articles on homepage',
    
    # Comment permissions
    'can_comment': 'Can post comments on articles',
    'can_edit_own_comments': 'Can edit own comments',
    'can_delete_own_comments': 'Can delete own comments',
    'can_delete_any_comment': 'Can delete any comment',
    'can_moderate_comments': 'Can approve or reject comments',
    
    # User permissions
    'can_view_profiles': 'Can view user profiles',
    'can_edit_own_profile': 'Can edit own profile',
    'can_manage_users': 'Can create, edit, and delete users',
    'can_assign_roles': 'Can assign roles to users',
    
    # Category and tag permissions
    'can_manage_categories': 'Can create, edit, and delete categories',
    'can_manage_tags': 'Can create, edit, and delete tags',
    
    # Website settings
    'can_manage_settings': 'Can modify website settings',
    'can_view_stats': 'Can view website statistics',
    
    # Other permissions
    'can_upload_files': 'Can upload files',
    'can_access_api': 'Can access the API',
}

# Define roles and their corresponding permissions
ROLES = {
    'viewer': {
        'description': 'Regular user who can read content and post comments',
        'permissions': [
            'can_view_articles',
            'can_comment',
            'can_edit_own_comments',
            'can_delete_own_comments',
            'can_view_profiles',
            'can_edit_own_profile',
            'can_access_api'
        ]
    },
    'contributor': {
        'description': 'Content creator who can write and manage their own articles',
        'permissions': [
            'can_view_articles',
            'can_comment',
            'can_edit_own_comments',
            'can_delete_own_comments',
            'can_view_profiles',
            'can_edit_own_profile',
            'can_access_api',
            'can_create_articles',
            'can_edit_own_articles',
            'can_delete_own_articles',
            'can_publish_articles',
            'can_upload_files'
        ]
    },
    'admin': {
        'description': 'Administrator with full access to all features',
        'permissions': list(PERMISSIONS.keys())  # All permissions
    }
}

def get_role_permissions(role):
    """
    Get all permissions for a specific role.
    
    Args:
        role (str): Role name ('viewer', 'contributor', 'admin')
        
    Returns:
        list: List of permission strings
    """
    return ROLES.get(role, {}).get('permissions', [])

def has_permission(user_role, permission):
    """
    Check if a role has a specific permission.
    
    Args:
        user_role (str): Role name ('viewer', 'contributor', 'admin')
        permission (str): Permission to check
        
    Returns:
        bool: True if the role has the permission, False otherwise
    """
    if user_role == 'admin':
        return True  # Admin has all permissions
    
    permissions = get_role_permissions(user_role)
    return permission in permissions

def role_exists(role):
    """
    Check if a role exists.
    
    Args:
        role (str): Role name to check
        
    Returns:
        bool: True if the role exists, False otherwise
    """
    return role in ROLES