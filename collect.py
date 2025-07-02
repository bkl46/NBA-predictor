import csv
from datetime import datetime, timedelta
from nba_api.stats.endpoints import playergamelog, boxscoretraditionalv2, leaguegamefinder, commonplayerinfo, teamgamelog, teamyearbyyearstats, commonteamroster
from nba_api.stats.static import teams, players
import pandas as pd
import time

calls = 0
waittime = 3

class CriticalTimeoutException(Exception):
    pass

# Helper to handle rate limits
def safe_api_call(endpoint_cls, **kwargs):
    print("Making API call to:", endpoint_cls.__name__, "with args:", kwargs)
    global calls
    global waittime
    while True:
        try:
            time.sleep(waittime)
            save =  endpoint_cls(**kwargs)
            print("success")
            print(calls)
            calls+=1
            print(kwargs)
            return save
        
        except Exception as e:
            err_str = str(e)
            print("Rate limited or error, sleeping: ", err_str)
            # Check for the specific timeout error
            if "HTTPSConnectionPool(host='stats.nba.com', port=443): Read timed out. (read timeout=30)" in err_str:
                raise CriticalTimeoutException(err_str)
            time.sleep(waittime)

# Helper functions
def get_player_season_avg(player_id, season):
    log = safe_api_call(playergamelog.PlayerGameLog, player_id=player_id, season=season).get_data_frames()[0]
    if log.empty:
        return {}
    return log.mean(numeric_only=True).to_dict()

def get_recent_games_avg(player_id, season, date):
    log = safe_api_call(playergamelog.PlayerGameLog, player_id=player_id, season=season).get_data_frames()[0]
    log["GAME_DATE"] = pd.to_datetime(log["GAME_DATE"])
    log = log[log["GAME_DATE"] < pd.to_datetime(date)].sort_values("GAME_DATE", ascending=False)
    if log.empty:
        return {}
    return log.head(2).mean(numeric_only=True).to_dict()

def get_recent_vs_team_avg(player_id, season, date, opponent_team_id):
    log = safe_api_call(playergamelog.PlayerGameLog, player_id=player_id, season=season).get_data_frames()[0]
    log["GAME_DATE"] = pd.to_datetime(log["GAME_DATE"])
    log = log[log["GAME_DATE"] < pd.to_datetime(date)]
    log = log[log["MATCHUP"].str.contains(get_team_abbreviation(opponent_team_id))]
    if log.empty:
        return {}
    return log.sort_values("GAME_DATE", ascending=False).head(2).mean(numeric_only=True).to_dict()

def get_team_abbreviation(team_id):
    for team in teams.get_teams():
        if team['id'] == team_id:
            return team['abbreviation']
    return ""

def get_team_stats(team_id, date, season):
    log = safe_api_call(teamgamelog.TeamGameLog, team_id=team_id, season=season).get_data_frames()[0]
    log["GAME_DATE"] = pd.to_datetime(log["GAME_DATE"])
    past_games = log[log["GAME_DATE"] < pd.to_datetime(date)]
    if past_games.empty:
        return {"W_PCT": None, "GP": 0}
    gp = len(past_games)
    w_pct = past_games["WL"].value_counts(normalize=True).get("W", 0)
    stats = past_games.mean(numeric_only=True).to_dict()
    stats.update({"GP": gp, "W_PCT": w_pct})
    return stats

def get_game_data(season, start_date, end_date, output_csv):
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    games_df = safe_api_call(leaguegamefinder.LeagueGameFinder, season_nullable=season).get_data_frames()[0]
    games_df["GAME_DATE"] = pd.to_datetime(games_df["GAME_DATE"])
    games_df = games_df[(games_df["GAME_DATE"] >= start_dt) & (games_df["GAME_DATE"] <= end_dt)]
    games_df =games_df.head(1)
    print(len(games_df), "games found between", start_date, "and", end_date)

    all_fieldnames = set()
    row_data_list = []
    try:
        for gidx, game in games_df.iterrows():
            game_id = game['GAME_ID']
            game_date = game['GAME_DATE']
            boxscore = safe_api_call(boxscoretraditionalv2.BoxScoreTraditionalV2, game_id=game_id).get_data_frames()[0]
            for pidx, player_row in boxscore.iterrows():
                print(f"player{pidx} of game{gidx}")
                if player_row['MIN'] == '0':
                    continue
                player_name = player_row['PLAYER_NAME']
                player = players.find_players_by_full_name(player_name)
                if not player:
                    continue
                player_id = player[0]['id']
                team_id = player_row['TEAM_ID']
                opp_ids = [tid for tid in boxscore['TEAM_ID'].unique() if tid != team_id]
                opp_team_id = opp_ids[0] if opp_ids else None

                season_avg = get_player_season_avg(player_id, season)
                recent_avg = get_recent_games_avg(player_id, season, game_date)
                recent_vs_team_avg = get_recent_vs_team_avg(player_id, season, game_date, opp_team_id)
                team_stats = get_team_stats(team_id, game_date, season)
                opp_stats = get_team_stats(opp_team_id, game_date, season)

                row_data = {
                    **player_row.to_dict(),
                    **{f"SEASON_{k}": v for k, v in season_avg.items()},
                    **{f"RECENT_{k}": v for k, v in recent_avg.items()},
                    **{f"VS_TEAM_{k}": v for k, v in recent_vs_team_avg.items()},
                    **{f"TEAM_{k}": v for k, v in team_stats.items()},
                    **{f"OPP_{k}": v for k, v in opp_stats.items()}
                }
                all_fieldnames.update(row_data.keys())
                row_data_list.append(row_data)
    except CriticalTimeoutException as e:
        print("Critical timeout encountered. Saving collected data and exiting:", e)
    finally:
        # Write to CSV with all fieldnames
        with open(output_csv, mode='w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=list(all_fieldnames))
            writer.writeheader()
            for row_data in row_data_list:
                writer.writerow(row_data)

# Example usage:
get_game_data("2023-24", "2024-01-04", "2024-01-04", "nba_games_output.csv")
