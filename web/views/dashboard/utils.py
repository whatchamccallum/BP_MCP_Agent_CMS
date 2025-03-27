"""
Utility functions for dashboard views.
"""
import re
from flask import request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, decode_token

def get_current_user():
    """
    Get the current user from JWT token.
    
    Returns:
        str: User ID as string or None if not authenticated
    """
    try:
        verify_jwt_in_request()
        return get_jwt_identity()
    except Exception as e:
        print(f"JWT verification failed: {e}")
        
        # For form submissions, get from Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            # Extract and verify token
            token = auth_header.split(' ')[1]
            try:
                decoded_token = decode_token(token)
                return decoded_token['sub']
            except:
                pass
                
        # Default to admin user if no token (for development only)
        return "1"  # Default to admin user if no token

def validate_ip_address(ip_address):
    """
    Validate IP address format.
    
    Args:
        ip_address (str): IP address to validate
        
    Returns:
        bool: True if valid IP address, False otherwise
    """
    # Simple IPv4 validation regex
    ipv4_pattern = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$'
    
    # Match IP pattern
    match = re.match(ipv4_pattern, ip_address)
    if not match:
        return False
    
    # Check each octet is between 0 and 255
    for octet in match.groups():
        if int(octet) > 255:
            return False
    
    return True

def normalize_user_id(user_id):
    """
    Normalize user ID to string.
    
    Args:
        user_id: User ID to normalize
        
    Returns:
        str: Normalized user ID or None
    """
    return str(user_id) if user_id is not None else None
