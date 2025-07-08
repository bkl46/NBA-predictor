"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import axios from "axios";

interface Player {
  PLAYER_ID: string;
  PLAYER_NAME: string;
  IS_ACTIVE: boolean;
}

export default function PlayersPage() {
  const router = useRouter();
  const [players, setPlayers] = useState<Player[]>([]);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");

  // Debounce search input
  useEffect(() => {
    const handler = setTimeout(() => setDebouncedSearch(search), 400);
    return () => clearTimeout(handler);
  }, [search]);

  useEffect(() => {
    const fetchPlayers = async () => {
      setLoading(true);
      setError("");
      try {
        const res = await axios.get(`${process.env.NEXT_PUBLIC_API_BASE_URL}/players/all`, {
          params: { search: debouncedSearch, page, limit: 30 },
        });
        setPlayers(res.data.players);
        setTotalPages(res.data.totalPages);
      } catch (err: any) {
        setError("Failed to load players");
      } finally {
        setLoading(false);
      }
    };
    fetchPlayers();
  }, [debouncedSearch, page]);

  return (
    <div className="min-h-screen bg-slate-900 text-white p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-blue-200 mb-6">NBA Players</h1>
        <div className="mb-4 flex items-center">
          <input
            type="text"
            placeholder="Search players..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="w-full p-2 rounded bg-slate-800 text-white border border-slate-700 focus:outline-none focus:border-blue-400"
          />
        </div>
        {loading ? (
          <div className="p-4">Loading players...</div>
        ) : error ? (
          <div className="p-4 text-red-500">{error}</div>
        ) : (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 mb-6">
              {players.map(player => (
                <button
                  key={player.PLAYER_ID}
                  className="bg-slate-800 border border-slate-700 rounded-lg p-4 text-left hover:bg-blue-900 transition-colors shadow"
                  onClick={() => router.push(`/players/${player.PLAYER_ID}`)}
                >
                  <div className="font-semibold text-lg text-blue-200">{player.PLAYER_NAME}</div>
                  <div className="text-xs text-gray-400 mt-1">ID: {player.PLAYER_ID}</div>
                  {!player.IS_ACTIVE && <div className="text-xs text-red-400 mt-1">Inactive</div>}
                </button>
              ))}
            </div>
            <div className="flex justify-center items-center space-x-2">
              <button
                className="px-3 py-1 rounded bg-slate-700 text-white disabled:opacity-50"
                onClick={() => setPage(page - 1)}
                disabled={page <= 1}
              >
                Prev
              </button>
              <span className="text-blue-200 font-semibold">Page {page} of {totalPages}</span>
              <button
                className="px-3 py-1 rounded bg-slate-700 text-white disabled:opacity-50"
                onClick={() => setPage(page + 1)}
                disabled={page >= totalPages}
              >
                Next
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
} 