import httpx
from typing import List, Dict, Any

NBA_API_HOST = "api-nba-v1.p.rapidapi.com"
NBA_API_KEY = "YOUR_RAPIDAPI_KEY"  # Replace with your actual key or load from env
HEADERS = {
    "X-RapidAPI-Host": NBA_API_HOST,
    "X-RapidAPI-Key": NBA_API_KEY,
}
BASE_URL = f"https://{NBA_API_HOST}"

async def get_upcoming_games() -> List[Dict[str, Any]]:
    url = f"{BASE_URL}/games"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=HEADERS, params={"season": "2023"})
        response.raise_for_status()
        data = response.json()
        # Parse and return relevant game info
        return data.get("response", [])

async def get_players_for_game(game_id: str) -> List[Dict[str, Any]]:
    url = f"{BASE_URL}/players"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=HEADERS, params={"game": game_id})
        response.raise_for_status()
        data = response.json()
        # Parse and return relevant player info
        return data.get("response", []) 