import collection
import pandas as pd
from nba_api.stats.endpoints import playergamelog, boxscoretraditionalv2, leaguegamefinder, commonplayerinfo, teamgamelog, teamyearbyyearstats, commonteamroster
import os

def get_player_input_data(player_id, season, opponent_team_id, date, player_team_id):
    """
    Generate input data for a single player prediction.
    
    Args:
        player_id (str): NBA player ID
        season (str): NBA season (e.g., "2023-24")
        opponent_team_id (str): ID of the opposing team
        date (str): Game date in "YYYY-MM-DD" format
        player_team_id (str): ID of the player's team
    
    Returns:
        dict: Dictionary containing all input features for the player
    """
    
    # Define column names for consistent output
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
    
    try:
        print(f"Generating input data for player {player_id} on {date}")
        
        # Get player season averages
        print("Getting season averages...")
        season_avg = collection.get_player_season_avg(player_id, season)
        
        # Get recent games averages (last 2 games)
        print("Getting recent games averages...")
        recent_avg = collection.get_recent_games_avg(player_id, season, date)
        
        # Get recent vs team averages
        print("Getting recent vs team averages...")
        recent_vs_team_avg = collection.get_recent_vs_team_avg(player_id, season, date, opponent_team_id)
        
        # Get player's team stats
        print("Getting player's team stats...")
        team_stats = collection.get_team_stats(player_team_id, date, season)
        
        # Get opponent team stats
        print("Getting opponent team stats...")
        opp_stats = collection.get_team_stats(opponent_team_id, date, season)
        
        # Build the complete input data dictionary
        input_data = {
            # Add basic identifiers
            'PLAYER_ID': player_id,
            'SEASON': season,
            'OPPONENT_TEAM_ID': opponent_team_id,
            'GAME_DATE': date,
            'PLAYER_TEAM_ID': player_team_id,
            
            # Season averages with prefixes
            **{f"SEASON_{k}": v for k, v in season_avg.items()},
            
            # Recent games averages with prefixes
            **{f"RECENT_{k}": v for k, v in recent_avg.items()},
            
            # Recent vs team averages with prefixes
            **{f"VS_TEAM_{k}": v for k, v in recent_vs_team_avg.items()},
            
            # Team stats with prefixes
            **{f"TEAM_{k}": v for k, v in team_stats.items()},
            
            # Opponent stats with prefixes
            **{f"OPP_{k}": v for k, v in opp_stats.items()}
        }
        
        # Fill in any missing columns with None
        all_expected_columns = (SEASON_COLUMNS + RECENT_COLUMNS + VS_TEAM_COLUMNS + 
                               TEAM_COLUMNS + OPP_COLUMNS)
        
        for col in all_expected_columns:
            if col not in input_data:
                input_data[col] = None
        
        print(f"Successfully generated input data with {len(input_data)} features")
        
        info = commonplayerinfo.CommonPlayerInfo(player_id=player_id)
        df = info.get_data_frames()[0]
        name= df.loc[0, 'DISPLAY_FIRST_LAST']
        folder_path = r'C:\Users\ucbra\OneDrive\Documents\NBA\data_collection\output\player_inputs'
        
        csv_path = os.path.join(folder_path, f"player_input_{name}_{season}_{date}.csv")
        pd.DataFrame([input_data]).to_csv(csv_path, index=False)  # Save for debugging
        return input_data
        
    except Exception as e:
        print(f"Error generating input data: {e}")
        return None
    
    
print(get_player_input_data("202691", "2023-24", "1610612743", "2024-01-04", "1610612744"))