"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import axios from "axios";
import PredictionChart from "../../../components/PredictionChart";

export default function PredictPage() {
  const params = useParams();
  const { playerId, gameId } = params as { playerId: string; gameId: string };
  const [prediction, setPrediction] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchPrediction = async () => {
      setLoading(true);
      setError("");
      try {
        const res = await axios.post(`${process.env.NEXT_PUBLIC_API_BASE_URL}/predict`, {
          player_id: playerId,
          game_id: gameId,
        });
        setPrediction(res.data.prediction);
      } catch (err: any) {
        setError("Failed to fetch prediction");
      } finally {
        setLoading(false);
      }
    };
    fetchPrediction();
  }, [playerId, gameId]);

  if (loading) return <div className="p-4">Loading prediction...</div>;
  if (error) return <div className="p-4 text-red-500">{error}</div>;

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Prediction for Player {playerId} in Game {gameId}</h1>
      {prediction ? (
        <PredictionChart prediction={prediction} />
      ) : (
        <div>No prediction available.</div>
      )}
    </div>
  );
} 