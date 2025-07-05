import joblib
import os
from typing import Dict

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
model_cache: Dict[str, any] = {}

def get_model_for_player(player_id: str):
    if player_id in model_cache:
        return model_cache[player_id]
    model_path = os.path.join(MODEL_DIR, f"{player_id}.joblib")
    if not os.path.exists(model_path):
        return None
    model = joblib.load(model_path)
    model_cache[player_id] = model
    return model 