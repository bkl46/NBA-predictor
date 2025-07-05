export default function AboutPage() {
  return (
    <div className="min-h-screen bg-slate-900 text-white p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-blue-200 mb-6">About Me</h1>
        <div className="bg-slate-800 p-6 rounded-lg">
          <p className="text-gray-300 mb-4">
            Hi! I'm a developer passionate about basketball analytics and machine learning.
          </p>
          <div className="space-y-4 mt-6">
            <div className="border-l-4 border-blue-500 pl-4">
              <h3 className="text-lg font-semibold text-blue-200">Background</h3>
              <p className="text-gray-400 text-sm">Experienced in data science, web development, and sports analytics.</p>
            </div>
            <div className="border-l-4 border-green-500 pl-4">
              <h3 className="text-lg font-semibold text-green-200">Technologies Used</h3>
              <p className="text-gray-400 text-sm">Python, FastAPI, Next.js, TypeScript, Machine Learning, NBA APIs.</p>
            </div>
            <div className="border-l-4 border-purple-500 pl-4">
              <h3 className="text-lg font-semibold text-purple-200">Project Goals</h3>
              <p className="text-gray-400 text-sm">Creating accurate, user-friendly NBA prediction tools for fans and analysts.</p>
            </div>
          </div>
          <div className="mt-8 pt-6 border-t border-slate-700">
            <p className="text-gray-400 text-sm">
              This project combines my love for basketball with modern web development and AI technologies.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
} 