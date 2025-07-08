import httpx
from typing import List, Dict, Any
import csv
from datetime import datetime, timedelta
from nba_api.stats.endpoints import playergamelog, boxscoretraditionalv2, leaguegamefinder, commonplayerinfo, teamgamelog, teamyearbyyearstats, commonteamroster
from nba_api.stats.static import teams, players
import pandas as pd
import time
import os
import numpy as np

# test data
MOCK_GAMES = [
    {"id": "1", "date": "2024-01-15", "teams": "Lakers vs Warriors"},
    {"id": "2", "date": "2024-01-16", "teams": "Celtics vs Heat"},
    {"id": "3", "date": "2024-01-17", "teams": "Nets vs Knicks"},
]

MOCK_PLAYERS = [
    {"id": "player1", "name": "LeBron James"},
    {"id": "player2", "name": "Stephen Curry"},
    {"id": "player3", "name": "Kevin Durant"},
]
class CriticalTimeoutException(Exception):
    pass

waittime = 5  


async def tester():
    print("Testing NBA API connection...")
    save =  await safe_api_call(playergamelog.PlayerGameLog, player_id='203999', season="2023-24")

    print(save.get_data_frames()[0].head())
    
    
async def playerlist()-> List[Dict[str, Any]]:
    print("Fetching player list...")
    try:
        return players.get_players()
    except Exception as e:
        print(f"NBA API error: {e}. Using mock data.")
        return MOCK_PLAYERS
    
#send api calls safely with retry logic
async def safe_api_call(endpoint_cls, **kwargs):
    print("Making API call to:", endpoint_cls.__name__, "with args:", kwargs)
    global waittime
    while True:
        try:
            time.sleep(waittime)
            save =  endpoint_cls(**kwargs)
            print("success")
            print(kwargs)
            return save
        
        except Exception as e:
            err_str = str(e)
            print("Rate limited or error, sleeping: ", err_str)
            # Check for the specific timeout error
            if "HTTPSConnectionPool(host='stats.nba.com', port=443): Read timed out. (read timeout=30)" in err_str:
                raise CriticalTimeoutException(err_str)
            time.sleep(waittime)
    

async def get_upcoming_games() -> List[Dict[str, Any]]:
    try:
        gamefinder = leaguegamefinder.LeagueGameFinder(
            season_nullable="2023-24",
            league_id_nullable="00"
        )
        games = gamefinder.get_data_frames()[0]
        
        # Remove duplicates by GAME_ID before processing
        unique_games = games.drop_duplicates(subset=['GAME_ID']).head(10)
        
        upcoming_games = []
        for _, game in unique_games.iterrows():
            upcoming_games.append({
                "id": str(game['GAME_ID']),
                "date": game['GAME_DATE'],
                "teams": f"{game['TEAM_NAME']} vs {game['MATCHUP']}"
            })
        
        return upcoming_games
    except Exception as e:
        print(f"NBA API error: {e}. Using mock data.")
        return MOCK_GAMES

async def get_game_details(game_id: str) -> Dict[str, Any]:
    print("ive been hit")
    try:
        boxscore = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=game_id)
        game_data = boxscore.get_data_frames()[0]
        if game_data.empty:
            print("fail")
            return None
        
        game_data = game_data.replace({np.nan: None, np.inf: None, -np.inf: None})

        return game_data.to_dict(orient='records')
    except Exception as e:
        print(f"failure for game {game_id}: {e}")


async def get_players_for_game(game_id: str) -> List[Dict[str, Any]]:
    try:
        # Get players for a specific game
        all_players = players.get_players()
        game_players = []
        
        # For now, return a subset of players
        for i, player in enumerate(all_players[:10]):
            game_players.append({
                "id": str(player['id']),
                "name": player['full_name']
            })
        return game_players
    except Exception as e:
        print(f"NBA API error: {e}. Using mock data.")
        return MOCK_PLAYERS 

def get_nba_teams() -> List[Dict[str, Any]]:
    """
    Returns a list of all NBA teams with their id and name.
    """
    try:
        all_teams = teams.get_teams()
        return [
            {"id": str(team["id"]), "name": f'{team["full_name"]} ({team["abbreviation"]})'}
            for team in all_teams
        ]
    except Exception as e:
        print(f"NBA API error: {e}. Returning empty team list.")
        return [] 