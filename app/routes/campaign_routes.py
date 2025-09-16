from flask import Blueprint, request, jsonify
from app.services.ai_service import AIService
from app.utils.validators import validate_campaign_data

campaign_bp = Blueprint('campaign', __name__)
ai_service = AIService()

@campaign_bp.route('/campaign/recommendations', methods=['POST'])
def get_recommendations():
    try:
        data = request.get_json()
        
        error = validate_campaign_data(data)
        if error:
            return jsonify({'error': error, 'success': False}), 400
        
        recommendations = ai_service.generate_recommendations(data)
        
        return jsonify({
            'success': True,
            'data': recommendations
        })
        
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@campaign_bp.route('/platforms', methods=['GET'])
def get_platforms():
    platforms = {
        'google_ads': {
            'name': 'Google Ads',
            'types': ['Search', 'Display', 'Shopping'],
            'min_budget': 10
        },
        'meta_ads': {
            'name': 'Meta Ads',
            'types': ['Feed', 'Stories', 'Reels'],
            'min_budget': 5
        },
        'linkedin_ads': {
            'name': 'LinkedIn Ads',
            'types': ['Sponsored', 'Message'],
            'min_budget': 10
        }
    }
    
    return jsonify({'success': True, 'platforms': platforms})
