from flask import Blueprint, request, jsonify
from app.services.ai_service import ai_service
from app.utils.validators import validate_campaign_data

campaign_bp = Blueprint('campaign', __name__)

@campaign_bp.route('/campaign/recommendations', methods=['POST'])
def get_recommendations():
    try:
        data = request.get_json()
        
        # Validate campaign data
        error = validate_campaign_data(data)
        if error:
            return jsonify({'error': error, 'success': False}), 400
        
        print(f"📥 Received campaign data: {data}")
        
        # Get AI recommendations using the trained ML model
        recommendations = ai_service.get_recommendations(data)
        
        print(f"🤖 AI Recommendations generated: {recommendations['recommended_platform']}")
        
        # Format response to match frontend expectations
        total_budget = data.get('budget', 1000)
        budget_allocation_formatted = {}
        
        for platform, amount in recommendations['budget_allocation'].items():
            percentage = (amount / total_budget) * 100
            budget_allocation_formatted[platform] = {
                'amount': int(amount),
                'percentage': round(percentage, 1)
            }
        
        formatted_recommendations = {
            # Direct fields that AISuggestions expects
            'recommended_platform': recommendations['recommended_platform'],
            'platform_scores': recommendations['platform_scores'],
            'confidence_score': recommendations['confidence_score'],
            'budget_allocation': budget_allocation_formatted,
            'ad_copy_suggestions': recommendations['ad_copy_suggestions'],
            'optimal_timing': recommendations['optimal_timing'],
            'performance_predictions': {
                'estimated_ctr': recommendations['performance_predictions']['estimated_ctr'],
                'estimated_conversions': int(recommendations['performance_predictions']['estimated_conversions'] * 100),  # Convert to actual number
                'estimated_reach': recommendations['performance_predictions']['estimated_reach']
            },
            'insights': [
                f"Based on your {data['objectives'][0]} objective, {recommendations['recommended_platform']} is the optimal platform",
                f"Expected CTR: {recommendations['performance_predictions']['estimated_ctr']:.1f}%",
                f"Predicted conversions: {int(recommendations['performance_predictions']['estimated_conversions'] * 100)}",
                f"Estimated reach: {recommendations['performance_predictions']['estimated_reach']:,} people"
            ],
            'generated_at': '2025-09-17T11:28:00Z'  # Add timestamp
        }
        
        return jsonify({
            'success': True,
            'data': formatted_recommendations
        })
        
    except Exception as e:
        print(f"❌ Error in campaign recommendations: {str(e)}")
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

@campaign_bp.route('/campaign/health', methods=['GET'])
def health_check():
    """Health check endpoint for the campaign AI service"""
    try:
        return jsonify({
            'success': True,
            'message': 'Campaign AI service is running',
            'model_status': 'loaded' if ai_service.model.is_trained else 'not_loaded',
            'available_endpoints': [
                '/campaign/recommendations',
                '/platforms',
                '/campaign/health'
            ]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'model_status': 'error'
        }), 500
