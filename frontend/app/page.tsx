"use client";

import Link from "next/link";
import { useState, useEffect } from "react";

export default function Home() {
  const [isDark, setIsDark] = useState(true);

  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDark]);

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 transition-colors duration-500 overflow-hidden">
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-0 left-0 w-full h-full opacity-30 dark:opacity-100"
          style={{
            background: `radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.15) 0px, transparent 50%),
                        radial-gradient(at 100% 0%, rgba(168, 85, 247, 0.15) 0px, transparent 50%),
                        radial-gradient(at 100% 100%, rgba(16, 185, 129, 0.1) 0px, transparent 50%),
                        radial-gradient(at 0% 100%, rgba(59, 130, 246, 0.15) 0px, transparent 50%)`,
            filter: 'blur(80px)',
            animation: 'mesh-move 20s ease infinite alternate'
          }}
        />
      </div>

      <div className="fixed top-[10%] left-[5%] w-64 h-64 bg-indigo-500/5 rounded-full blur-[120px] pointer-events-none"></div>
      <div className="fixed bottom-[10%] right-[5%] w-96 h-96 bg-purple-500/5 rounded-full blur-[120px] pointer-events-none"></div>

      <nav className="relative w-full max-w-7xl mx-auto px-6 py-8 flex justify-between items-center z-10">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-indigo-600 flex items-center justify-center shadow-lg shadow-indigo-600/20">
            <span className="text-white text-2xl">🤖</span>
          </div>
          <span className="text-xl font-extrabold tracking-tight">OmniRetail</span>
        </div>
        <div className="flex items-center gap-6">
          <button 
            onClick={() => setIsDark(!isDark)}
            className="p-2 rounded-full hover:bg-slate-200 dark:hover:bg-slate-800 transition-colors"
          >
            {isDark ? '☀️' : '🌙'}
          </button>
          <a className="px-5 py-2.5 rounded-full bg-slate-900 dark:bg-white text-white dark:text-slate-900 font-semibold text-sm hover:opacity-90 transition-opacity" href="#">
            Get Started
          </a>
        </div>
      </nav>

      <main className="relative w-full max-w-6xl mx-auto px-6 py-12 flex flex-col items-center text-center z-10">
        <header className="mb-20 space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-600/10 text-indigo-600 dark:text-indigo-400 border border-indigo-600/20 text-xs font-bold uppercase tracking-widest mb-4">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-600 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-indigo-600"></span>
            </span>
            Powered by Multi-Agent AI
          </div>
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-4">
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-slate-900 to-slate-600 dark:from-white dark:to-slate-400">
              Omni-Retail Assistant
            </span>
          </h1>
          <p className="text-xl text-slate-600 dark:text-slate-400 max-w-2xl mx-auto leading-relaxed">
            The unified intelligence layer for your retail ecosystem. Seamlessly handle text, voice, and data orchestration.
          </p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 w-full">
          <Link
            href="/chat"
            className="group relative overflow-hidden rounded-3xl p-10 flex flex-col items-center transition-all duration-400 hover:transform hover:-translate-y-3 hover:scale-105 bg-white/30 dark:bg-white/5 backdrop-blur-md border border-slate-200/50 dark:border-white/10 hover:shadow-2xl hover:shadow-emerald-500/20 hover:border-emerald-500/50"
          >
            <div className="w-20 h-20 rounded-2xl bg-emerald-500/10 text-emerald-500 flex items-center justify-center mb-8 group-hover:scale-110 transition-transform text-5xl">
              💬
            </div>
            <h3 className="text-2xl font-bold mb-3">Chat Interface</h3>
            <p className="text-slate-500 dark:text-slate-400 leading-relaxed mb-6">
              Multi-agent text support powered by LangGraph for complex reasoning and workflow automation.
            </p>
            <div className="mt-auto flex items-center gap-2 text-emerald-500 font-bold">
              Open Chat <span className="group-hover:translate-x-1 transition-transform">→</span>
            </div>
          </Link>

          <Link
            href="/voice"
            className="group relative overflow-hidden rounded-3xl p-10 flex flex-col items-center transition-all duration-400 hover:transform hover:-translate-y-3 hover:scale-105 bg-white/30 dark:bg-white/5 backdrop-blur-md border border-slate-200/50 dark:border-white/10 hover:shadow-2xl hover:shadow-purple-500/20 hover:border-purple-500/50"
          >
            <div className="w-20 h-20 rounded-2xl bg-purple-500/10 text-purple-500 flex items-center justify-center mb-8 group-hover:scale-110 transition-transform text-5xl">
              🎤
            </div>
            <h3 className="text-2xl font-bold mb-3">Voice Interface</h3>
            <p className="text-slate-500 dark:text-slate-400 leading-relaxed mb-6">
              Natural language voice processing using Google ADK for hands-free inventory and order queries.
            </p>
            <div className="mt-auto flex items-center gap-2 text-purple-500 font-bold">
              Start Speaking <span className="group-hover:translate-x-1 transition-transform">→</span>
            </div>
          </Link>

          <Link
            href="/dashboard"
            className="group relative overflow-hidden rounded-3xl p-10 flex flex-col items-center transition-all duration-400 hover:transform hover:-translate-y-3 hover:scale-105 bg-white/30 dark:bg-white/5 backdrop-blur-md border border-slate-200/50 dark:border-white/10 hover:shadow-2xl hover:shadow-blue-500/20 hover:border-blue-500/50"
          >
            <div className="w-20 h-20 rounded-2xl bg-blue-500/10 text-blue-500 flex items-center justify-center mb-8 group-hover:scale-110 transition-transform text-5xl">
              📊
            </div>
            <h3 className="text-2xl font-bold mb-3">Dashboard</h3>
            <p className="text-slate-500 dark:text-slate-400 leading-relaxed mb-6">
              Real-time monitoring of agent performance, latency, and database health on Neon PostgreSQL.
            </p>
            <div className="mt-auto flex items-center gap-2 text-blue-500 font-bold">
              View Insights <span className="group-hover:translate-x-1 transition-transform">→</span>
            </div>
          </Link>
        </div>
      </main>

      <footer className="relative w-full py-12 px-6 z-10 border-t border-slate-200/50 dark:border-white/5 bg-white/50 dark:bg-slate-900/50 backdrop-blur-md mt-20">
        <div className="max-w-6xl mx-auto flex flex-col items-center">
          <p className="text-xs font-bold uppercase tracking-widest text-slate-400 mb-8">
            Integrated With Enterprise Tech Stack
          </p>
          <div className="flex flex-wrap justify-center items-center gap-12 md:gap-20 opacity-50 hover:opacity-100 transition-opacity grayscale hover:grayscale-0">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 bg-emerald-500 rounded flex items-center justify-center text-[10px] text-white font-bold">L</div>
              <span className="text-sm font-bold tracking-tight">LangGraph</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center text-[10px] text-white font-bold">G</div>
              <span className="text-sm font-bold tracking-tight">Google ADK</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 bg-green-400 rounded-lg flex items-center justify-center text-[10px] text-black font-bold">N</div>
              <span className="text-sm font-bold tracking-tight">Neon DB</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 bg-black dark:bg-white rounded-full flex items-center justify-center text-[10px] text-white dark:text-black font-bold">N</div>
              <span className="text-sm font-bold tracking-tight">Next.js</span>
            </div>
          </div>
          <div className="mt-12 text-slate-400 text-sm">
            © 2024 Omni-Retail Intelligence System. All rights reserved.
          </div>
        </div>
      </footer>

      <style jsx global>{`
        @keyframes mesh-move {
          0% { transform: scale(1); }
          100% { transform: scale(1.1); }
        }
      `}</style>
    </div>
  );
}
