# NBA-predictor

## Project Overview

NBA Predictor is a full-stack application for predicting NBA player statistics for upcoming games. It leverages real NBA data, advanced feature engineering, and a machine learning model (multi-output XGBoost regressor) to forecast player performance. The project includes:

- **Automated data collection** from the NBA API
- **Feature engineering** for player, matchup, and team statistics
- **Model training** using historical data
- **REST API backend** (FastAPI) for serving predictions and NBA data
- **Modern frontend** (Next.js + React) for user interaction and visualization

---

## Data Collection

### How Data is Collected

- The data collection scripts are in `data_collection/collection.py`.
- The process uses the `nba_api` to fetch:
  - Game logs for players and teams
  - Box scores for each game
  - Player and team statistics (season averages, recent games, matchup history)
- Data is saved as CSV files in `data_collection/output/` for use in model training.

#### To Collect Data

1. **Install dependencies** (see below).
2. Run the data collection script:
   ```bash
   python data_collection/collection.py
   ```
   - You may need to edit the script to specify the season, date range, and output file.
   - The script handles NBA API rate limits and saves detailed logs and outputs.

---

## Model Training

### How Model Training Works

- The training script is in `analytics/train.py`.
- It loads the processed CSV data from `data_collection/output/`.
- Feature columns include season averages, recent performance, matchup data, and team stats.
- The model is a multi-output XGBoost regressor, predicting multiple stats (PTS, REB, AST, etc.) at once.
- The script evaluates model performance and saves the trained model as a `.joblib` file.

#### To Train the Model

1. **Ensure you have collected data** as above.
2. Run the training script:
   ```bash
   python analytics/train.py
   ```
   - The script will output evaluation metrics and save the model to `analytics/models/`.

---

## Application Structure

### Backend (API)

- Located in `app/backend/`
- Built with FastAPI
- Loads the trained model and exposes endpoints for:
  - Listing games and players
  - Fetching player and team details
  - Making predictions for player stats

#### To Launch the Backend

1. **Install backend dependencies:**
   ```bash
   pip install -r app/backend/requirements.txt
   ```
2. **Start the FastAPI server:**
   ```bash
   uvicorn main:app --reload
   ```
   - Run this command from the `app/backend/` directory.
   - The API will be available at `http://localhost:8000`.

### Frontend (Web App)

- Located in `app/frontend/`
- Built with Next.js (React, TypeScript, Tailwind CSS)
- Provides a user-friendly interface to:
  - Browse games and players
  - View predictions and player stats
  - Visualize results with charts

#### To Launch the Frontend

1. **Install frontend dependencies:**
   ```bash
   cd app/frontend
   npm install
   ```
2. **Start the development server:**
   ```bash
   npm run dev
   ```
   - The app will be available at `http://localhost:3000`.

---

## Dependency Installation

### Python Dependencies

- The root `requirements.txt` contains all necessary packages for data collection and model training:
  ```bash
  pip install -r requirements.txt
  ```
- The backend has its own `requirements.txt` for API dependencies:
  ```bash
  pip install -r app/backend/requirements.txt
  ```

### Node.js Dependencies (Frontend)

- Use `npm install` in `app/frontend/` to install all frontend dependencies.

---

## Usage Summary

1. **Collect NBA data** using the data collection script.
2. **Train the model** with the training script.
3. **Start the backend API** to serve predictions.
4. **Start the frontend app** to interact with the system and visualize predictions.

---

## Technologies Used

- Python, FastAPI, pandas, scikit-learn, XGBoost, nba_api, joblib
- React, Next.js, TypeScript, Tailwind CSS, Recharts

