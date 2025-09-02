from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
import pandas as pd

def train_collaborative_model(final_dataset):
    """
    Trains the collaborative filtering model using a KNN algorithm.
    """
    movie_to_user_df = final_dataset.pivot_table(index='tmdbId', columns='userId', values='rating').fillna(0)
    movie_to_user_sparse_matrix = csr_matrix(movie_to_user_df.values)
    
    model_knn = NearestNeighbors(metric='cosine', algorithm='brute')
    model_knn.fit(movie_to_user_sparse_matrix)
    
    return model_knn, movie_to_user_df

def get_collaborative_recommendations(movie_id, df, model_knn, movie_to_user_df):
    """
    Generates collaborative filtering recommendations for a given movie ID.
    """
    if movie_id not in movie_to_user_df.index:
        return pd.DataFrame({'title_x': []})

    distances, indices = model_knn.kneighbors(
        movie_to_user_df.loc[movie_id].values.reshape(1, -1), 
        n_neighbors=11
    )
    
    similar_movies = [movie_to_user_df.index[i] for i in indices.flatten()[1:]]
    return df[df['tmdbId'].isin(similar_movies)][['title_x']]