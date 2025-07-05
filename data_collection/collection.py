import csv
from datetime import datetime, timedelta
from nba_api.stats.endpoints import playergamelog, boxscoretraditionalv2, leaguegamefinder, commonplayerinfo, teamgamelog, teamyearbyyearstats, commonteamroster
from nba_api.stats.static import teams, players
import pandas as pd
import time
import os

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
    try:
        log = safe_api_call(playergamelog.PlayerGameLog, player_id=player_id, season=season).get_data_frames()[0]
        if log.empty:
            return {}
        return log.mean(numeric_only=True).to_dict()
    except:
        return {}

def get_recent_games_avg(player_id, season, date):
    try:
        log = safe_api_call(playergamelog.PlayerGameLog, player_id=player_id, season=season).get_data_frames()[0]
        log["GAME_DATE"] = pd.to_datetime(log["GAME_DATE"])
        log = log[log["GAME_DATE"] < pd.to_datetime(date)].sort_values("GAME_DATE", ascending=False)
        if log.empty:
            return {}
        return log.head(2).mean(numeric_only=True).to_dict()
    except:
        return {}

def get_recent_vs_team_avg(player_id, season, date, opponent_team_id):
    try:
        log = safe_api_call(playergamelog.PlayerGameLog, player_id=player_id, season=season).get_data_frames()[0]
        log["GAME_DATE"] = pd.to_datetime(log["GAME_DATE"])
        log = log[log["GAME_DATE"] < pd.to_datetime(date)]
        log = log[log["MATCHUP"].str.contains(get_team_abbreviation(opponent_team_id))]
        if log.empty:
            return {}
        return log.sort_values("GAME_DATE", ascending=False).head(2).mean(numeric_only=True).to_dict()
    except:
        return {}

def get_team_abbreviation(team_id):
    for team in teams.get_teams():
        if team['id'] == team_id:
            return team['abbreviation']
    return ""

def get_team_stats(team_id, date, season):
    try:
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
    except:
        return {"W_PCT": None, "GP": 0}

def get_game_data(season, start_date, end_date, output_csv):
    # PREDEFINED FIELD NAMES in organized order
    BOXSCORE_COLUMNS = [
        'GAME_ID', 'TEAM_ID', 'TEAM_ABBREVIATION', 'TEAM_CITY', 'PLAYER_ID', 'PLAYER_NAME', 
        'NICKNAME', 'START_POSITION',  'MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 
        'FG3A', 'FG3_PCT', 'FTM', 'FTA', 'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'STL', 
        'BLK', 'TO', 'PF', 'PTS', 'PLUS_MINUS'
    ]
    
    SEASON_COLUMNS = [
        'SEASON_Player_ID', 'SEASON_MIN', 'SEASON_FGM', 'SEASON_FGA', 'SEASON_FG_PCT', 
        'SEASON_FG3M', 'SEASON_FG3A', 'SEASON_FG3_PCT', 'SEASON_FTM', 'SEASON_FTA', 
        'SEASON_FT_PCT', 'SEASON_OREB', 'SEASON_DREB', 'SEASON_REB', 'SEASON_AST', 
        'SEASON_STL', 'SEASON_BLK', 'SEASON_TOV', 'SEASON_PF', 'SEASON_PTS', 
        'SEASON_PLUS_MINUS', 'SEASON_VIDEO_AVAILABLE'
    ]
    
    RECENT_COLUMNS = [
        'RECENT_Player_ID', 'RECENT_MIN', 'RECENT_FGM', 'RECENT_FGA', 'RECENT_FG_PCT', 
        'RECENT_FG3M', 'RECENT_FG3A', 'RECENT_FG3_PCT', 'RECENT_FTM', 'RECENT_FTA', 
        'RECENT_FT_PCT', 'RECENT_OREB', 'RECENT_DREB', 'RECENT_REB', 'RECENT_AST', 
        'RECENT_STL', 'RECENT_BLK', 'RECENT_TOV', 'RECENT_PF', 'RECENT_PTS', 
        'RECENT_PLUS_MINUS', 'RECENT_VIDEO_AVAILABLE'
    ]
    
    VS_TEAM_COLUMNS = [
        'VS_TEAM_Player_ID', 'VS_TEAM_MIN', 'VS_TEAM_FGM', 'VS_TEAM_FGA', 'VS_TEAM_FG_PCT', 
        'VS_TEAM_FG3M', 'VS_TEAM_FG3A', 'VS_TEAM_FG3_PCT', 'VS_TEAM_FTM', 'VS_TEAM_FTA', 
        'VS_TEAM_FT_PCT', 'VS_TEAM_OREB', 'VS_TEAM_DREB', 'VS_TEAM_REB', 'VS_TEAM_AST', 
        'VS_TEAM_STL', 'VS_TEAM_BLK', 'VS_TEAM_TOV', 'VS_TEAM_PF', 'VS_TEAM_PTS', 
        'VS_TEAM_PLUS_MINUS', 'VS_TEAM_VIDEO_AVAILABLE'
    ]
    
    TEAM_COLUMNS = [
        'TEAM_W_PCT', 'TEAM_GP', 'TEAM_W', 'TEAM_L'
    ]
    
    OPP_COLUMNS = [
        'OPP_W_PCT', 'OPP_GP', 'OPP_W', 'OPP_L'
    ]
    
    # Complete ordered fieldnames
    ALL_FIELDNAMES = BOXSCORE_COLUMNS + SEASON_COLUMNS + RECENT_COLUMNS + VS_TEAM_COLUMNS + TEAM_COLUMNS + OPP_COLUMNS
    
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    games_df = safe_api_call(leaguegamefinder.LeagueGameFinder, season_nullable=season).get_data_frames()[0]
    nba_team_ids = {team['id'] for team in teams.get_teams()}
    games_df = games_df[games_df["TEAM_ID"].isin(nba_team_ids)]

    games_df.to_csv("games_df.csv", index=False)  # Save games_df for debugging
    games_df["GAME_DATE"] = pd.to_datetime(games_df["GAME_DATE"])
    games_df = games_df[(games_df["GAME_DATE"] >= start_dt) & (games_df["GAME_DATE"] <= end_dt)]
    games_df.to_csv("filtered_games_df.csv", index=False)  # Save filtered games_df for debugging
    games_df = games_df.head(1)
    print(len(games_df), "games found between", start_date, "and", end_date)
    
    
    count = 0
    row_data_list = []
    excluded_players = []  # Track excluded players and their missing data
    
    def has_complete_data(row_data, required_fields):
        """Check if a row has data for all required fields"""
        missing_fields = []
        for field in required_fields:
            if field not in row_data or row_data[field] is None or row_data[field] == '':
                missing_fields.append(field)
        return len(missing_fields) == 0, missing_fields
    
    try:
        for gidx, game in games_df.iterrows():
            game_id = game['GAME_ID']
            game_date = game['GAME_DATE']
            boxscore = safe_api_call(boxscoretraditionalv2.BoxScoreTraditionalV2, game_id=game_id).get_data_frames()[0]
            boxscore.to_csv(f"boxscore_{game_id}.csv", index=False)  # Save boxscore for debugging
            
            
            for pidx, player_row in boxscore.iterrows():
                count += 1
                if count > 10:
                    continue
                    
                print(f"player{pidx} of game{gidx}")
                if player_row['MIN'] == '0':
                    continue
                    
                player_name = player_row['PLAYER_NAME']
                print("Processing player:", player_name)
                player = players.find_players_by_full_name(player_name)
                if not player:
                    print(f"  Player {player_name} not found in API, skipping")
                    excluded_players.append({
                        'player_name': player_name,
                        'game_id': game_id,
                        'game_date': str(game_date.date()),
                        'reason': 'Player not found in API',
                        'missing_fields': ['ALL - Player not found in API']
                    })
                    continue
                    
                player_id = str(player[0]['id'])
                team_id = player_row['TEAM_ID'] 
                opp_ids = [tid for tid in boxscore['TEAM_ID'].unique() if tid != team_id] 
                opp_team_id = str(opp_ids[0]) if opp_ids else None
                
                
                print("Season Stats:")
                season_avg = get_player_season_avg(player_id, season)
                print(season_avg)
                print("Recent Games Stats:")
                recent_avg = get_recent_games_avg(player_id, season, game_date)
                print(recent_avg)
                print("Recent vs Team Stats:")
                recent_vs_team_avg = get_recent_vs_team_avg(player_id, season, game_date, opp_team_id)
                print(recent_vs_team_avg)
                print("Team Stats:")
                team_stats = get_team_stats(team_id, game_date, season)
                print("team api working-----------------------------------")
                print(team_stats)
                print("Opponent Team Stats:")
                opp_stats = get_team_stats(opp_team_id, game_date, season)
                print(opp_stats)

                print("Compiling row data for player:", player_name)
                
                # Build the complete row data
                row_data = {
                    **player_row.to_dict(),
                    **{f"SEASON_{k}": v for k, v in season_avg.items()},
                    **{f"RECENT_{k}": v for k, v in recent_avg.items()},
                    **{f"VS_TEAM_{k}": v for k, v in recent_vs_team_avg.items()},
                    **{f"TEAM_{k}": v for k, v in team_stats.items()},
                    **{f"OPP_{k}": v for k, v in opp_stats.items()}
                }
                
                # Check if player has complete data for all required fields
                is_complete, missing_fields = has_complete_data(row_data, ALL_FIELDNAMES)
                
                if is_complete:
                    print(f"  Player {player_name} has complete data, adding to dataset")
                    row_data_list.append(row_data)
                else:
                    print(f"  Player {player_name} missing data for {len(missing_fields)} fields, skipping")
                    print(f"  Missing fields: {missing_fields[:5]}..." if len(missing_fields) > 5 else f"  Missing fields: {missing_fields}")
                    
                    # Track excluded player
                    excluded_players.append({
                        'player_name': player_name,
                        'player_id': player_id,
                        'game_id': game_id,
                        'game_date': str(game_date.date()),
                        'team_id': team_id,
                        'reason': 'Missing required data fields',
                        'missing_fields': missing_fields
                    })
                
    except CriticalTimeoutException as e:
        print("Critical timeout encountered. Saving collected data and exiting:", e)
    except Exception as e:
        print("Error encountered:", e)
        print("Saving collected data and exiting...")
    finally:
        folder_path = r'C:\Users\ucbra\OneDrive\Documents\NBA\data_collection\output'
        
        csv_path = os.path.join(folder_path, output_csv)

        if not row_data_list:
            print("No complete data collected.")
        else:
            print("Writing data to CSV:")
            
            with open(csv_path, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=ALL_FIELDNAMES)
                writer.writeheader()
                for row_data in row_data_list:
                    # Create complete row ensuring all fields are present
                    complete_row = {field: row_data.get(field, None) for field in ALL_FIELDNAMES}
                    writer.writerow(complete_row)

            print(f"Successfully wrote {len(row_data_list)} complete rows to {output_csv}")
        
        # Write excluded players report
        exclusion_report_file = output_csv.replace('.csv', '_exclusion_report.txt')
        exclusion_path = os.path.join(folder_path, exclusion_report_file)
        print(f"Writing exclusion report to {exclusion_path}")
        
        with open(exclusion_path, mode='w', encoding='utf-8') as f:
            f.write("NBA Data Collection - Excluded Players Report\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Total excluded players: {len(excluded_players)}\n")
            f.write(f"Total included players: {len(row_data_list)}\n\n")
            
            if excluded_players:
                f.write("EXCLUDED PLAYERS DETAILS:\n")
                f.write("-" * 30 + "\n\n")
                
                for i, player_info in enumerate(excluded_players, 1):
                    f.write(f"{i}. Player: {player_info['player_name']}\n")
                    f.write(f"   Game ID: {player_info['game_id']}\n")
                    f.write(f"   Game Date: {player_info['game_date']}\n")
                    if 'player_id' in player_info:
                        f.write(f"   Player ID: {player_info['player_id']}\n")
                    if 'team_id' in player_info:
                        f.write(f"   Team ID: {player_info['team_id']}\n")
                    f.write(f"   Reason: {player_info['reason']}\n")
                    f.write(f"   Missing Fields ({len(player_info['missing_fields'])}):\n")
                    
                    # Write missing fields in a readable format
                    for field in player_info['missing_fields']:
                        f.write(f"     - {field}\n")
                    
                    f.write("\n" + "-" * 50 + "\n\n")
                
                # Summary by missing field frequency
                f.write("MISSING FIELDS FREQUENCY ANALYSIS:\n")
                f.write("-" * 35 + "\n\n")
                
                field_counts = {}
                for player_info in excluded_players:
                    if player_info['reason'] == 'Missing required data fields':
                        for field in player_info['missing_fields']:
                            field_counts[field] = field_counts.get(field, 0) + 1
                
                if field_counts:
                    sorted_fields = sorted(field_counts.items(), key=lambda x: x[1], reverse=True)
                    for field, count in sorted_fields:
                        f.write(f"{field}: {count} players missing\n")
                else:
                    f.write("No field-specific missing data (all exclusions were API-related)\n")
            else:
                f.write("No players were excluded - all processed players had complete data.\n")
        
        print(f"Exclusion report saved to {exclusion_report_file}")
        print(f"Report includes {len(excluded_players)} excluded players")

# Example usage:
get_game_data("2023-24", "2024-01-04", "2024-01-04", "nba_games_output_organized16.csv")