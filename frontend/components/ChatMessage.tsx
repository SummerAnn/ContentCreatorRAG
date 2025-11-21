'use client';

import { User, Bot } from 'lucide-react';
import GeneratedContent from './GeneratedContent';

interface ChatMessageProps {
  role: 'user' | 'assistant';
  content: string;
  type?: 'hooks' | 'script' | 'shotlist' | 'music' | 'titles' | 'description' | 'tags' | 'thumbnails' | 'beatmap' | 'cta' | 'tools';
}

export default function ChatMessage({ role, content, type }: ChatMessageProps) {
  if (role === 'assistant' && type) {
    return <GeneratedContent type={type} content={content} isStreaming={false} />;
  }

  return (
    <div className={`flex gap-4 max-w-3xl ${role === 'user' ? 'ml-auto' : ''}`}>
      {role === 'assistant' && (
        <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-[var(--accent)] to-[var(--accent-dark)] flex items-center justify-center luxury-shadow">
          <Bot className="w-5 h-5 text-white" />
        </div>
      )}
      
      <div className={`flex-1 ${role === 'user' ? 'text-right' : ''}`}>
        <div
          className={`inline-block px-5 py-3 rounded-xl luxury-shadow ${
            role === 'user'
              ? 'luxury-accent text-white'
              : 'bg-white dark:bg-[#1a1a1a] text-[var(--foreground)] luxury-border'
          }`}
        >
          <p className="whitespace-pre-wrap">{content}</p>
        </div>
      </div>

      {role === 'user' && (
        <div className="flex-shrink-0 w-10 h-10 rounded-full luxury-accent flex items-center justify-center luxury-shadow">
          <User className="w-5 h-5 text-white" />
        </div>
      )}
    </div>
  );
}

