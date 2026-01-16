'use client';

import React, { useState, useRef, useEffect } from 'react';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: string;
  agents?: string[];
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [wsConnected, setWsConnected] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;

  const connectWebSocket = () => {
    try {
      const websocket = new WebSocket('ws://localhost:8000/ws/chat');

      websocket.onopen = () => {
        console.log('✓ WebSocket connected');
        setWsConnected(true);
        wsRef.current = websocket;
        reconnectAttempts.current = 0;
      };

      websocket.onmessage = (event) => {
        try {
          const response = JSON.parse(event.data);

          if (response.type === 'response') {
            const assistantMessage: Message = {
              id: `msg-${Date.now()}`,
              type: 'assistant',
              content: response.narrative || response.narrative_response || 'No response received',
              timestamp: response.timestamp || new Date().toISOString(),
              agents: response.agents_used || response.agents_invoked
            };

            setMessages(prev => [...prev, assistantMessage]);
            setLoading(false);
          } else if (response.type === 'error') {
            const errorMessage: Message = {
              id: `msg-${Date.now()}`,
              type: 'assistant',
              content: `Error: ${response.message || 'An error occurred'}`,
              timestamp: new Date().toISOString()
            };
            setMessages(prev => [...prev, errorMessage]);
            setLoading(false);
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
          setLoading(false);
        }
      };

      websocket.onerror = (error) => {
        console.error('WebSocket error:', error);
        setWsConnected(false);
      };

      websocket.onclose = () => {
        console.log('WebSocket closed');
        setWsConnected(false);
        wsRef.current = null;

        if (reconnectAttempts.current < maxReconnectAttempts) {
          reconnectAttempts.current += 1;
          const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 10000);
          console.log(`Reconnecting in ${delay}ms (attempt ${reconnectAttempts.current})...`);

          reconnectTimeoutRef.current = setTimeout(() => {
            connectWebSocket();
          }, delay);
        }
      };
    } catch (error) {
      console.error('Failed to create WebSocket:', error);
      setWsConnected(false);
    }
  };

  useEffect(() => {
    connectWebSocket();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async () => {
    if (!input.trim() || loading) return;

    const query = input.trim();
    setInput('');
    setLoading(true);

    const userMessage: Message = {
      id: `msg-${Date.now()}`,
      type: 'user',
      content: query,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);

    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      try {
        wsRef.current.send(JSON.stringify({
          query: query,
          user_id: 1
        }));
      } catch (error) {
        console.error('WebSocket send error:', error);
        await sendViaRestAPI(query);
      }
    } else {
      await sendViaRestAPI(query);
    }
  };

  const handleNewChat = async () => {
    // 1. Clear local UI messages
    setMessages([]);
    setInput('');

    // 2. Send 'reset' command to backend to wipe session memory
    const resetQuery = 'reset';
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        query: resetQuery,
        user_id: 1
      }));
    } else {
      await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: resetQuery, user_id: 1 })
      });
    }
    console.log('✓ Session reset triggered');
  };

  const sendViaRestAPI = async (query: string) => {
    try {
      const response = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query,
          user_id: 1
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      const assistantMessage: Message = {
        id: `msg-${Date.now()}`,
        type: 'assistant',
        content: data.narrative_response || 'No response received',
        timestamp: data.timestamp || new Date().toISOString(),
        agents: data.agents_invoked || []
      };

      setMessages(prev => [...prev, assistantMessage]);
      setLoading(false);
    } catch (error) {
      console.error('REST API error:', error);
      const errorMessage: Message = {
        id: `msg-${Date.now()}`,
        type: 'assistant',
        content: `Error: Failed to get response. ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const suggestedPrompts = [
    { icon: '🎧', text: '"Where is my Wireless Noise-Canceling Headphones?"', desc: 'Track current shipment status' },
    { icon: '💳', text: '"Check wallet for Order 2"', desc: 'Verify payment and balance' },
    { icon: '🎫', text: '"Check support ticket for Order 5"', desc: 'View updates on active cases' }
  ];

  return (
    <div className="flex flex-col h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 transition-colors duration-300 overflow-hidden">
      <div className="fixed inset-0 pointer-events-none overflow-hidden opacity-0 dark:opacity-100">
        <div className="absolute -top-24 -left-24 w-96 h-96 bg-teal-600/20 rounded-full blur-[100px] animate-pulse"></div>
        <div className="absolute top-1/2 -right-24 w-80 h-80 bg-emerald-500/10 rounded-full blur-[100px] animate-pulse" style={{ animationDelay: '1s' }}></div>
        <div className="absolute bottom-0 left-1/3 w-[500px] h-[500px] bg-teal-600/10 rounded-full blur-[100px] animate-pulse" style={{ animationDelay: '2s' }}></div>
      </div>

      <header className="relative flex items-center justify-between px-8 h-20 border-b border-slate-200 dark:border-white/5 bg-white/50 dark:bg-black/20 backdrop-blur-md z-10">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-teal-600 to-emerald-500 flex items-center justify-center shadow-lg shadow-teal-600/20">
            <span className="text-white text-2xl">🤖</span>
          </div>
          <div>
            <h1 className="font-bold text-xl tracking-tight leading-none">Omni-Retail Assistant</h1>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 font-medium tracking-wide uppercase">Multi-Agent Support System</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <button
            onClick={handleNewChat}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-200 dark:bg-white/5 border border-slate-300 dark:border-white/10 hover:bg-teal-600/10 hover:border-teal-600/20 transition-all text-sm font-semibold text-slate-600 dark:text-slate-300 hover:text-teal-600 dark:hover:text-teal-400"
          >
            <span>✨</span> New Chat
          </button>

          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20">
            <span className="relative flex h-2 w-2">
              {wsConnected && <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>}
              <span className={`relative inline-flex rounded-full h-2 w-2 ${wsConnected ? 'bg-emerald-500' : 'bg-red-500'}`}></span>
            </span>
            <span className="text-xs font-semibold text-emerald-600 dark:text-emerald-400">{wsConnected ? 'Connected' : 'Disconnected'}</span>
          </div>
        </div>
      </header>

      <main className="relative flex-1 flex flex-col items-center justify-center p-6 overflow-y-auto z-10">
        {messages.length === 0 ? (
          <div className="max-w-2xl w-full text-center space-y-12">
            <div className="space-y-4">
              <h2 className="text-4xl md:text-5xl font-extrabold text-slate-900 dark:text-white tracking-tight">
                Welcome to <span className="text-transparent bg-clip-text bg-gradient-to-r from-teal-600 to-emerald-500">Omni-Retail Support</span>
              </h2>
              <p className="text-lg text-slate-500 dark:text-slate-400 max-w-lg mx-auto leading-relaxed">
                Ask me anything about your orders, shipments, refunds, or support tickets.
              </p>
            </div>
            <div className="grid grid-cols-1 gap-4 w-full">
              {suggestedPrompts.map((prompt, idx) => (
                <button
                  key={idx}
                  onClick={() => setInput(prompt.text.replace(/"/g, ''))}
                  className="group flex items-center gap-4 p-5 rounded-2xl transition-all duration-300 text-left border border-slate-200 dark:border-white/5 hover:border-teal-600/40 bg-white/70 dark:bg-white/5 backdrop-blur-md hover:transform hover:-translate-y-1"
                >
                  <div className="flex-shrink-0 w-12 h-12 rounded-xl bg-teal-600/10 flex items-center justify-center group-hover:scale-110 transition-transform text-2xl">
                    {prompt.icon}
                  </div>
                  <div className="flex-grow">
                    <span className="text-slate-900 dark:text-white font-medium block">{prompt.text}</span>
                    <span className="text-sm text-slate-500 dark:text-slate-400">{prompt.desc}</span>
                  </div>
                  <span className="text-slate-300 dark:text-white/20 group-hover:text-teal-600 transition-colors text-2xl">→</span>
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="w-full max-w-4xl space-y-4">
            {messages.map(msg => (
              <div
                key={msg.id}
                className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-xl px-5 py-4 rounded-2xl backdrop-blur-md ${msg.type === 'user'
                    ? 'bg-gradient-to-r from-teal-600 to-emerald-500 text-white rounded-br-none shadow-lg shadow-teal-600/20'
                    : 'bg-white/70 dark:bg-white/5 text-slate-900 dark:text-gray-100 rounded-bl-none border border-slate-200 dark:border-white/10'
                    }`}
                >
                  <p className="text-sm whitespace-pre-wrap leading-relaxed">{msg.content}</p>

                  {msg.agents && msg.agents.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-white/20 flex flex-wrap gap-2">
                      {msg.agents.map(agent => (
                        <span
                          key={agent}
                          className="text-xs bg-white/20 dark:bg-white/10 px-3 py-1 rounded-full font-medium"
                        >
                          {agent}
                        </span>
                      ))}
                    </div>
                  )}

                  <p className="text-xs opacity-60 mt-2">
                    {new Date(msg.timestamp).toLocaleTimeString()}
                  </p>
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex justify-start">
                <div className="bg-white/70 dark:bg-white/5 backdrop-blur-md px-5 py-4 rounded-2xl border border-slate-200 dark:border-white/10">
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 bg-teal-600 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-teal-600 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-teal-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        )}
      </main>

      <footer className="relative p-6 md:p-10 w-full flex justify-center z-10">
        <div className="max-w-4xl w-full">
          <div className="bg-white/70 dark:bg-white/5 backdrop-blur-md rounded-2xl p-2 flex items-center gap-3 shadow-2xl shadow-slate-200 dark:shadow-black/50 border border-slate-200 dark:border-white/10 focus-within:ring-2 focus-within:ring-teal-600/40 transition-all">
            <div className="hidden sm:flex items-center justify-center w-10 h-10 rounded-xl bg-slate-100 dark:bg-white/5 text-slate-400 dark:text-white/40 ml-1 text-2xl">
              💬
            </div>
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              className="flex-1 bg-transparent border-none focus:ring-0 focus:outline-none text-slate-800 dark:text-white placeholder-slate-400 dark:placeholder-white/30 text-base py-3 px-2"
              placeholder="Ask about your order, shipment, refund, or support ticket..."
              disabled={loading}
              type="text"
            />
            <button
              onClick={handleSendMessage}
              disabled={loading || !input.trim()}
              className="bg-gradient-to-r from-teal-600 to-emerald-500 hover:from-teal-600/90 hover:to-emerald-500/90 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-3 px-6 rounded-xl flex items-center gap-2 transition-all active:scale-95 shadow-lg shadow-teal-600/20"
            >
              <span className="hidden sm:inline">Send Message</span>
              <span className="text-xl">{loading ? '⏳' : '📤'}</span>
            </button>
          </div>
          <p className="text-center text-[10px] uppercase tracking-[0.2em] font-bold text-slate-400 dark:text-white/20 mt-4">
            AI agent might provide automated information. please verify critical details.
          </p>
        </div>
      </footer>

      <div className="fixed bottom-6 right-6 z-50">
        <button className="w-12 h-12 rounded-full bg-white/70 dark:bg-white/5 backdrop-blur-md flex items-center justify-center text-slate-600 dark:text-slate-400 hover:text-teal-600 dark:hover:text-teal-600 transition-colors shadow-lg border border-slate-200 dark:border-white/10 text-2xl">
          ⚙️
        </button>
      </div>
    </div>
  );
}
