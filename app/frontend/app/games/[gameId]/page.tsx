"use client";
import { useEffect, useState } from "react";
import axios from "axios";
import { useRouter, useParams, useSearchParams } from "next/navigation";

interface Player {
  GAME_ID: string;
  TEAM_ID: number;
  TEAM_ABBREVIATION: string;
  TEAM_CITY: string;
  PLAYER_ID: number;
  PLAYER_NAME: string;
  NICKNAME: string;
  START_POSITION: string;
  COMMENT: string;
  MIN: string;
  FGM: number;
  FGA: number;
  FG_PCT: number;
  FG3M: number;
  FG3A: number;
  FG3_PCT: number;
  FTM: number;
  FTA: number;
  FT_PCT: number;
  OREB: number;
  DREB: number;
  REB: number;
  AST: number;
  STL: number;
  BLK: number;
  TO: number;
  PF: number;
  PTS: number;
  PLUS_MINUS: number;
}

interface TeamPlayers {
  [teamAbbr: string]: {
    teamCity: string;
    players: Player[];
  };
}

export default function Game() {
  const router = useRouter();
  const params = useParams();
  const searchParams = useSearchParams();
  const { gameId } = params as { gameId: string };
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [teamPlayers, setTeamPlayers] = useState<TeamPlayers>({});
  const [teamScores, setTeamScores] = useState<{[teamAbbr: string]: number}>({});
  const [gameDate, setGameDate] = useState<string>("");

  useEffect(() => {
    const fetchGameDetails = async () => {
      setLoading(true);
      setError("");
      try {
        const res = await axios.get(`${process.env.NEXT_PUBLIC_API_BASE_URL}/games/${gameId}`);
        
        // Organize players by team and calculate team scores
        const organizedPlayers: TeamPlayers = {};
        const scores: {[teamAbbr: string]: number} = {};
        
        res.data.forEach((player: Player) => {
          const teamAbbr = player.TEAM_ABBREVIATION;
          
          if (!organizedPlayers[teamAbbr]) {
            organizedPlayers[teamAbbr] = {
              teamCity: player.TEAM_CITY,
              players: []
            };
            scores[teamAbbr] = 0;
          }
          
          organizedPlayers[teamAbbr].players.push(player);
          scores[teamAbbr] += player.PTS;
        });
        
        setTeamPlayers(organizedPlayers);
        setTeamScores(scores);
        
        // Get date from URL parameter, fallback to extracting from game ID
        const urlDate = searchParams.get('date');
        if (urlDate) {
          setGameDate(urlDate);
        } else if (gameId && gameId.length >= 8) {
          // Extract date from game ID (format: 0042300404 -> 2024-03-23)
          // NBA game IDs typically follow: 00 + year + month + day + sequence
          const year = "20" + gameId.substring(2, 4);
          const month = gameId.substring(4, 6);
          const day = gameId.substring(6, 8);
          const dateString = `${year}-${month}-${day}`;
          setGameDate(dateString);
        }
        
        console.log(res.data);
      } catch (err: any) {
        setError("Failed to load game details");
      } finally {
        setLoading(false);
      }
    };

    fetchGameDetails();
  }, [gameId]);

  const handlePlayerClick = (playerId: number, playerName: string) => {
    console.log(`Player clicked: ${playerName} (ID: ${playerId})`);
    // You can add navigation or other functionality here
  };

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Game Details</h1>
      {loading && <div className="p-4">Loading game details...</div>}
      {error && <div className="p-4 text-red-500">{error}</div>}
      <h2 className="text-xl font-semibold mb-4">Game ID: {gameId}</h2>
      {gameDate && (
        <div className="text-lg text-gray-600 mb-4">
          {new Date(gameDate).toLocaleDateString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
          })}
        </div>
      )}
      
      {!loading && !error && Object.keys(teamScores).length > 0 && (
        <div className="bg-white border rounded-lg p-6 mb-6 shadow-sm">
          <h3 className="text-lg font-semibold mb-4 text-center text-gray-700">Final Score</h3>
          <div className="flex justify-center items-center space-x-8">
            {Object.entries(teamScores).map(([teamAbbr, score]) => {
              const teamData = teamPlayers[teamAbbr];
              return (
                <div key={teamAbbr} className="text-center">
                  <div className="text-2xl font-bold text-gray-900">{score}</div>
                  <div className="text-sm text-gray-600">{teamData?.teamCity} {teamAbbr}</div>
                </div>
              );
            })}
            {Object.keys(teamScores).length === 2 && (
              <div className="text-gray-400 text-xl font-bold">-</div>
            )}
          </div>
        </div>
      )}
      
      {!loading && !error && Object.keys(teamPlayers).length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {Object.entries(teamPlayers).map(([teamAbbr, teamData]) => (
            <div key={teamAbbr} className="border rounded-lg p-4 bg-gray-50">
              <h3 className="text-lg font-semibold mb-3 text-blue-600">
                {teamData.teamCity} {teamAbbr}
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {teamData.players.map((player) => (
                  <button
                    key={player.PLAYER_ID}
                    onClick={() => handlePlayerClick(player.PLAYER_ID, player.PLAYER_NAME)}
                    className="bg-white border border-gray-300 rounded-lg p-3 text-left hover:bg-gray-50 hover:border-blue-300 transition-colors"
                  >
                    <div className="font-medium text-gray-900">{player.PLAYER_NAME}</div>
                    <div className="text-sm text-gray-600">
                      Position: {player.START_POSITION} | ID: {player.PLAYER_ID}
                    </div>
                    <div className="text-sm text-gray-500 mt-1">
                      {player.MIN} | {player.PTS} pts | {player.AST} ast | {player.REB} reb
                    </div>
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
} 