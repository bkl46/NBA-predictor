from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from nba_data import get_upcoming_games, get_players_for_game, tester, playerlist, get_game_details
from model_loader import get_model_for_player
from feature_engineering import build_features
import asyncio
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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

@app.get("/realtest")
async def realtest():
    await tester()
    return await playerlist()

@app.get("/players")
async def players(game_id: str):
    return await get_players_for_game(game_id)

@app.get("/games/{game_id}")
async def game_details(game_id: str):
    game_details = await get_game_details(game_id)
    if not game_details:
        raise HTTPException(status_code=404, detail="Game not found")
    return game_details

@app.post("/predict")
async def predict(request: PredictRequest):
    model = get_model_for_player(request.player_id)
    if model is None:
        raise HTTPException(status_code=404, detail="Model not found for player")
    features = await build_features(request.player_id, request.game_id)
    prediction = model.predict([features])[0]
    return {"prediction": prediction} 