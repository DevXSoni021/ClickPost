'use client';

import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';

interface Agent {
  name: string;
  status: 'ready' | 'busy' | 'error';
  icon: string;
  queries_processed: number;
}

interface SystemMetrics {
  total_agents: number;
  active_conversations: number;
  avg_response_time: number;
  uptime: string;
}

export default function DashboardPage() {
  const [agents, setAgents] = useState<Agent[]>([
    {
      name: 'ShopCore Agent',
      status: 'ready',
      icon: '🛍️',
      queries_processed: 247
    },
    {
      name: 'ShipStream Agent',
      status: 'ready',
      icon: '📦',
      queries_processed: 189
    },
    {
      name: 'PayGuard Agent',
      status: 'ready',
      icon: '💳',
      queries_processed: 156
    },
    {
      name: 'CareDesk Agent',
      status: 'ready',
      icon: '🎫',
      queries_processed: 203
    }
  ]);

  const [metrics, setMetrics] = useState<SystemMetrics>({
    total_agents: 4,
    active_conversations: 3,
    avg_response_time: 0.87,
    uptime: '99.9%'
  });

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const response = await fetch('http://localhost:8000/agents/status');
        const data = await response.json();
        // Update metrics logic here if available from backend
      } catch (error) {
        console.error('Failed to fetch metrics:', error);
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-[#0f172a] text-slate-900 dark:text-slate-100 transition-colors duration-300 font-sans">
      <nav className="border-b border-slate-200 dark:border-slate-800 bg-white/50 dark:bg-slate-900/50 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-[1440px] mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-indigo-500 rounded-lg flex items-center justify-center">
              <span className="text-white text-xl">🤖</span>
            </div>
            <h1 className="font-bold text-xl tracking-tight">Omni-Retail <span className="text-indigo-500 font-medium">Assistant</span></h1>
          </div>
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-2 text-sm font-medium text-slate-500 dark:text-slate-400">
              <span className="w-2 h-2 rounded-full bg-green-500 shadow-[0_0_0_0_rgba(34,197,94,0.7)] animate-[pulse_2s_infinite]"></span>
              System Live
            </div>
            <button className="p-2 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
              <span className="text-xl">🔔</span>
            </button>
            <div className="h-8 w-8 rounded-full bg-slate-200 dark:bg-slate-700 flex items-center justify-center overflow-hidden">
              <span className="text-slate-400">👤</span>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-[1440px] mx-auto p-6 space-y-8">
        <header className="flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div>
            <h2 className="text-3xl font-bold tracking-tight">Agent Performance Dashboard</h2>
            <p className="text-slate-500 dark:text-slate-400 mt-1">Real-time status of the Multi-Agent Orchestrator</p>
          </div>
          <div className="flex gap-3">
            <button className="flex items-center gap-2 px-4 py-2 text-sm font-semibold rounded-lg border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors">
              <span className="text-lg">📅</span>
              Last 30 Days
            </button>
            <button className="flex items-center gap-2 px-4 py-2 text-sm font-semibold rounded-lg bg-indigo-500 text-white shadow-lg shadow-indigo-500/20 hover:opacity-90 transition-all">
              <span className="text-lg">📥</span>
              Export PDF
            </button>
          </div>
        </header>

        <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="relative overflow-hidden p-6 rounded-2xl bg-blue-600 text-white group cursor-pointer hover:shadow-2xl hover:shadow-blue-500/20 transition-all">
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:scale-110 transition-transform">
              <span className="text-6xl">👥</span>
            </div>
            <p className="text-blue-100 text-sm font-medium uppercase tracking-wider">Total Agents</p>
            <h3 className="text-4xl font-bold mt-2">{metrics.total_agents}</h3>
            <p className="text-blue-100/80 text-xs mt-4 flex items-center gap-1">
              <span className="text-sm">✓</span>
              All systems operational
            </p>
          </div>

          <div className="relative overflow-hidden p-6 rounded-2xl bg-emerald-600 text-white group cursor-pointer hover:shadow-2xl hover:shadow-emerald-500/20 transition-all">
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:scale-110 transition-transform">
              <span className="text-6xl">💬</span>
            </div>
            <p className="text-emerald-100 text-sm font-medium uppercase tracking-wider">Active Conversations</p>
            <h3 className="text-4xl font-bold mt-2">{metrics.active_conversations}</h3>
            <p className="text-emerald-100/80 text-xs mt-4 flex items-center gap-1">
              <span className="text-sm">📈</span>
              In-progress queries
            </p>
          </div>

          <div className="relative overflow-hidden p-6 rounded-2xl bg-purple-600 text-white group cursor-pointer hover:shadow-2xl hover:shadow-purple-500/20 transition-all">
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:scale-110 transition-transform">
              <span className="text-6xl">⚡️</span>
            </div>
            <p className="text-purple-100 text-sm font-medium uppercase tracking-wider">Avg Response Time</p>
            <h3 className="text-4xl font-bold mt-2">{metrics.avg_response_time}s</h3>
            <p className="text-purple-100/80 text-xs mt-4 flex items-center gap-1">
              <span className="text-sm">🔍</span>
              Multi-database optimized
            </p>
          </div>

          <div className="relative overflow-hidden p-6 rounded-2xl bg-orange-600 text-white group cursor-pointer hover:shadow-2xl hover:shadow-orange-500/20 transition-all">
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:scale-110 transition-transform">
              <span className="text-6xl">☁️</span>
            </div>
            <p className="text-orange-100 text-sm font-medium uppercase tracking-wider">System Uptime</p>
            <h3 className="text-4xl font-bold mt-2">{metrics.uptime}</h3>
            <p className="text-orange-100/80 text-xs mt-4 flex items-center gap-1">
              <span className="text-sm">📅</span>
              Past 30 days
            </p>
          </div>
        </section>

        <section className="space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-xl font-bold flex items-center gap-2">
              Sub-Agent Status
              <span className="text-xs font-normal px-2 py-0.5 bg-slate-100 dark:bg-slate-800 rounded-full text-slate-500">4 Active</span>
            </h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {agents.map((agent, idx) => (
              <div key={idx} className="bg-white/5 backdrop-blur-md border border-slate-200 dark:border-white/10 p-6 rounded-2xl hover:bg-white/10 dark:hover:bg-white/10 transition-all">
                <div className="flex items-start justify-between mb-6">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-white rounded-xl shadow-sm flex items-center justify-center text-2xl">
                      {agent.icon}
                    </div>
                    <div>
                      <h4 className="font-bold text-lg">{agent.name}</h4>
                      <p className="text-xs text-slate-500 dark:text-slate-400">{agent.queries_processed} queries processed</p>
                    </div>
                  </div>
                  <span className={`flex items-center gap-1.5 px-3 py-1 text-xs font-bold rounded-full uppercase tracking-tighter ${agent.status === 'ready' ? 'bg-green-500/10 text-green-500' :
                      agent.status === 'busy' ? 'bg-yellow-500/10 text-yellow-500' : 'bg-red-500/10 text-red-500'
                    }`}>
                    <span className={`w-1.5 h-1.5 rounded-full ${agent.status === 'ready' ? 'bg-green-500' :
                        agent.status === 'busy' ? 'bg-yellow-500' : 'bg-red-500'
                      }`}></span>
                    {agent.status}
                  </span>
                </div>
                <div className="grid grid-cols-3 gap-4 border-t border-slate-200 dark:border-slate-800 pt-4">
                  <div>
                    <p className="text-[10px] uppercase font-bold text-slate-400 mb-1">Queries/hr</p>
                    <p className="font-semibold">{Math.floor(agent.queries_processed / 24)}</p>
                  </div>
                  <div>
                    <p className="text-[10px] uppercase font-bold text-slate-400 mb-1">Avg Response</p>
                    <p className="font-semibold">{idx === 0 ? '1.2s' : idx === 1 ? '0.9s' : idx === 2 ? '0.5s' : '1.1s'}</p>
                  </div>
                  <div>
                    <p className="text-[10px] uppercase font-bold text-slate-400 mb-1">Error Rate</p>
                    <p className="font-semibold text-green-500">0.{idx}%</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="space-y-6">
          <h3 className="text-xl font-bold">Database Connections</h3>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {['Neon PostgreSQL', 'Vector Search DB', 'Warehouse API', 'Upstash Redis'].map((name, idx) => (
              <div key={idx} className="bg-white/5 backdrop-blur-md border border-slate-200 dark:border-white/10 p-5 rounded-2xl flex flex-col items-center text-center gap-3">
                <div className="w-10 h-10 bg-slate-100 dark:bg-slate-800 rounded-lg flex items-center justify-center mb-1">
                  <span className="text-indigo-500 text-2xl">
                    {idx === 0 ? '🗄️' : idx === 1 ? '🔍' : idx === 2 ? '🏭' : '⚡️'}
                  </span>
                </div>
                <div>
                  <div className="flex items-center justify-center gap-2 mb-1">
                    <span className="w-2 h-2 rounded-full bg-green-500 shadow-[0_0_0_0_rgba(34,197,94,0.7)] animate-[pulse_2s_infinite]"></span>
                    <span className="text-green-500 text-xs font-bold">CONNECTED</span>
                  </div>
                  <p className="text-sm font-medium">{name}</p>
                </div>
              </div>
            ))}
          </div>
        </section>
      </main>

      <footer className="mt-12 py-8 border-t border-slate-200 dark:border-slate-800 text-center">
        <p className="text-sm text-slate-500 dark:text-slate-400">Powered by LangGraph • Google ADK • Neon PostgreSQL • Next.js</p>
      </footer>

      <style jsx global>{`
        @keyframes pulse {
          0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7); }
          70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(34, 197, 94, 0); }
          100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }
        }
      `}</style>
    </div>
  );
}
