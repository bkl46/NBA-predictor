"use client";
import { useEffect, useState } from "react";
import axios from "axios";

interface Game {
  id: string;
  date: string;
  teams: string;
}

export default function GamesPage() {
  const [games, setGames] = useState<Game[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchGames = async () => {
      debugger;
      setLoading(true);
      setError("");
      try {
        var s = process.env.NEXT_PUBLIC_API_BASE_URL
        const res = await axios.get(`${process.env.NEXT_PUBLIC_API_BASE_URL}/games`);
        setGames(res.data);
      } catch (err: any) {
        setError("Failed to load games");
      } finally {
        setLoading(false);
      }
    };
    fetchGames();
  }, []);

  if (loading) return <div className="p-4">Loading games...</div>;
  if (error) return (
  <div className="p-4 text-red-500">{error}
  <h1 className="text-2xl font-bold mb-4">Ensure Backend is setup and NBA_API is secure</h1>
  </div>
);

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Upcoming NBA Games</h1>
      <ul className="space-y-2">
        {games.map((game) => (
          <li key={game.id} className="border p-2 rounded hover:bg-gray-100">
            <a href={`/games/${game.id}?date=${encodeURIComponent(game.date)}`} className="text-blue-600 hover:underline">
              {game.teams} - {game.date}
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
} 