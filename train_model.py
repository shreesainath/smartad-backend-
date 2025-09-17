import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, mean_squared_error
import joblib
import json

class SmartAdMLModel:
    def __init__(self):
        self.platform_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.score_regressor = RandomForestRegressor(n_estimators=100, random_state=42)
        self.ctr_regressor = RandomForestRegressor(n_estimators=100, random_state=42)
        self.conversion_regressor = RandomForestRegressor(n_estimators=100, random_state=42)
        
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def prepare_features(self, df):
        """Prepare features for training"""
        features = []
        
        # Encode categorical variables
        categorical_columns = ['location', 'age_group', 'objectives']
        for col in categorical_columns:
            if col not in self.label_encoders:
                self.label_encoders[col] = LabelEncoder()
                df[f'{col}_encoded'] = self.label_encoders[col].fit_transform(df[col])
            else:
                df[f'{col}_encoded'] = self.label_encoders[col].transform(df[col])
            features.append(f'{col}_encoded')
        
        # Budget (numerical)
        features.append('budget')
        
        # Interest count
        df['interest_count'] = df['interests'].str.count(';') + 1
        features.append('interest_count')
        
        # Interest categories
        common_interests = ['technology', 'business', 'fitness', 'lifestyle', 'health', 'fashion', 'education']
        for interest in common_interests:
            df[f'has_{interest}'] = df['interests'].str.contains(interest, case=False).astype(int)
            features.append(f'has_{interest}')
        
        return df[features]
    
    def train(self, csv_file_path):
        """Train the model with CSV data"""
        print("Loading and preparing data...")
        df = pd.read_csv(csv_file_path)
        
        # Prepare features
        X = self.prepare_features(df.copy())
        
        # Prepare targets
        y_platform = df['recommended_platform']
        y_score = df['platform_score']
        y_ctr = df['ctr_prediction']
        y_conversion = df['conversion_prediction']
        
        # Encode platform labels
        self.platform_encoder = LabelEncoder()
        y_platform_encoded = self.platform_encoder.fit_transform(y_platform)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Split data
        X_train, X_test, y_platform_train, y_platform_test, y_score_train, y_score_test, y_ctr_train, y_ctr_test, y_conv_train, y_conv_test = train_test_split(
            X_scaled, y_platform_encoded, y_score, y_ctr, y_conversion, test_size=0.2, random_state=42
        )
        
        print("Training models...")
        
        # Train models
        self.platform_classifier.fit(X_train, y_platform_train)
        self.score_regressor.fit(X_train, y_score_train)
        self.ctr_regressor.fit(X_train, y_ctr_train)
        self.conversion_regressor.fit(X_train, y_conv_train)
        
        # Evaluate models
        platform_acc = accuracy_score(y_platform_test, self.platform_classifier.predict(X_test))
        score_mse = mean_squared_error(y_score_test, self.score_regressor.predict(X_test))
        ctr_mse = mean_squared_error(y_ctr_test, self.ctr_regressor.predict(X_test))
        conv_mse = mean_squared_error(y_conv_test, self.conversion_regressor.predict(X_test))
        
        print(f"Platform Classification Accuracy: {platform_acc:.3f}")
        print(f"Score Prediction MSE: {score_mse:.6f}")
        print(f"CTR Prediction MSE: {ctr_mse:.6f}")
        print(f"Conversion Prediction MSE: {conv_mse:.6f}")
        
        self.is_trained = True
        print("Training completed!")
        
    def predict(self, campaign_data):
        """Make predictions for a campaign"""
        if not self.is_trained:
            raise ValueError("Model must be trained first!")
        
        # Convert single campaign to DataFrame
        df = pd.DataFrame([campaign_data])
        
        # Prepare features
        X = self.prepare_features(df)
        X_scaled = self.scaler.transform(X)
        
        # Make predictions
        platform_pred = self.platform_classifier.predict(X_scaled)[0]
        platform_name = self.platform_encoder.inverse_transform([platform_pred])[0]
        
        score_pred = self.score_regressor.predict(X_scaled)[0]
        ctr_pred = self.ctr_regressor.predict(X_scaled)[0]
        conversion_pred = self.conversion_regressor.predict(X_scaled)[0]
        
        # Generate budget allocation
        budget_allocation = self._generate_budget_allocation(
            platform_name, campaign_data['objectives'], campaign_data['budget']
        )
        
        return {
            'recommended_platform': platform_name,
            'platform_score': float(score_pred),
            'budget_allocation': budget_allocation,
            'ctr_prediction': float(ctr_pred),
            'conversion_prediction': float(conversion_pred),
            'confidence_score': float(min(score_pred + 0.05, 0.95))
        }
    
    def _generate_budget_allocation(self, platform, objective, total_budget):
        """Generate budget allocation based on platform and objective"""
        allocations = {
            'Facebook': {'awareness': 0.4, 'engagement': 0.45, 'traffic': 0.3, 'leads': 0.2, 'conversions': 0.25},
            'Google': {'awareness': 0.3, 'engagement': 0.25, 'traffic': 0.5, 'leads': 0.4, 'conversions': 0.35},
            'Instagram': {'awareness': 0.2, 'engagement': 0.2, 'traffic': 0.25, 'leads': 0.15, 'conversions': 0.35},
            'LinkedIn': {'awareness': 0.05, 'engagement': 0.05, 'traffic': 0.1, 'leads': 0.4, 'conversions': 0.1},
            'Twitter': {'awareness': 0.05, 'engagement': 0.05, 'traffic': 0.05, 'leads': 0.05, 'conversions': 0.05}
        }
        
        base_allocation = allocations['Facebook']
        if platform in allocations:
            base_allocation = allocations[platform]
        
        return {
            'Facebook': base_allocation.get(objective, 0.25) * total_budget,
            'Google': allocations['Google'].get(objective, 0.3) * total_budget,
            'Instagram': allocations['Instagram'].get(objective, 0.2) * total_budget,
            'LinkedIn': allocations['LinkedIn'].get(objective, 0.15) * total_budget,
            'Twitter': allocations['Twitter'].get(objective, 0.1) * total_budget
        }
    
    def save_model(self, model_path='smartad_model.pkl'):
        """Save the trained model"""
        model_data = {
            'platform_classifier': self.platform_classifier,
            'score_regressor': self.score_regressor,
            'ctr_regressor': self.ctr_regressor,
            'conversion_regressor': self.conversion_regressor,
            'label_encoders': self.label_encoders,
            'platform_encoder': self.platform_encoder,
            'scaler': self.scaler,
            'is_trained': self.is_trained
        }
        joblib.dump(model_data, model_path)
        print(f"Model saved to {model_path}")
    
    def load_model(self, model_path='smartad_model.pkl'):
        """Load a trained model"""
        model_data = joblib.load(model_path)
        
        self.platform_classifier = model_data['platform_classifier']
        self.score_regressor = model_data['score_regressor']
        self.ctr_regressor = model_data['ctr_regressor']
        self.conversion_regressor = model_data['conversion_regressor']
        self.label_encoders = model_data['label_encoders']
        self.platform_encoder = model_data['platform_encoder']
        self.scaler = model_data['scaler']
        self.is_trained = model_data['is_trained']
        
        print(f"Model loaded from {model_path}")

if __name__ == "__main__":
    # Train the model
    model = SmartAdMLModel()
    model.train('campaign_data.csv')
    model.save_model()
    
    # Test prediction
    test_campaign = {
        'product_name': 'Smart Watch',
        'budget': 2000,
        'location': 'chennai',
        'age_group': '25-34',
        'interests': 'technology;fitness;health',
        'objectives': 'conversions'
    }
    
    prediction = model.predict(test_campaign)
    print("\nTest Prediction:")
    print(json.dumps(prediction, indent=2))
