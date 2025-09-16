import random
from typing import Dict, List
import datetime

class AIService:
    def generate_recommendations(self, campaign_data: Dict) -> Dict:
        product = campaign_data.get('product_name', '').lower()
        audience = campaign_data.get('target_audience', {})
        budget = campaign_data.get('budget', 1000)
        location = campaign_data.get('location', 'United States')
        
        platform_scores = self._calculate_platform_scores(product, audience)
        recommended_platform = max(platform_scores, key=platform_scores.get)
        
        return {
            'recommended_platform': recommended_platform,
            'platform_scores': platform_scores,
            'budget_allocation': self._calculate_budget_allocation(platform_scores, budget),
            'ad_copy_suggestions': self._generate_ad_copy(product),
            'optimal_timing': {
                'best_days': ['Tuesday', 'Wednesday', 'Thursday'],
                'best_hours': ['9-11 AM', '2-4 PM', '7-9 PM']
            },
            'performance_predictions': {
                'estimated_reach': int((budget / 2.5) * 1000),
                'estimated_ctr': 0.025,
                'estimated_conversions': random.randint(50, 500)
            },
            'confidence_score': round(random.uniform(0.75, 0.95), 2),
            'generated_at': datetime.datetime.now().isoformat()
        }
    
    def _calculate_platform_scores(self, product: str, audience: Dict) -> Dict:
        scores = {'google_ads': 0.5, 'meta_ads': 0.5, 'linkedin_ads': 0.3}
        
        if any(word in product for word in ['tech', 'software', 'b2b']):
            scores['google_ads'] += 0.3
            scores['linkedin_ads'] += 0.4
        
        if any(word in product for word in ['fashion', 'food', 'lifestyle']):
            scores['meta_ads'] += 0.3
        
        max_score = max(scores.values())
        return {k: round(v/max_score, 2) for k, v in scores.items()}
    
    def _calculate_budget_allocation(self, scores: Dict, budget: float) -> Dict:
        total_score = sum(scores.values())
        return {
            platform: {
                'percentage': round((score/total_score) * 100, 1),
                'amount': round((score/total_score) * budget, 2)
            }
            for platform, score in scores.items()
        }
    
    def _generate_ad_copy(self, product: str) -> List[str]:
        return [
            f"Discover the best {product} for your needs!",
            f"Transform your experience with premium {product}",
            f"Limited time: Get {product} with exclusive benefits"
        ]
