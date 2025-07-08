"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import axios from "axios";

interface PlayerInfo {
  DISPLAY_FIRST_LAST: string;
  TEAM_NAME?: string;
  TEAM_ID?: string;
  // ...other fields
}

interface SeasonStat {
  SEASON_ID: string;
  TEAM_ABBREVIATION: string;
  GP: number;
  MIN: string;
  PTS: number;
  AST: number;
  REB: number;
  // ...other fields
}

interface Game {
  id: string;
  date: string;
  teams: string;
}

export default function PlayerDetailPage() {
  const { playerId } = useParams() as { playerId: string };
  const [playerInfo, setPlayerInfo] = useState<PlayerInfo | null>(null);
  const [seasonStats, setSeasonStats] = useState<SeasonStat[]>([]);
  const [upcomingGames, setUpcomingGames] = useState<Game[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Prediction section
  const [season, setSeason] = useState("");
  const [date, setDate] = useState("");
  const [opponentTeamId, setOpponentTeamId] = useState("");
  const [playerTeamId, setPlayerTeamId] = useState("");
  const [teams, setTeams] = useState<{ id: string; name: string }[]>([]);
  const [prediction, setPrediction] = useState<any>(null);
  const [predictLoading, setPredictLoading] = useState(false);
  const [predictError, setPredictError] = useState("");

  useEffect(() => {
    const fetchPlayer = async () => {
      setLoading(true);
      setError("");
      try {
        const res = await axios.get(`${process.env.NEXT_PUBLIC_API_BASE_URL}/players/${playerId}`);
        setPlayerInfo(res.data.player_info);
        setSeasonStats(res.data.season_stats);
        setUpcomingGames(res.data.upcoming_games);
        // Set defaults for prediction
        if (res.data.player_info?.TEAM_ID) setPlayerTeamId(res.data.player_info.TEAM_ID.toString());
        if (res.data.season_stats?.length > 0) setSeason(res.data.season_stats[0].SEASON_ID);
      } catch (err: any) {
        setError("Failed to load player details");
      } finally {
        setLoading(false);
      }
    };
    fetchPlayer();
  }, [playerId]);

  // Fetch NBA teams for opponent selection
  useEffect(() => {
    const fetchTeams = async () => {
      try {
        const res = await axios.get(`${process.env.NEXT_PUBLIC_API_BASE_URL}/teams`);
        setTeams(res.data);
      } catch {
        setTeams([]);
      }
    };
    fetchTeams();
  }, []);

  const handlePredict = async () => {
    setPredictLoading(true);
    setPredictError("");
    setPrediction(null);
    try {
      const res = await axios.post(`${process.env.NEXT_PUBLIC_API_BASE_URL}/predict`, {
        player_id: playerId,
        season,
        date,
        opponent_team_id: opponentTeamId,
        player_team_id: playerTeamId,
      });
      setPrediction(res.data.prediction);
    } catch (err: any) {
      setPredictError("Prediction failed. Please check your input and try again.");
    } finally {
      setPredictLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white p-8">
      <div className="max-w-3xl mx-auto">
        {loading ? (
          <div className="p-4">Loading player details...</div>
        ) : error ? (
          <div className="p-4 text-red-500">{error}</div>
        ) : playerInfo ? (
          <>
            <h1 className="text-3xl font-bold text-blue-200 mb-2">{playerInfo.DISPLAY_FIRST_LAST}</h1>
            <div className="text-lg text-gray-300 mb-2">{playerInfo.TEAM_NAME || "No Team"}</div>
            <div className="mb-4">
              <h2 className="text-xl font-semibold text-blue-100 mb-2">Season Stats</h2>
              {seasonStats.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="min-w-full bg-slate-800 rounded-lg">
                    <thead>
                      <tr>
                        <th className="px-2 py-1">Season</th>
                        <th className="px-2 py-1">Team</th>
                        <th className="px-2 py-1">GP</th>
                        <th className="px-2 py-1">MIN/G</th>
                        <th className="px-2 py-1">PTS/G</th>
                        <th className="px-2 py-1">AST/G</th>
                        <th className="px-2 py-1">REB/G</th>
                      </tr>
                    </thead>
                    <tbody>
                      {seasonStats.slice(0, 5).map((stat, idx) => {
                        const gp = stat.GP || 0;
                        const min = gp > 0 ? (parseFloat(stat.MIN) / gp).toFixed(1) : "-";
                        const pts = gp > 0 ? (stat.PTS / gp).toFixed(1) : "-";
                        const ast = gp > 0 ? (stat.AST / gp).toFixed(1) : "-";
                        const reb = gp > 0 ? (stat.REB / gp).toFixed(1) : "-";
                        return (
                          <tr key={idx} className="text-center">
                            <td className="px-2 py-1">{stat.SEASON_ID}</td>
                            <td className="px-2 py-1">{stat.TEAM_ABBREVIATION}</td>
                            <td className="px-2 py-1">{stat.GP}</td>
                            <td className="px-2 py-1">{min}</td>
                            <td className="px-2 py-1">{pts}</td>
                            <td className="px-2 py-1">{ast}</td>
                            <td className="px-2 py-1">{reb}</td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div>No season stats available.</div>
              )}
            </div>
            <div className="mb-6">
              <h2 className="text-xl font-semibold text-blue-100 mb-2">Upcoming Games</h2>
              {upcomingGames.length > 0 ? (
                <ul className="list-disc ml-6">
                  {upcomingGames.map((game, idx) => (
                    <li key={idx}>{game.teams} - {game.date}</li>
                  ))}
                </ul>
              ) : (
                <div>No upcoming games.</div>
              )}
            </div>
            <div className="bg-slate-800 rounded-lg p-6 mb-6">
              <h2 className="text-lg font-semibold text-blue-200 mb-4">Prediction</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                  <label className="block mb-1 text-sm">Season</label>
                  <input
                    type="text"
                    value={season}
                    onChange={e => setSeason(e.target.value)}
                    className="w-full p-2 rounded bg-slate-900 text-white border border-slate-700"
                    placeholder="e.g. 2023-24"
                  />
                </div>
                <div>
                  <label className="block mb-1 text-sm">Date</label>
                  <input
                    type="date"
                    value={date}
                    onChange={e => setDate(e.target.value)}
                    className="w-full p-2 rounded bg-slate-900 text-white border border-slate-700"
                  />
                </div>
                <div>
                  <label className="block mb-1 text-sm">Opponent Team</label>
                  <select
                    value={opponentTeamId}
                    onChange={e => setOpponentTeamId(e.target.value)}
                    className="w-full p-2 rounded bg-slate-900 text-white border border-slate-700"
                  >
                    <option value="">Select team</option>
                    {teams.map(team => (
                      <option key={team.id} value={team.id}>{team.name}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block mb-1 text-sm">Player Team</label>
                  <input
                    type="text"
                    value={playerTeamId}
                    onChange={e => setPlayerTeamId(e.target.value)}
                    className="w-full p-2 rounded bg-slate-900 text-white border border-slate-700"
                    placeholder="Team ID"
                  />
                </div>
              </div>
              <button
                className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 font-semibold"
                onClick={handlePredict}
                disabled={predictLoading || !season || !date || !opponentTeamId || !playerTeamId}
              >
                {predictLoading ? "Predicting..." : "Predict"}
              </button>
              {predictError && <div className="text-red-400 mt-2">{predictError}</div>}
              {prediction && (
                <div className="mt-4 bg-slate-900 p-4 rounded">
                  <h3 className="text-blue-200 font-semibold mb-2">Prediction Result</h3>
                  <table className="min-w-full text-left">
                    <thead>
                      <tr>
                        <th className="pr-4">Stat</th>
                        <th>Value</th>
                      </tr>
                    </thead>
                    <tbody>
                      {(() => {
                        // If prediction is an array, map to stat names
                        const statOrder = ['PTS', 'REB', 'AST', 'STL', 'BLK', 'FGM', 'FGA', 'FG3M', 'FG3A', 'FTM', 'FTA'];
                        if (Array.isArray(prediction)) {
                          return statOrder.map((stat, idx) => (
                            <tr key={stat}>
                              <td className="pr-4 font-semibold">{stat}</td>
                              <td>{typeof prediction[idx] === 'number' ? prediction[idx].toFixed(2) : prediction[idx]}</td>
                            </tr>
                          ));
                        } else if (typeof prediction === 'object' && prediction !== null) {
                          // If prediction is a dict/object
                          return statOrder.map((stat) => (
                            <tr key={stat}>
                              <td className="pr-4 font-semibold">{stat}</td>
                              <td>{typeof prediction[stat] === 'number' ? prediction[stat].toFixed(2) : prediction[stat]}</td>
                            </tr>
                          ));
                        } else {
                          return <tr><td colSpan={2}>{String(prediction)}</td></tr>;
                        }
                      })()}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </>
        ) : null}
      </div>
    </div>
  );
} 