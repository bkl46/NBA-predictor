"use client";
import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import axios from "axios";

interface Player {
  id: string;
  name: string;
}

export default function PlayersPage() {
  const router = useRouter();
  const params = useParams();
  const { gameId } = params as { gameId: string };
  const [players, setPlayers] = useState<Player[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchPlayers = async () => {
      setLoading(true);
      setError("");
      try {
        const res = await axios.get(`${process.env.NEXT_PUBLIC_API_BASE_URL}/players`, { params: { game_id: gameId } });
        setPlayers(res.data);
      } catch (err: any) {
        setError("Failed to load players");
      } finally {
        setLoading(false);
      }
    };
    fetchPlayers();
  }, [gameId]);

  if (loading) return <div className="p-4">Loading players...</div>;
  if (error) return <div className="p-4 text-red-500">{error}</div>;

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Players for Game {gameId}</h1>
      <ul className="space-y-2">
        {players.map((player) => (
          <li key={player.id} className="border p-2 rounded hover:bg-gray-100 flex justify-between items-center">
            <span>{player.name}</span>
            <button
              className="bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700"
              onClick={() => router.push(`/predict/${player.id}/${gameId}`)}
            >
              Predict
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
} 