'use client';

import React, { useState, useRef, useEffect } from 'react';

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

  useEffect(() => {
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
        speakText(response.text);
        setIsProcessing(false);
      }
    };

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
        setIsListening(false);
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
      setTranscript('');
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

    const userMessage: VoiceMessage = {
      id: `msg-${Date.now()}`,
      type: 'user',
      text: transcript,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);

    setIsProcessing(true);

    ws.current.send(JSON.stringify({
      transcription: userMessage.text,
      user_id: 1
    }));

    // Clear transcript after sending
    setTranscript('');
  };

  const handleClear = () => {
    setTranscript('');
    setMessages([]);
    window.speechSynthesis.cancel();
  };

  return (
    <div className="bg-slate-50 dark:bg-[#120B2E] text-slate-900 dark:text-white min-h-screen overflow-hidden transition-colors duration-500 font-sans">
      <nav className="fixed top-0 w-full z-50 px-8 py-6 flex justify-between items-center bg-transparent">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-violet-500 rounded-xl flex items-center justify-center text-white shadow-lg shadow-violet-500/20">
            <span className="text-2xl">🎤</span>
          </div>
          <span className="font-extrabold text-xl tracking-tight text-slate-900 dark:text-white">Omni-Retail</span>
        </div>
        <div className="flex gap-4">
          <button className="p-2 rounded-full hover:bg-slate-200 dark:hover:bg-white/10 transition-colors">
            <span className="text-xl">⚙️</span>
          </button>
          <button className="p-2 rounded-full hover:bg-slate-200 dark:hover:bg-white/10 transition-colors">
            <span className="text-xl">👤</span>
          </button>
        </div>
      </nav>

      <main className="relative h-screen flex flex-col items-center justify-center px-4 overflow-hidden">
        {/* Background Effects */}
        <div className="absolute inset-0 z-0 pointer-events-none">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-violet-600/20 rounded-full blur-[120px] animate-pulse" style={{ animationDuration: '4s' }}></div>
          <div className="absolute bottom-1/4 right-1/4 w-[500px] h-[500px] bg-blue-500/10 rounded-full blur-[150px] animate-bounce" style={{ animationDuration: '6s' }}></div>
        </div>

        <div className="relative z-10 w-full max-w-2xl flex flex-col items-center text-center">
          {messages.length === 0 && !transcript ? (
            <div className="mb-12 space-y-2">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-violet-500/10 text-violet-500 text-xs font-bold uppercase tracking-widest mb-4">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-violet-500 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-violet-500"></span>
                </span>
                AI Assistant Active
              </div>
              <h1 className="text-5xl md:text-6xl font-extrabold tracking-tight text-slate-900 dark:text-white">
                Voice Assistant
              </h1>
              <p className="text-slate-500 dark:text-slate-400 text-lg font-medium">
                Speak naturally to query your orders and shipments
              </p>
            </div>
          ) : (
            <div className="mb-8 w-full h-[300px] overflow-y-auto px-4 space-y-4 scrollbar-hide">
              {messages.map((msg) => (
                <div key={msg.id} className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-md px-6 py-4 rounded-2xl backdrop-blur-md text-left ${msg.type === 'user'
                      ? 'bg-violet-600 text-white rounded-br-none'
                      : 'bg-white/10 text-white rounded-bl-none border border-white/10'
                    }`}>
                    <p className="leading-relaxed">{msg.text}</p>
                  </div>
                </div>
              ))}
              {transcript && (
                <div className="flex justify-center mt-4">
                  <div className="bg-white/5 backdrop-blur-md border border-white/10 px-6 py-3 rounded-full flex items-center gap-3">
                    <div className="flex gap-1 h-3 items-center">
                      <div className="w-1 bg-violet-400 h-full animate-pulse"></div>
                      <div className="w-1 bg-violet-400 h-2/3 animate-pulse delay-75"></div>
                      <div className="w-1 bg-violet-400 h-full animate-pulse delay-150"></div>
                    </div>
                    <span className="text-slate-300 italic">{transcript}</span>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Voice Orb */}
          <div
            className="relative group cursor-pointer mb-16 transition-transform duration-300 active:scale-95"
            onClick={isListening ? handleStopListening : handleStartListening}
          >
            {isListening && <div className="absolute inset-0 bg-violet-500/30 rounded-full scale-150 blur-xl animate-pulse"></div>}

            <div className={`relative w-48 h-48 rounded-full flex items-center justify-center transition-all duration-500 ${isListening
                ? 'bg-gradient-to-br from-red-500 to-red-600 shadow-[0_0_60px_rgba(239,68,68,0.4)] scale-110'
                : 'bg-[radial-gradient(circle_at_30%_30%,#a78bfa,#7c3aed)] shadow-[0_0_60px_rgba(139,92,246,0.4)] hover:scale-105'
              }`}>
              <span className="text-6xl text-white">
                {isListening ? '⏹' : '🎤'}
              </span>
            </div>

            {/* Sound Waves */}
            {isListening && (
              <div className="absolute -bottom-8 left-1/2 -translate-x-1/2 flex items-center gap-1">
                {[...Array(5)].map((_, i) => (
                  <div
                    key={i}
                    className="w-1 bg-violet-500 rounded-full animate-[wave_1s_ease-in-out_infinite]"
                    style={{
                      height: `${Math.random() * 24 + 12}px`,
                      animationDelay: `${i * 0.1}s`
                    }}
                  ></div>
                ))}
              </div>
            )}

            {/* Processing Indicator */}
            {isProcessing && !isListening && (
              <div className="absolute -bottom-12 left-1/2 -translate-x-1/2 flex items-center gap-2 whitespace-nowrap">
                <div className="w-2 h-2 bg-violet-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-violet-400 rounded-full animate-bounce delay-100"></div>
                <div className="w-2 h-2 bg-violet-400 rounded-full animate-bounce delay-200"></div>
                <span className="text-violet-300 text-sm font-medium">Processing...</span>
              </div>
            )}
          </div>

          {!messages.length && !transcript && (
            <div className="space-y-4 w-full max-w-md">
              <div className="space-y-2">
                <h2 className="text-3xl font-bold text-slate-900 dark:text-white">Ready to Help!</h2>
                <p className="text-slate-500 dark:text-slate-400">Click the microphone above and ask your question</p>
              </div>
              <button
                onClick={() => setTranscript("Where is my Gaming Monitor?")} // Simulates speaking
                className="w-full bg-white/5 backdrop-blur-md hover:bg-white/10 transition-all border border-white/10 py-4 px-6 rounded-2xl flex items-center justify-between group"
              >
                <div className="flex items-center gap-3 text-left">
                  <span className="text-violet-400 font-bold">Try saying:</span>
                  <span className="text-slate-700 dark:text-slate-200 italic">"Where is my Gaming Monitor?"</span>
                </div>
                <span className="text-violet-400 opacity-0 group-hover:opacity-100 transition-opacity">→</span>
              </button>
            </div>
          )}
        </div>
      </main>

      <footer className="fixed bottom-0 w-full p-8 z-50">
        <div className="max-w-4xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="hidden md:flex items-center gap-2 text-slate-500 dark:text-slate-400 text-sm">
            <span className="text-green-500 text-base">✓</span>
            System ready for input
          </div>
          <div className="flex items-center gap-4 w-full md:w-auto">
            <button
              onClick={handleClear}
              className="flex-1 md:flex-none px-8 py-4 rounded-2xl bg-white dark:bg-white/5 border border-slate-200 dark:border-white/10 font-bold flex items-center justify-center gap-2 hover:bg-slate-50 dark:hover:bg-white/10 transition-all text-slate-900 dark:text-white"
            >
              <span className="text-slate-400">🗑️</span>
              Clear
            </button>

            {transcript && !isListening && !isProcessing && (
              <button
                onClick={handleSendVoiceQuery}
                className="flex-1 md:flex-none px-12 py-4 rounded-2xl bg-violet-600 text-white font-bold flex items-center justify-center gap-2 shadow-2xl shadow-violet-600/40 hover:scale-[1.02] active:scale-[0.98] transition-all"
              >
                <span>📤</span>
                Send Query
              </button>
            )}

            {(!transcript || isListening) && (
              <button
                onClick={isListening ? handleStopListening : handleStartListening}
                className={`flex-1 md:flex-none px-12 py-4 rounded-2xl font-bold flex items-center justify-center gap-2 shadow-2xl transition-all hover:scale-[1.02] active:scale-[0.98] ${isListening
                    ? 'bg-red-500 text-white shadow-red-500/40'
                    : 'bg-violet-600 text-white shadow-violet-600/40'
                  }`}
              >
                <span>{isListening ? '⏹' : '🎤'}</span>
                {isListening ? 'Stop Listening' : 'Start Listening'}
              </button>
            )}
          </div>
          <div className="hidden md:block">
            <div className="text-xs text-slate-400 dark:text-slate-500 text-right">
              Powered by Omni-Engine v2.4<br />
              <span className="font-mono">Lat: 24ms • Quality: High</span>
            </div>
          </div>
        </div>
      </footer>

      <div className="fixed top-8 left-1/2 -translate-x-1/2 px-4 py-2 bg-white/5 backdrop-blur-md rounded-full text-[10px] font-bold tracking-[0.2em] uppercase text-slate-400 dark:text-slate-500 z-50 border border-white/5">
        SECURE VOICE CHANNEL
      </div>

      <style jsx global>{`
        @keyframes wave {
          0%, 100% { transform: scaleY(0.5); opacity: 0.5; }
          50% { transform: scaleY(1.2); opacity: 1; }
        }
      `}</style>
    </div>
  );
}
