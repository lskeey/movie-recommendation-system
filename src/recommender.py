import pickle
import os

class Recommender:
    def __init__(self, model_path='models/recommender_models.pkl'):
        self.models = self.load_models(model_path)
    
    def load_models(self, file_path):
        """Loads models and data from a pickle file."""
        if not os.path.exists(file_path):
            print(f"Error: Model file not found at {file_path}. Please train the model first.")
            return None
        with open(file_path, 'rb') as file:
            models = pickle.load(file)
        return models

    def get_recommendations(self, movie_title, n=15, w_content=0.5, w_collaborative=0.5):
        """
        Gets movie recommendations using the hybrid model.
        """
        if self.models is None:
            return {"error": "Recommender models not loaded."}

        from .models.hybrid_model import hybrid_recommender
        
        recommendations = hybrid_recommender(
            movie_title,
            n=n,
            w_content=w_content,
            w_collaborative=w_collaborative,
            models=self.models
        )
        return recommendations