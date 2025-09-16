from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import datetime

auth_bp = Blueprint('auth', __name__)

USERS = {
    'demo@smartad.com': {
        'password': 'demo123',
        'name': 'Demo User',
        'company': 'SmartAd Demo'
    }
}

@auth_bp.route('/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        user = USERS.get(email)
        if not user or user['password'] != password:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        access_token = create_access_token(
            identity=email,
            expires_delta=datetime.timedelta(hours=24)
        )
        
        return jsonify({
            'success': True,
            'access_token': access_token,
            'user': {
                'email': email,
                'name': user['name'],
                'company': user['company']
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@auth_bp.route('/auth/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        email = get_jwt_identity()
        user = USERS.get(email)
        
        return jsonify({
            'success': True,
            'user': {
                'email': email,
                'name': user['name'],
                'company': user['company']
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500
