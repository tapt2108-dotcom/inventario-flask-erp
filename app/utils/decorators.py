"""
Role-based access control decorators for Flask routes.
Provides decorators to restrict access based on user roles.
"""
from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def admin_required(f):
    """
    Decorator to restrict route access to admin users only.
    
    Usage:
        @bp.route('/admin-only')
        @login_required
        @admin_required
        def admin_only_route():
            return "Admin content"
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Por favor inicia sesión para acceder a esta página.')
            return redirect(url_for('auth.login'))
        
        if not current_user.has_role('admin'):
            flash('No tienes permiso para acceder a esta página. Se requiere rol de administrador.')
            return redirect(url_for('dashboard.index'))
        
        return f(*args, **kwargs)
    return decorated_function

def role_required(role):
    """
    Decorator to restrict route access to users with a specific role.
    
    Args:
        role (str): The required role ('admin' or 'seller')
    
    Usage:
        @bp.route('/seller-route')
        @login_required
        @role_required('seller')
        def seller_route():
            return "Seller content"
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Por favor inicia sesión para acceder a esta página.')
                return redirect(url_for('auth.login'))
            
            if not current_user.has_role(role):
                flash(f'No tienes permiso para acceder a esta página. Se requiere rol de {role}.')
                return redirect(url_for('dashboard.index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
