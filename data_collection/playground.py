
import collection
import csv
from datetime import datetime, timedelta
from nba_api.stats.endpoints import playergamelog, boxscoretraditionalv2, leaguegamefinder, commonplayerinfo, teamgamelog, teamyearbyyearstats, commonteamroster
from nba_api.stats.static import teams, players
import pandas as pd
import time


save = collection.safe_api_call(playergamelog.PlayerGameLog, player_id='203999', season="2023-24")

print(save.get_data_frames()[0].head())