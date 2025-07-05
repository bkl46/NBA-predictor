import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score
import xgboost as xgb
import joblib
import os


path = r'C:\Users\ucbra\OneDrive\Documents\NBA\data_collection\output\nba_games_output_organized20.csv'
# Load and prepare data
df = pd.read_csv(path)

# Define features and targets
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
target_columns = ['PTS', 'REB', 'AST', 'STL', 'BLK', 'FGM', 'FGA', 'FG3M', 'FG3A', 'FTM', 'FTA']

X = df[feature_columns]
y = df[target_columns]


from xgboost import XGBRegressor
from sklearn.multioutput import MultiOutputRegressor

# Multi-output XGBoost
model = MultiOutputRegressor(XGBRegressor(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    random_state=42
))

# Train
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model.fit(X_train, y_train)

# Train
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
for i, col in enumerate(target_columns):
    score = r2_score(y_test[col], y_pred[:, i])
    print(f'R2 score for {col}: {score:.3f}')
    
# Path to your input CSV
input_csv = r'C:\Users\ucbra\OneDrive\Documents\NBA\data_collection\output\player_inputs\player_input_Klay Thompson_2023-24_2024-01-04.csv'

# Load input data
input_df = pd.read_csv(input_csv)

# Select only the feature columns (in case there are extra columns)
input_features = input_df[feature_columns]

# If you used pd.get_dummies() on X during training, do the same here and align columns:
# input_features = pd.get_dummies(input_features)
# input_features = input_features.reindex(columns=X.columns, fill_value=0)

# Predict
prediction = model.predict(input_features)
print("Predicted stats:", dict(zip(target_columns, prediction[0])))

iteration = 1
model_path = r'C:\Users\ucbra\OneDrive\Documents\NBA\analytics\models'
final_path = os.path.join(model_path, f'nba_xgb_multioutput_model{iteration}.joblib')
joblib.dump(model, final_path )