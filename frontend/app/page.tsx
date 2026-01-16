import Link from 'next/link'

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-gradient-to-br from-slate-900 to-slate-800">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-white mb-4">
          🤖 Omni-Retail Assistant
        </h1>
        <p className="text-2xl text-gray-300 mb-12">
          Multi-Agent Customer Support System
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl">
          <Link 
            href="/chat"
            className="bg-gradient-to-r from-teal-600 to-teal-700 hover:from-teal-700 hover:to-teal-800 text-white p-8 rounded-lg shadow-lg transition transform hover:scale-105"
          >
            <div className="text-5xl mb-4">💬</div>
            <h2 className="text-2xl font-bold mb-2">Chat Interface</h2>
            <p className="text-teal-100">Text-based multi-agent support</p>
          </Link>
          
          <Link 
            href="/voice"
            className="bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 text-white p-8 rounded-lg shadow-lg transition transform hover:scale-105"
          >
            <div className="text-5xl mb-4">🎤</div>
            <h2 className="text-2xl font-bold mb-2">Voice Interface</h2>
            <p className="text-purple-100">Speak naturally to get help</p>
          </Link>
          
          <Link 
            href="/dashboard"
            className="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white p-8 rounded-lg shadow-lg transition transform hover:scale-105"
          >
            <div className="text-5xl mb-4">📊</div>
            <h2 className="text-2xl font-bold mb-2">Dashboard</h2>
            <p className="text-blue-100">Monitor agent performance</p>
          </Link>
        </div>
        
        <div className="mt-12 text-gray-400">
          <p className="mb-2">Powered by:</p>
          <p className="text-sm">LangGraph • Google ADK • Neon PostgreSQL • Next.js</p>
        </div>
      </div>
    </main>
  )
}
