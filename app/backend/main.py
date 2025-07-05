from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from backend.nba_api import get_upcoming_games, get_players_for_game
from backend.model_loader import get_model_for_player
from backend.feature_engineering import build_features
import asyncio

app = FastAPI()

# In-memory cache for games
games_cache = []

class PredictRequest(BaseModel):
    player_id: str
    game_id: str

@app.on_event("startup")
async def startup_event():
    await cache_games()

async def cache_games():
    global games_cache
    games_cache = await get_upcoming_games()

@app.get("/games")
async def games():
    return games_cache

@app.get("/players")
async def players(game_id: str):
    return await get_players_for_game(game_id)

@app.post("/predict")
async def predict(request: PredictRequest):
    model = get_model_for_player(request.player_id)
    if model is None:
        raise HTTPException(status_code=404, detail="Model not found for player")
    features = await build_features(request.player_id, request.game_id)
    prediction = model.predict([features])[0]
    return {"prediction": prediction} 