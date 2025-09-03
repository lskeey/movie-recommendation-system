import streamlit as st
import requests
import os
import sys
from dotenv import load_dotenv

# Add the project root to the system path to allow importing from src
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.recommender import Recommender

load_dotenv()

# Get the TMDB API key from an environment variable
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

# Use st.cache_resource to load the model only once
@st.cache_resource
def load_recommender_model():
    """Initializes and loads the recommender model, caching it for performance."""
    try:
        recommender = Recommender(model_path='models/recommender_models.pkl')
        if recommender.models is None:
            return None
        return recommender
    except Exception as e:
        st.error(f"Error loading recommender models: {e}")
        return None

def fetch_poster(movie_id):
    """Fetches the movie poster from the TMDB API using an environment variable."""
    if not TMDB_API_KEY:
        st.error("TMDB API key not found. Please set the 'TMDB_API_KEY' environment variable.")
        return None

    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
    try:
        data = requests.get(url)
        data.raise_for_status() # Raise an exception for bad status codes
        data = data.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500/{poster_path}"
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching poster: {e}")
        return None

st.header('Movie Recommender System')

# Load the recommender model using the cached function
recommender = load_recommender_model()

if recommender is None:
    st.error("Model files not found. Please run the notebook to train the model first.")
    st.stop()

selected_movie = st.text_input(
    "Enter a movie title",
    ""
)

if st.button('Show Recommendation'):
    if selected_movie:
        with st.spinner('Generating recommendations...'):
            recommended_movies = recommender.get_recommendations(selected_movie, n=9)

        if recommended_movies:
            st.subheader("Recommended Movies:")
            
            # Create a 3-column grid
            cols = st.columns(3)
            for i, movie in enumerate(recommended_movies):
                with cols[i % 3]: # Use modulo to cycle through columns
                    poster = fetch_poster(movie['tmdbId'])
                    if poster:
                        st.image(poster)
                    else:
                        st.text("No poster available")
            
        else:
            st.warning(f"No recommendations found for '{selected_movie}'. Please try a different movie title.")
    else:
        st.warning("Please enter a movie title to get recommendations.")