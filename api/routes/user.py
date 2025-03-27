"""
User API routes.
"""

from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError

from api.models import db
from api.models.user import User

user_blueprint = Blueprint('user', __name__)


@user_blueprint.route('', methods=['GET'])
@jwt_required()
def get_users():
    """Get all users."""
    # Get current user to check if admin
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user or not current_user.is_admin:
        return jsonify({'error': 'Unauthorized - Admin access required'}), 403
    
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])


@user_blueprint.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_user(id):
    """Get user by ID."""
    # Get current user to check if admin or self
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user or (not current_user.is_admin and current_user.id != id):
        return jsonify({'error': 'Unauthorized - Admin access or self required'}), 403
    
    user = User.query.get_or_404(id)
    return jsonify(user.to_dict())


@user_blueprint.route('', methods=['POST'])
@jwt_required()
def create_user():
    """Create a new user."""
    # Get current user to check if admin
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user or not current_user.is_admin:
        return jsonify({'error': 'Unauthorized - Admin access required'}), 403
    
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    required_fields = ['username', 'email', 'password']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    user = User(
        username=data['username'],
        email=data['email'],
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        is_admin=data.get('is_admin', False)
    )
    
    # Set password
    user.set_password(data['password'])
    
    try:
        db.session.add(user)
        db.session.commit()
        return jsonify(user.to_dict()), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'User with this username or email already exists'}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@user_blueprint.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_user(id):
    """Update a user."""
    # Get current user to check if admin or self
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user or (not current_user.is_admin and current_user.id != id):
        return jsonify({'error': 'Unauthorized - Admin access or self required'}), 403
    
    user = User.query.get_or_404(id)
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Only allow admin to change is_admin
    if 'is_admin' in data and not current_user.is_admin:
        return jsonify({'error': 'Unauthorized - Admin access required to change admin status'}), 403
    
    if 'username' in data:
        user.username = data['username']
    
    if 'email' in data:
        user.email = data['email']
    
    if 'first_name' in data:
        user.first_name = data['first_name']
    
    if 'last_name' in data:
        user.last_name = data['last_name']
    
    if 'is_admin' in data and current_user.is_admin:
        user.is_admin = data['is_admin']
    
    if 'password' in data:
        user.set_password(data['password'])
    
    try:
        db.session.commit()
        return jsonify(user.to_dict())
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'User with this username or email already exists'}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@user_blueprint.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_user(id):
    """Delete a user."""
    # Get current user to check if admin
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user or not current_user.is_admin:
        return jsonify({'error': 'Unauthorized - Admin access required'}), 403
    
    # Prevent deleting self
    if current_user.id == id:
        return jsonify({'error': 'Cannot delete self'}), 400
    
    user = User.query.get_or_404(id)
    
    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
