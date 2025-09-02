from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

def train_content_model(df):
    """
    Trains the content-based model by vectorizing features and calculating
    the cosine similarity matrix.
    """
    count = CountVectorizer(stop_words='english')
    count_matrix = count.fit_transform(df['soup'])
    content_cosine_sim = cosine_similarity(count_matrix, count_matrix)
    
    df = df.reset_index()
    indices = pd.Series(df.index, index=df['title_x'])
    
    return content_cosine_sim, indices

def get_content_recommendations(title, df, cosine_sim, indices):
    """
    Generates content-based recommendations for a given movie title.
    """
    if title not in indices:
        return pd.Series([])

    idx = indices[title]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:11]
    movie_indices = [i[0] for i in sim_scores]
    
    return df['title_x'].iloc[movie_indices]