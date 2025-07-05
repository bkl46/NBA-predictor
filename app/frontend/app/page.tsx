import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen bg-slate-900 text-white p-8">
      <div className="max-w-6xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-start">
          {/* Left side - Title and description */}
          <div className="space-y-6">
            <h1 className="text-4xl sm:text-5xl font-bold text-blue-200">
              NBA Stats Predictor
            </h1>
            <p className="text-lg text-gray-300 leading-relaxed">
              An AI-powered platform that analyzes player performance data to predict 
              upcoming game statistics. Select a game, choose a player, and get 
              detailed predictions for points, rebounds, assists, and more.
            </p>
          </div>

          {/* Right side - Navigation buttons */}
          <div className="space-y-4">
            <Link href="/games">
              <button className="w-full p-4 text-left bg-slate-800 hover:bg-blue-600 transition-colors duration-200 border border-slate-700 hover:border-blue-500 rounded-lg">
                <span className="text-lg font-medium">View Upcoming Games</span>
                <p className="text-sm text-gray-400 mt-1">Browse scheduled NBA matchups</p>
              </button>
            </Link>

            <Link href="/players">
              <button className="w-full p-4 text-left bg-slate-800 hover:bg-blue-600 transition-colors duration-200 border border-slate-700 hover:border-blue-500 rounded-lg">
                <span className="text-lg font-medium">Players</span>
                <p className="text-sm text-gray-400 mt-1">Explore player statistics and profiles</p>
              </button>
            </Link>

            <Link href="/models">
              <button className="w-full p-4 text-left bg-slate-800 hover:bg-blue-600 transition-colors duration-200 border border-slate-700 hover:border-blue-500 rounded-lg">
                <span className="text-lg font-medium">Models</span>
                <p className="text-sm text-gray-400 mt-1">Learn about our prediction models</p>
              </button>
            </Link>

            <Link href="/about">
              <button className="w-full p-4 text-left bg-slate-800 hover:bg-blue-600 transition-colors duration-200 border border-slate-700 hover:border-blue-500 rounded-lg">
                <span className="text-lg font-medium">About Me</span>
                <p className="text-sm text-gray-400 mt-1">Learn more about the developer</p>
              </button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
