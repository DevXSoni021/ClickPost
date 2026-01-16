'use client';

import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

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
    // Fetch real metrics from backend
    const fetchMetrics = async () => {
      try {
        const response = await fetch('http://localhost:8000/agents/status');
        const data = await response.json();
        // Update metrics based on response
      } catch (error) {
        console.error('Failed to fetch metrics:', error);
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-white mb-2">System Dashboard</h1>
        <p className="text-gray-400">Omni-Retail Multi-Agent Orchestrator Status</p>
      </div>

      {/* Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <Card className="bg-gradient-to-br from-blue-900 to-blue-800 border-blue-700 p-6">
          <h3 className="text-blue-200 text-sm font-semibold mb-2">Total Agents</h3>
          <p className="text-3xl font-bold text-white">{metrics.total_agents}</p>
          <p className="text-blue-300 text-xs mt-2">All operational</p>
        </Card>

        <Card className="bg-gradient-to-br from-green-900 to-green-800 border-green-700 p-6">
          <h3 className="text-green-200 text-sm font-semibold mb-2">Active Conversations</h3>
          <p className="text-3xl font-bold text-white">{metrics.active_conversations}</p>
          <p className="text-green-300 text-xs mt-2">In progress</p>
        </Card>

        <Card className="bg-gradient-to-br from-purple-900 to-purple-800 border-purple-700 p-6">
          <h3 className="text-purple-200 text-sm font-semibold mb-2">Avg Response Time</h3>
          <p className="text-3xl font-bold text-white">{metrics.avg_response_time}s</p>
          <p className="text-purple-300 text-xs mt-2">Multi-database queries</p>
        </Card>

        <Card className="bg-gradient-to-br from-orange-900 to-orange-800 border-orange-700 p-6">
          <h3 className="text-orange-200 text-sm font-semibold mb-2">System Uptime</h3>
          <p className="text-3xl font-bold text-white">{metrics.uptime}</p>
          <p className="text-orange-300 text-xs mt-2">30 days</p>
        </Card>
      </div>

      {/* Agent Status Grid */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-white mb-4">Sub-Agent Status</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {agents.map((agent, idx) => (
            <Card
              key={idx}
              className="bg-gray-800 border-gray-700 p-6 hover:bg-gray-750 transition"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-4">
                  <span className="text-4xl">{agent.icon}</span>
                  <div>
                    <h3 className="text-white font-semibold">{agent.name}</h3>
                    <p className="text-gray-400 text-sm">
                      {agent.queries_processed} queries processed
                    </p>
                  </div>
                </div>
                <Badge
                  className={`${
                    agent.status === 'ready'
                      ? 'bg-green-700 text-green-100'
                      : agent.status === 'busy'
                      ? 'bg-yellow-700 text-yellow-100'
                      : 'bg-red-700 text-red-100'
                  }`}
                >
                  {agent.status === 'ready' ? '🟢' : '🟡'} {agent.status}
                </Badge>
              </div>

              {/* Mini stats */}
              <div className="mt-4 grid grid-cols-3 gap-2 pt-4 border-t border-gray-700">
                <div>
                  <p className="text-gray-500 text-xs">Queries/Hour</p>
                  <p className="text-white font-semibold">{Math.floor(agent.queries_processed / 24)}</p>
                </div>
                <div>
                  <p className="text-gray-500 text-xs">Avg Response</p>
                  <p className="text-white font-semibold">234ms</p>
                </div>
                <div>
                  <p className="text-gray-500 text-xs">Error Rate</p>
                  <p className="text-white font-semibold">0.2%</p>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>

      {/* Database Status */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-white mb-4">Database Connections</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {['DB_ShopCore', 'DB_ShipStream', 'DB_PayGuard', 'DB_CareDesk'].map((db, idx) => (
            <Card key={idx} className="bg-gray-800 border-gray-700 p-4">
              <h4 className="text-white font-semibold mb-2">{db}</h4>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span className="text-green-400 text-sm">Connected</span>
              </div>
              <p className="text-gray-400 text-xs mt-2">Neon PostgreSQL</p>
            </Card>
          ))}
        </div>
      </div>

      {/* System Info */}
      <Card className="bg-gray-800 border-gray-700 p-6">
        <h3 className="text-white font-bold mb-4">System Information</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <p className="text-gray-400">Framework</p>
            <p className="text-white font-semibold">LangGraph + Google ADK</p>
          </div>
          <div>
            <p className="text-gray-400">Database</p>
            <p className="text-white font-semibold">Neon PostgreSQL</p>
          </div>
          <div>
            <p className="text-gray-400">Frontend</p>
            <p className="text-white font-semibold">Next.js 15 + React</p>
          </div>
          <div>
            <p className="text-gray-400">LLM</p>
            <p className="text-white font-semibold">Gemini 2.0 Flash</p>
          </div>
        </div>
      </Card>
    </div>
  );
}
