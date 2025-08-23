from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.services.role_service import RoleService
from app.utils.role_decorators import admin_required, can_manage_users

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
@login_required
@admin_required
def require_admin():
    """Toutes les routes admin nécessitent le rôle admin"""
    pass

@admin_bp.route('/roles')
def manage_roles():
    """Gestion des rôles"""
    roles = RoleService.get_all_roles()
    return render_template('admin/roles.html', roles=roles)

@admin_bp.route('/users')
@can_manage_users
def manage_users():
    """Gestion des utilisateurs"""
    from app.models.user import User
    users = User.query.all()
    roles = RoleService.get_all_roles()
    return render_template('admin/users.html', users=users, roles=roles)

@admin_bp.route('/api/assign-role', methods=['POST'])
def api_assign_role():
    """API pour assigner un rôle"""
    user_id = request.json.get('user_id')
    role_name = request.json.get('role_name')
    
    if RoleService.assign_role_to_user(user_id, role_name):
        return jsonify({'success': True, 'message': 'Role assigned successfully'})
    return jsonify({'success': False, 'message': 'Error assigning role'}), 400

@admin_bp.route('/api/remove-role', methods=['POST'])
def api_remove_role():
    """API pour retirer un rôle"""
    user_id = request.json.get('user_id')
    role_name = request.json.get('role_name')
    
    if RoleService.remove_role_from_user(user_id, role_name):
        return jsonify({'success': True, 'message': 'Role removed successfully'})
    return jsonify({'success': False, 'message': 'Error removing role'}), 400