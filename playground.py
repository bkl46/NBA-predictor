import collect
import csv
from datetime import datetime, timedelta
from nba_api.stats.endpoints import playergamelog, boxscoretraditionalv2, leaguegamefinder, commonplayerinfo, teamgamelog, teamyearbyyearstats, commonteamroster
from nba_api.stats.static import teams, players
import pandas as pd
import time


games_df = collect.safe_api_call(leaguegamefinder.LeagueGameFinder, season_nullable="2023-24").get_data_frames()[0].head(1)
print(games_df)
boxscore = collect.safe_api_call(boxscoretraditionalv2.BoxScoreTraditionalV2, game_id=games_df["GAME_ID"]).get_data_frames()[0]

print(boxscore.head(1))