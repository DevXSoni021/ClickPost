'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: string;
  agents?: string[];
}

interface QueryResponse {
  timestamp: string;
  query: string;
  agents_invoked: string[];
  narrative_response: string;
  data_sources: Record<string, any>;
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

  // Initialize WebSocket connection with reconnection logic
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
        
        // Attempt to reconnect
        if (reconnectAttempts.current < maxReconnectAttempts) {
          reconnectAttempts.current += 1;
          const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 10000);
          console.log(`Reconnecting in ${delay}ms (attempt ${reconnectAttempts.current})...`);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            connectWebSocket();
          }, delay);
        } else {
          console.error('Max reconnection attempts reached. Falling back to REST API.');
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

  // Auto-scroll to latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async () => {
    if (!input.trim() || loading) return;

    const query = input.trim();
    setInput('');
    setLoading(true);

    // Add user message immediately
    const userMessage: Message = {
      id: `msg-${Date.now()}`,
      type: 'user',
      content: query,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);

    // Try WebSocket first, fallback to REST API
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      try {
        wsRef.current.send(JSON.stringify({
          query: query,
          user_id: 1
        }));
      } catch (error) {
        console.error('WebSocket send error:', error);
        // Fallback to REST API
        await sendViaRestAPI(query);
      }
    } else {
      // Use REST API if WebSocket is not available
      await sendViaRestAPI(query);
    }
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

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-slate-900 to-slate-800">
      {/* Header */}
      <div className="bg-gradient-to-r from-teal-600 to-teal-700 text-white p-6 shadow-lg">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">🤖 Omni-Retail Assistant</h1>
            <p className="text-teal-100 mt-2">Multi-Agent Customer Support System</p>
          </div>
          <div className="flex items-center gap-2">
            <div className={`w-3 h-3 rounded-full ${wsConnected ? 'bg-green-400' : 'bg-red-400'} animate-pulse`}></div>
            <span className="text-sm">{wsConnected ? 'Connected' : 'Disconnected'}</span>
          </div>
        </div>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center text-gray-400">
              <h2 className="text-2xl font-bold mb-4">Welcome to Omni-Retail Support</h2>
              <p className="mb-6">Ask me about your orders, shipments, refunds, or support tickets!</p>
              <div className="space-y-3 text-left max-w-md mx-auto">
                <div className="bg-slate-700 p-4 rounded-lg">
                  <p className="font-semibold text-teal-400">📦 &quot;Where is my Gaming Monitor?&quot;</p>
                </div>
                <div className="bg-slate-700 p-4 rounded-lg">
                  <p className="font-semibold text-teal-400">💳 &quot;What&apos;s the status of my refund?&quot;</p>
                </div>
                <div className="bg-slate-700 p-4 rounded-lg">
                  <p className="font-semibold text-teal-400">🎫 &quot;Can you check my support ticket?&quot;</p>
                </div>
              </div>
            </div>
          </div>
        ) : (
          messages.map(msg => (
            <div
              key={msg.id}
              className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-xl px-4 py-3 rounded-lg ${
                  msg.type === 'user'
                    ? 'bg-teal-600 text-white rounded-br-none'
                    : 'bg-slate-700 text-gray-100 rounded-bl-none'
                }`}
              >
                <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                
                {msg.agents && msg.agents.length > 0 && (
                  <div className="mt-2 pt-2 border-t border-slate-600 flex flex-wrap gap-1">
                    {msg.agents.map(agent => (
                      <span
                        key={agent}
                        className="text-xs bg-slate-600 px-2 py-1 rounded text-teal-300"
                      >
                        {agent}
                      </span>
                    ))}
                  </div>
                )}
                
                <p className="text-xs opacity-70 mt-1">
                  {new Date(msg.timestamp).toLocaleTimeString()}
                </p>
              </div>
            </div>
          ))
        )}
        
        {loading && (
          <div className="flex justify-start">
            <div className="bg-slate-700 px-4 py-3 rounded-lg">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-teal-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-teal-400 rounded-full animate-bounce delay-100"></div>
                <div className="w-2 h-2 bg-teal-400 rounded-full animate-bounce delay-200"></div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="bg-slate-800 border-t border-slate-700 p-4 shadow-xl">
        <div className="flex gap-3">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about your order, shipment, refund, or support ticket..."
            className="flex-1 bg-slate-700 text-white border-slate-600 placeholder-gray-400 focus:border-teal-500 focus:ring-teal-500"
            disabled={loading}
          />
          <Button
            onClick={handleSendMessage}
            disabled={loading || !input.trim()}
            className="bg-teal-600 hover:bg-teal-700 text-white px-6"
          >
            {loading ? '⏳' : '📤'} Send
          </Button>
        </div>
      </div>
    </div>
  );
}
