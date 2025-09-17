import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from train_model import SmartAdMLModel
import json

class AIRecommendationService:
    def __init__(self):
        self.model = SmartAdMLModel()
        self.load_model()
    
    def load_model(self):
        """Load the trained ML model"""
        try:
            model_path = os.path.join(os.path.dirname(__file__), '..', '..', 'smartad_model.pkl')
            self.model.load_model(model_path)
            print("✅ ML Model loaded successfully")
        except FileNotFoundError:
            print("❌ Model file not found. Please train the model first.")
            print("Run: python train_model.py")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
    
    def get_recommendations(self, campaign_data):
        """Get AI recommendations using trained ML model"""
        try:
            # Prepare data for ML model
            ml_input = {
                'product_name': campaign_data.get('product_name', ''),
                'budget': campaign_data.get('budget', 1000),
                'location': campaign_data.get('location', 'United States'),
                'age_group': campaign_data.get('target_audience', {}).get('age_group', '25-34'),
                'interests': ';'.join(campaign_data.get('target_audience', {}).get('interests', [])),
                'objectives': campaign_data.get('objectives', ['awareness'])[0]
            }
            
            # Get ML predictions
            prediction = self.model.predict(ml_input)
            
            # Format response
            return {
                'recommended_platform': prediction['recommended_platform'],
                'platform_scores': {
                    'Facebook': 0.85 if prediction['recommended_platform'] == 'Facebook' else 0.72,
                    'Google': 0.89 if prediction['recommended_platform'] == 'Google' else 0.78,
                    'Instagram': 0.82 if prediction['recommended_platform'] == 'Instagram' else 0.68,
                    'LinkedIn': 0.91 if prediction['recommended_platform'] == 'LinkedIn' else 0.65,
                    'Twitter': 0.75 if prediction['recommended_platform'] == 'Twitter' else 0.60
                },
                'budget_allocation': prediction['budget_allocation'],
                'ad_copy_suggestions': self._generate_ad_copy(campaign_data),
                'optimal_timing': self._generate_timing_suggestions(),
                'performance_predictions': {
                    'estimated_ctr': prediction['ctr_prediction'],
                    'estimated_conversions': prediction['conversion_prediction'],
                    'estimated_reach': int(campaign_data.get('budget', 1000) * 15),
                    'estimated_impressions': int(campaign_data.get('budget', 1000) * 50)
                },
                'confidence_score': prediction['confidence_score']
            }
            
        except Exception as e:
            print(f"Error in AI recommendations: {e}")
            # Fallback to rule-based system
            return self._fallback_recommendations(campaign_data)
    
    def _generate_ad_copy(self, campaign_data):
        """Generate ad copy suggestions"""
        product = campaign_data.get('product_name', 'Product')
        objective = campaign_data.get('objectives', ['awareness'])[0]
        
        templates = {
            'awareness': [
                f"Discover the amazing {product} - Now Available!",
                f"Introducing {product} - Revolutionary Innovation",
                f"Don't Miss Out on {product} - Limited Time"
            ],
            'traffic': [
                f"Visit Our Website to Learn More About {product}",
                f"Click Here to Explore {product} Features",
                f"Get Details About {product} - Click Now"
            ],
            'leads': [
                f"Get Your Free {product} Demo Today",
                f"Sign Up for {product} - Free Trial Available",
                f"Request Information About {product}"
            ],
            'conversions': [
                f"Buy {product} Now - Special Discount Available",
                f"Order {product} Today - Fast Shipping",
                f"Get {product} - 30% Off This Week"
            ]
        }
        
        return templates.get(objective, templates['awareness'])
    
    def _generate_timing_suggestions(self):
        """Generate optimal timing suggestions"""
        return {
            'best_days': ['Tuesday', 'Wednesday', 'Thursday'],
            'best_hours': ['9:00 AM', '1:00 PM', '7:00 PM'],
            'timezone': 'Target audience timezone',
            'frequency': 'Show ads 3-4 times per day per user'
        }
    
    def _fallback_recommendations(self, campaign_data):
        """Fallback recommendations when ML model fails"""
        return {
            'recommended_platform': 'Facebook',
            'platform_scores': {
                'Facebook': 0.85,
                'Google': 0.82,
                'Instagram': 0.78,
                'LinkedIn': 0.75,
                'Twitter': 0.70
            },
            'budget_allocation': {
                'Facebook': campaign_data.get('budget', 1000) * 0.4,
                'Google': campaign_data.get('budget', 1000) * 0.3,
                'Instagram': campaign_data.get('budget', 1000) * 0.2,
                'LinkedIn': campaign_data.get('budget', 1000) * 0.05,
                'Twitter': campaign_data.get('budget', 1000) * 0.05
            },
            'ad_copy_suggestions': self._generate_ad_copy(campaign_data),
            'optimal_timing': self._generate_timing_suggestions(),
            'performance_predictions': {
                'estimated_ctr': 0.035,
                'estimated_conversions': 0.085,
                'estimated_reach': campaign_data.get('budget', 1000) * 15,
                'estimated_impressions': campaign_data.get('budget', 1000) * 50
            },
            'confidence_score': 0.78
        }

# Create global instance
ai_service = AIRecommendationService()
