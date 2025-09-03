import streamlit as st
import requests
import os
import sys
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
import difflib

# Add the project root to the system path to allow importing from src
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.recommender import Recommender
from src.data_processing import load_and_preprocess_data

# Load environment variables from .env file
load_dotenv()

# Get the TMDB API key from an environment variable
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

# Use st.cache_resource to load the machine learning model only once
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

# Use st.cache_data to load the movie data only once
@st.cache_data
def load_movie_titles():
    """Loads and returns a list of all movie titles from the dataset."""
    try:
        # Load data and get the list of movie titles
        tmdb_movies_df, _ = load_and_preprocess_data()
        if tmdb_movies_df is not None:
            return tmdb_movies_df['title'].sort_values().tolist()
        return []
    except Exception as e:
        st.error(f"Error loading movie data: {e}")
        return []

def fetch_poster(movie_id):
    """Fetches the movie poster from the TMDB API using an environment variable."""
    if not TMDB_API_KEY:
        st.error("TMDB API key not found. Please set the 'TMDB_API_KEY' environment variable.")
        return None

    # Construct the API request URL
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
    try:
        data = requests.get(url)
        data.raise_for_status()  # Raise an exception for bad status codes
        data = data.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500/{poster_path}"
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching poster: {e}")
        return None

# Set the Streamlit page configuration and header
st.set_page_config(layout="centered")
st.header('Movie Recommender System')

# Load the recommender model and movie titles using cached functions
recommender = load_recommender_model()
movie_titles = load_movie_titles()

# Stop the app if model or data files are not found
if recommender is None or not movie_titles:
    st.error("Model or movie data files not found. Please run the notebook to train the model first.")
    st.stop()

# Use a text input field for the user to type a movie title
user_input = st.text_input(
    "Enter a movie title",
    ""
)

# Button to trigger the recommendation process
if st.button('Show Recommendation'):
    if user_input:
        with st.spinner('Generating recommendations...'):
            # Use difflib to find the closest matching movie title from the dataset
            matches = difflib.get_close_matches(user_input, movie_titles, n=1, cutoff=0.6)
            
            if matches:
                selected_movie = matches[0]
                st.info(f"Showing recommendations for: **{selected_movie}**")
                # Get recommendations using the selected movie title
                recommended_movies = recommender.get_recommendations(selected_movie, n=9)
            else:
                st.warning(f"No close match found for '{user_input}'. Please try a different title.")
                recommended_movies = None

        if recommended_movies and not isinstance(recommended_movies, dict):
            st.subheader("Recommended Movies:")
            
            posters = {}
            # Use ThreadPoolExecutor to fetch movie posters in parallel for faster loading
            with ThreadPoolExecutor(max_workers=9) as executor:
                future_to_movie = {executor.submit(fetch_poster, movie['tmdbId']): movie for movie in recommended_movies}
                for future in as_completed(future_to_movie):
                    movie = future_to_movie[future]
                    try:
                        poster_url = future.result()
                        posters[movie['tmdbId']] = poster_url
                    except Exception as exc:
                        st.error(f"Movie {movie.get('title', 'N/A')} generated an exception: {exc}")

            # Create a 3-column grid to display the posters
            cols = st.columns(3)
            for i, movie in enumerate(recommended_movies):
                with cols[i % 3]:
                    poster = posters.get(movie['tmdbId'])
                    if poster:
                        st.image(poster, width='stretch', caption=movie.get('title', ''))
                    else:
                        st.text("No poster available")
        elif recommended_movies is None:
            # The warning message for no match is already shown above, so we pass
            pass
        else:
            st.warning(f"No recommendations found for '{selected_movie}'. Please try a different movie title.")
    else:
        st.warning("Please enter a movie title to get recommendations.")