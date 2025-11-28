'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, User } from 'lucide-react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
}

interface SimpleChatProps {
  onClose?: () => void;
}

export default function SimpleChat({ onClose }: SimpleChatProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  
  const [userId] = useState(() => {
    if (typeof window !== 'undefined') {
      let uid = localStorage.getItem('user_id');
      if (!uid) {
        uid = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        localStorage.setItem('user_id', uid);
      }
      return uid;
    }
    return 'default_user';
  });

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Focus input on mount
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  const handleSend = async () => {
    if (!input.trim() || isGenerating) return;

    const userMessage: Message = {
      role: 'user',
      content: input.trim(),
      timestamp: Date.now()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsGenerating(true);

    // Add placeholder for assistant response
    const assistantMessage: Message = {
      role: 'assistant',
      content: '',
      timestamp: Date.now()
    };
    setMessages(prev => [...prev, assistantMessage]);

    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      
      // Use the free-form chat endpoint
      const response = await fetch(`${API_URL}/api/chat/free`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          messages: messages.map(m => ({
            role: m.role,
            content: m.content
          })),
          user_message: userMessage.content
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('No response body');
      }

      let fullResponse = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.chunk) {
                fullResponse += data.chunk;
                // Update the last message with accumulated content
                setMessages(prev => {
                  const newMessages = [...prev];
                  newMessages[newMessages.length - 1] = {
                    ...newMessages[newMessages.length - 1],
                    content: fullResponse
                  };
                  return newMessages;
                });
              }
              if (data.done) {
                setIsGenerating(false);
                return;
              }
              if (data.error) {
                throw new Error(data.error);
              }
            } catch (e) {
              // Skip invalid JSON
            }
          }
        }
      }
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => {
        const newMessages = [...prev];
        newMessages[newMessages.length - 1] = {
          ...newMessages[newMessages.length - 1],
          content: `Sorry, I encountered an error: ${error instanceof Error ? error.message : 'Unknown error'}. Please try again.`
        };
        return newMessages;
      });
    } finally {
      setIsGenerating(false);
      // Refocus input after sending
      setTimeout(() => {
        if (inputRef.current) {
          inputRef.current.focus();
        }
      }, 100);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-full bg-[#1a1a1a] text-white overflow-hidden">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6 min-h-0">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <h2 className="text-2xl font-bold mb-2">How can I help you today?</h2>
            <p className="text-white/60 max-w-md">
              Ask me anything about content creation, strategy, ideas, or just chat freely!
            </p>
          </div>
        ) : (
          <>
            {messages.map((message, idx) => (
              <div
                key={idx}
                className={`flex gap-4 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`max-w-[85%] ${message.role === 'user' ? 'order-2' : ''}`}>
                  <div
                    className={`inline-block px-4 py-3 rounded-2xl ${
                      message.role === 'user'
                        ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white'
                        : 'bg-[#0f0f0f] text-white/90 border border-white/10'
                    }`}
                  >
                    <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
                    {isGenerating && idx === messages.length - 1 && message.role === 'assistant' && (
                      <span className="inline-block w-2 h-2 bg-white/60 rounded-full ml-1 animate-pulse" />
                    )}
                  </div>
                </div>

                {message.role === 'user' && (
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-r from-purple-600 to-blue-600 flex items-center justify-center order-1">
                    <User className="w-4 h-4 text-white" />
                  </div>
                )}
              </div>
            ))}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input Area - Fixed height to prevent layout shifts */}
      <div className="border-t border-white/10 bg-[#1a1a1a] flex-shrink-0">
        <div className="max-w-4xl mx-auto p-4">
          <div className="flex gap-3 items-end">
            <div className="flex-1 relative">
              <textarea
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Message CreatorFlow AI..."
                className="w-full p-4 bg-[#0f0f0f] border border-white/10 rounded-xl text-white placeholder-white/40 resize-none focus:outline-none focus:border-purple-500/50 focus:ring-1 focus:ring-purple-500/50 transition-all overflow-y-auto"
                rows={1}
                disabled={isGenerating}
                style={{
                  minHeight: '52px',
                  maxHeight: '200px',
                  height: '52px',
                }}
                onInput={(e) => {
                  const target = e.target as HTMLTextAreaElement;
                  const newHeight = Math.min(Math.max(target.scrollHeight, 52), 200);
                  target.style.height = `${newHeight}px`;
                }}
              />
            </div>
            <button
              onClick={handleSend}
              disabled={!input.trim() || isGenerating}
              className="px-6 py-4 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-xl hover:opacity-90 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 flex-shrink-0 h-[52px]"
              style={{ minHeight: '52px' }}
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
          {/* Reserve space for help text to prevent layout shifts */}
          <div className="h-5 mt-2">
            <p className="text-xs text-white/40 text-center">
              Press Enter to send, Shift+Enter for new line
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

