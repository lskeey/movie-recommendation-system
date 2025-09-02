import pandas as pd
from .content_based_filtering import get_content_recommendations
from .collaborative_filtering import get_collaborative_recommendations

def hybrid_recommender(movie_title, n, w_content, w_collaborative, models):
    """
    Hybrid recommender combining content and collaborative filtering with weighted scores.
    
    Args:
        movie_title: Target movie title
        n: Number of recommendations
        w_content: Weight for content-based recommendations (0-1)
        w_collaborative: Weight for collaborative recommendations (0-1)
        models: Dictionary containing all necessary models and dataframes
        
    Returns:
        List of recommended movie titles sorted by hybrid score
    """
    # Extract models and data
    content_cosine_sim = models['content_cosine_sim']
    indices = models['indices']
    tmdb_movies_df = models['tmdb_movies_df']
    model_knn = models['model_knn']
    movie_to_user_df = models['movie_to_user_df']

    # Get content-based recommendations
    content_recs = get_content_recommendations(movie_title, tmdb_movies_df, content_cosine_sim, indices)

    # Get collaborative recommendations
    if movie_title not in tmdb_movies_df['title_x'].values:
        return []
    
    movie_id = tmdb_movies_df[tmdb_movies_df['title_x'] == movie_title]['tmdbId'].values[0]
    collaborative_recs = get_collaborative_recommendations(movie_id, tmdb_movies_df, model_knn, movie_to_user_df)

    # Calculate hybrid scores
    hybrid_scores = {}

    # Add content-based scores
    for title in content_recs:
        if title not in hybrid_scores:
            hybrid_scores[title] = w_content * 1.0

    # Add collaborative scores
    for title in collaborative_recs['title_x']:
        if title in hybrid_scores:
            hybrid_scores[title] += w_collaborative * 1.0
        else:
            hybrid_scores[title] = w_collaborative * 1.0

    # Sort by hybrid score
    sorted_recs = sorted(hybrid_scores.items(), key=lambda x: x[1], reverse=True)

    return [title for title, score in sorted_recs][:n]