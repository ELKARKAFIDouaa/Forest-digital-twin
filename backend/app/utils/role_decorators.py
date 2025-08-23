from functools import wraps
from flask import flash, redirect, url_for, abort, jsonify
from flask_login import current_user

def permission_required(permission_name):
    """Décorateur pour vérifier une permission spécifique"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Authentication required.', 'warning')
                return redirect(url_for('auth.login'))
            
            if not current_user.has_permission(permission_name):
                flash('Insufficient permissions.', 'danger')
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def role_required(role_name):
    """Décorateur pour vérifier un rôle spécifique"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Authentication required.', 'warning')
                return redirect(url_for('auth.login'))
            
            if not current_user.has_role(role_name):
                flash('Insufficient role privileges.', 'danger')
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Décorateurs spécifiques
def admin_required(f):
    return role_required('admin')(f)

def can_manage_users(f):
    return permission_required('manage_users')(f)

def can_manage_iot(f):
    return permission_required('manage_iot')(f)

def can_view_reports(f):
    return permission_required('view_reports')(f)