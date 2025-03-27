"""
Authentication API routes.
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)

from api.models import db
from api.models.user import User

auth_blueprint = Blueprint('auth', __name__)


@auth_blueprint.route('/login', methods=['POST'])
def login():
    """User login."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Check if username/email and password are provided
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not password:
        return jsonify({'error': 'Password is required'}), 400
    
    if not username and not email:
        return jsonify({'error': 'Username or email is required'}), 400
    
    # Find the user by username or email
    if username:
        user = User.query.filter_by(username=username).first()
    else:
        user = User.query.filter_by(email=email).first()
    
    if not user or not user.verify_password(password):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Create tokens
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict()
    })


@auth_blueprint.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token."""
    current_user_id = get_jwt_identity()
    access_token = create_access_token(identity=current_user_id)
    
    return jsonify({'access_token': access_token})


@auth_blueprint.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """User logout."""
    # In a stateless JWT setup, there's nothing to do on the server side
    # The client should just discard the tokens
    
    return jsonify({'message': 'Logout successful'})


@auth_blueprint.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user info."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(user.to_dict())


@auth_blueprint.route('/password', methods=['PUT'])
@jwt_required()
def change_password():
    """Change user password."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    if not current_password or not new_password:
        return jsonify({'error': 'Current password and new password are required'}), 400
    
    if not user.verify_password(current_password):
        return jsonify({'error': 'Current password is incorrect'}), 401
    
    user.set_password(new_password)
    
    try:
        db.session.commit()
        return jsonify({'message': 'Password changed successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
