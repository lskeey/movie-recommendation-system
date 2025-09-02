import pandas as pd
from ast import literal_eval
import warnings

def load_and_preprocess_data():
    """
    Loads movie and ratings datasets, merges them, and preprocesses data.
    Returns the processed movie dataframe and the filtered ratings dataframe.
    """
    warnings.filterwarnings('ignore')

    # Load datasets
    try:
        tmdb_movies_df = pd.read_csv('data/raw/tmdb_5000_movie_dataset/tmdb_5000_movies.csv')
        tmdb_credits_df = pd.read_csv('data/raw/tmdb_5000_movie_dataset/tmdb_5000_credits.csv')
        ratings_df = pd.read_csv('data/raw/the_movie_dataset/ratings.csv')
        links_df = pd.read_csv('data/raw/the_movie_dataset/links.csv')
    except FileNotFoundError:
        print("Please ensure the datasets are in the correct directory.")
        return None, None

    # Merge movie data
    tmdb_credits_df.columns = ['id', 'title', 'cast', 'crew']
    tmdb_movies_df = tmdb_movies_df.merge(tmdb_credits_df, on='id')
    tmdb_movies_df = tmdb_movies_df.rename(columns={'id': 'tmdbId'})

    # Link ratings with TMDB IDs and filter
    ratings_with_tmdb_id_df = ratings_df.merge(links_df, on='movieId', how='inner')
    ratings_with_tmdb_id_df = ratings_with_tmdb_id_df.dropna(subset=['tmdbId']).astype({'tmdbId': 'int'})

    # Filter users and movies with insufficient ratings
    min_user_ratings = 50
    filtered_users = ratings_with_tmdb_id_df['userId'].value_counts()
    filtered_users = filtered_users[filtered_users >= min_user_ratings].index
    final_dataset = ratings_with_tmdb_id_df[ratings_with_tmdb_id_df['userId'].isin(filtered_users)]

    min_movie_ratings = 100
    filtered_movies = final_dataset['tmdbId'].value_counts()
    filtered_movies = filtered_movies[filtered_movies >= min_movie_ratings].index
    final_dataset = final_dataset[final_dataset['tmdbId'].isin(filtered_movies)]
    
    return tmdb_movies_df, final_dataset

def get_director(crew_list):
    """Extract director name from crew list."""
    for person in crew_list:
        if person['job'] == 'Director':
            return person['name']
    return None

def get_list(feature_list):
    """Extract top 3 names from feature list."""
    if isinstance(feature_list, list):
        names = [item['name'] for item in feature_list]
        return names[:3] if len(names) > 3 else names
    return []

def clean_data(data):
    """Clean and normalize text data."""
    if isinstance(data, list):
        return [str.lower(item.replace(' ', '')) for item in data]
    elif isinstance(data, str):
        return str.lower(data.replace(' ', ''))
    else:
        return ''

def create_feature_soup(df):
    """Combine all features into a single text string."""
    features = ['cast', 'crew', 'keywords', 'genres']
    for feature in features:
        df[feature] = df[feature].apply(literal_eval)
    
    df['director'] = df['crew'].apply(get_director)
    
    features_to_process = ['cast', 'keywords', 'genres', 'director']
    for feature in ['cast', 'keywords', 'genres']:
        df[feature] = df[feature].apply(get_list)
        
    for feature in features_to_process:
        df[feature] = df[feature].apply(clean_data)
        
    df['soup'] = df.apply(
        lambda row: ' '.join(row['keywords']) + ' ' +
                    ' '.join(row['cast']) + ' ' +
                    row['director'] + ' ' +
                    ' '.join(row['genres']),
        axis=1
    )
    return df