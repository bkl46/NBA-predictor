export default function ModelsPage() {
  return (
    <div className="min-h-screen bg-slate-900 text-white p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-blue-200 mb-6">Prediction Models</h1>
        <div className="bg-slate-800 p-6 rounded-lg">
          <p className="text-gray-300 mb-4">
            Our prediction system uses machine learning models trained on historical NBA data to forecast player performance.
          </p>
          <div className="space-y-4 mt-6">
            <div className="border-l-4 border-blue-500 pl-4">
              <h3 className="text-lg font-semibold text-blue-200">Multi-Output Regression</h3>
              <p className="text-gray-400 text-sm">Predicts multiple statistics simultaneously for comprehensive analysis.</p>
            </div>
            <div className="border-l-4 border-green-500 pl-4">
              <h3 className="text-lg font-semibold text-green-200">Player-Specific Models</h3>
              <p className="text-gray-400 text-sm">Individual models trained for each player's unique playing style.</p>
            </div>
            <div className="border-l-4 border-purple-500 pl-4">
              <h3 className="text-lg font-semibold text-purple-200">Real-Time Updates</h3>
              <p className="text-gray-400 text-sm">Models are updated with the latest game data for improved accuracy.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 