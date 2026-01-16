'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

interface VoiceMessage {
  id: string;
  type: 'user' | 'assistant';
  text: string;
  timestamp: string;
}

export default function VoicePage() {
  const [messages, setMessages] = useState<VoiceMessage[]>([]);
  const [isListening, setIsListening] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [transcript, setTranscript] = useState('');
  const recognitionRef = useRef<any>(null);
  const ws = useRef<WebSocket | null>(null);
  const synthesisRef = useRef<SpeechSynthesisUtterance | null>(null);

  // Initialize WebSocket and Speech APIs
  useEffect(() => {
    // WebSocket connection
    ws.current = new WebSocket('ws://localhost:8000/ws/voice');
    
    ws.current.onmessage = (event) => {
      const response = JSON.parse(event.data);
      
      if (response.type === 'voice_response') {
        const assistantMessage: VoiceMessage = {
          id: `msg-${Date.now()}`,
          type: 'assistant',
          text: response.text,
          timestamp: response.timestamp
        };
        
        setMessages(prev => [...prev, assistantMessage]);
        
        // Speak the response
        speakText(response.text);
        setIsProcessing(false);
      }
    };

    // Speech Recognition
    const SpeechRecognition = (window as any).SpeechRecognition || 
                            (window as any).webkitSpeechRecognition;
    
    if (SpeechRecognition) {
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.language = 'en-US';
      
      recognitionRef.current.onstart = () => {
        setIsListening(true);
        setTranscript('');
      };
      
      recognitionRef.current.onresult = (event: any) => {
        let interim = '';
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcriptSegment = event.results[i][0].transcript;
          
          if (event.results[i].isFinal) {
            interim += transcriptSegment + ' ';
          } else {
            interim += transcriptSegment;
          }
        }
        
        setTranscript(interim);
      };
      
      recognitionRef.current.onend = () => {
        setIsListening(false);
      };
      
      recognitionRef.current.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error);
      };
    }

    return () => {
      if (ws.current) ws.current.close();
    };
  }, []);

  const speakText = (text: string) => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      
      synthesisRef.current = new SpeechSynthesisUtterance(text);
      synthesisRef.current.rate = 0.9;
      synthesisRef.current.pitch = 1;
      
      window.speechSynthesis.speak(synthesisRef.current);
    }
  };

  const handleStartListening = () => {
    if (recognitionRef.current && !isListening) {
      recognitionRef.current.start();
    }
  };

  const handleStopListening = () => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
    }
  };

  const handleSendVoiceQuery = () => {
    if (!transcript.trim() || !ws.current) return;

    // Add user message
    const userMessage: VoiceMessage = {
      id: `msg-${Date.now()}`,
      type: 'user',
      text: transcript,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setTranscript('');
    setIsProcessing(true);

    // Send to backend
    ws.current.send(JSON.stringify({
      transcription: userMessage.text,
      user_id: 1
    }));
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-purple-900 to-purple-800">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-700 to-purple-800 text-white p-6 shadow-lg">
        <h1 className="text-3xl font-bold">🎤 Voice Assistant</h1>
        <p className="text-purple-200 mt-2">Speak naturally to query your orders and shipments</p>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center text-gray-300">
              <div className="text-6xl mb-4">🎙️</div>
              <h2 className="text-2xl font-bold mb-4">Ready to Help!</h2>
              <p className="mb-8">Click the microphone below and ask your question</p>
              <div className="bg-purple-700 p-4 rounded-lg">
                <p className="text-sm">Try saying: <span className="font-semibold text-purple-300">&quot;Where is my Gaming Monitor?&quot;</span></p>
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
                className={`max-w-2xl px-4 py-3 rounded-lg ${
                  msg.type === 'user'
                    ? 'bg-purple-600 text-white rounded-br-none'
                    : 'bg-purple-700 text-purple-100 rounded-bl-none'
                }`}
              >
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-sm font-semibold">
                    {msg.type === 'user' ? '🗣️ You' : '🤖 Assistant'}
                  </span>
                </div>
                <p className="text-base leading-relaxed">{msg.text}</p>
                <p className="text-xs opacity-70 mt-1">
                  {new Date(msg.timestamp).toLocaleTimeString()}
                </p>
              </div>
            </div>
          ))
        )}

        {isProcessing && (
          <div className="flex justify-start">
            <div className="bg-purple-700 px-6 py-4 rounded-lg">
              <div className="flex items-center gap-2">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-purple-300 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-purple-300 rounded-full animate-bounce delay-100"></div>
                  <div className="w-2 h-2 bg-purple-300 rounded-full animate-bounce delay-200"></div>
                </div>
                <span className="text-purple-200 text-sm">Processing your query...</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Voice Input Controls */}
      <div className="bg-purple-800 border-t border-purple-700 p-6 shadow-xl">
        {/* Transcript Display */}
        {transcript && (
          <div className="bg-purple-700 p-4 rounded-lg mb-4">
            <p className="text-purple-200 text-sm font-semibold mb-1">Hearing:</p>
            <p className="text-white">{transcript}</p>
          </div>
        )}

        {/* Control Buttons */}
        <div className="flex gap-4 justify-center">
          {!isListening ? (
            <Button
              onClick={handleStartListening}
              disabled={isProcessing}
              className="bg-red-600 hover:bg-red-700 text-white px-8 py-3 text-lg"
            >
              🎙️ Start Listening
            </Button>
          ) : (
            <Button
              onClick={handleStopListening}
              className="bg-red-700 hover:bg-red-800 text-white px-8 py-3 text-lg animate-pulse"
            >
              🔴 Stop
            </Button>
          )}

          {transcript && (
            <Button
              onClick={handleSendVoiceQuery}
              disabled={isProcessing}
              className="bg-purple-600 hover:bg-purple-700 text-white px-8 py-3 text-lg"
            >
              📤 Send
            </Button>
          )}

          <Button
            onClick={() => setTranscript('')}
            variant="outline"
            className="border-purple-500 text-purple-300 hover:bg-purple-700"
          >
            🗑️ Clear
          </Button>
        </div>
      </div>

      {/* Status Indicator */}
      <div className="bg-purple-900 text-purple-200 px-6 py-2 text-center text-xs">
        {isListening ? '🎤 Listening...' : isProcessing ? '⚙️ Processing...' : '✓ Ready'}
      </div>
    </div>
  );
}
