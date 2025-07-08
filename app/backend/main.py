from fastapi import FastAPI, BackgroundTasks, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Any
from nba_data import get_upcoming_games, get_players_for_game, tester, playerlist, get_game_details, get_nba_teams
from model_loader import get_model_for_player
from feature_engineering import build_features
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from nba_api.stats.static import players as nba_players
from nba_api.stats.endpoints import commonplayerinfo, playercareerstats
from player_call import get_player_input_data
import joblib
import os
import numpy as np

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

MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "nba_xgb_multioutput_model1.joblib")
model = None

def get_global_model():
    global model
    if model is None:
        model = joblib.load(MODEL_PATH)
    return model

class PredictRequest(BaseModel):
    player_id: str
    season: str
    date: str
    opponent_team_id: str
    player_team_id: str

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
    # Always use the global multioutput model
    model = get_global_model()
    # Build input using player_call.py
    input_data = get_player_input_data(
        request.player_id,
        request.season,
        request.opponent_team_id,
        request.date,
        request.player_team_id
    )
    if input_data is None:
        raise HTTPException(status_code=400, detail="Failed to build input data for prediction")
    import pandas as pd
    feature_columns = [
        # Season averages
        'SEASON_PTS', 'SEASON_REB', 'SEASON_AST', 'SEASON_FGM', 'SEASON_FGA',
        # Recent performance 
        'RECENT_PTS', 'RECENT_REB', 'RECENT_AST', 'RECENT_FGM', 'RECENT_FGA',
        # Matchup data
        'VS_TEAM_PTS', 'VS_TEAM_REB', 'VS_TEAM_AST',
        # Team data
        'TEAM_W_PCT', 'TEAM_GP', 'OPP_W_PCT', 'OPP_GP'
    ]
    # Only keep the required features, fill missing with 0
    features = {col: input_data.get(col, 0) for col in feature_columns}
    input_df = pd.DataFrame([features], columns=feature_columns)
    prediction = model.predict(input_df)[0]
    # Ensure prediction is JSON serializable
    def to_python_type(val):
        if isinstance(val, np.generic):
            return val.item()
        elif isinstance(val, np.ndarray):
            return val.tolist()
        return val
    prediction = to_python_type(prediction)
    return {"prediction": prediction}

@app.get("/players/all")
async def all_players(
    search: str = Query("", description="Search term for player name"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(30, ge=1, le=100, description="Results per page")
):
    """
    Returns a paginated, searchable list of all active NBA players.
    """
    all_players = await playerlist()
    # Filter by search term (case-insensitive substring match on full_name)
    if search:
        all_players = [p for p in all_players if search.lower() in p.get('full_name', p.get('name', '')).lower()]
    total = len(all_players)
    start = (page - 1) * limit
    end = start + limit
    paginated = all_players[start:end]
    # Standardize output fields
    players_out = [
        {
            "PLAYER_ID": p.get("id", p.get("person_id")),
            "PLAYER_NAME": p.get("full_name", p.get("name")),
            "IS_ACTIVE": p.get("is_active", True)
        }
        for p in paginated
    ]
    return {"players": players_out, "page": page, "total": total, "totalPages": (total + limit - 1) // limit}

@app.get("/players/{player_id}")
async def player_details(player_id: str):
    """
    Returns player info, team, season stats, and upcoming games for a given player.
    """
    # Get player info
    info = commonplayerinfo.CommonPlayerInfo(player_id=player_id)
    info_df = info.get_data_frames()[0]
    if info_df.empty:
        raise HTTPException(status_code=404, detail="Player not found")
    player_info = info_df.iloc[0].to_dict()
    # Get season stats
    stats = playercareerstats.PlayerCareerStats(player_id=player_id)
    stats_df = stats.get_data_frames()[0]
    season_stats = stats_df.to_dict(orient="records")
    # Get upcoming games (stub: you may want to implement real logic)
    # For now, return empty or mock
    upcoming_games = []
    return {
        "player_info": player_info,
        "season_stats": season_stats,
        "upcoming_games": upcoming_games
    }

@app.get("/teams")
def teams():
    """
    Returns a list of all NBA teams with their id and name.
    """
    return get_nba_teams() 