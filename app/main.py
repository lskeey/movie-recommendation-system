from fastapi import FastAPI, HTTPException
from src.recommender import Recommender

app = FastAPI()
recommender = Recommender()

@app.get("/recommend")
async def get_recommendations(title: str):
    """
    Endpoint to get movie recommendations based on a movie title.
    Returns a structured response with status, message, and a list of movie titles.
    """
    if recommender.models is None:
        raise HTTPException(
            status_code=500, 
            detail={"status": "error", "message": "Models are not loaded. Please ensure the model file exists.", "data": []}
        )

    recommendations = recommender.get_recommendations(title)
    
    if not recommendations:
        return {
            "status": "error",
            "message": f"Movie '{title}' not found or no recommendations available.",
            "data": []
        }
    
    return {
        "status": "success",
        "message": "Recommendations found.",
        "data": recommendations
    }