'use client';

import { useState } from 'react';
import Chat from '@/components/Chat';
import Sidebar from '@/components/Sidebar';
import { Conversation } from '@/lib/history';

export default function Home() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [selectedAgent, setSelectedAgent] = useState<{ platform: string; niche: string; goal: string; personality?: string; audience?: string[]; reference?: string } | null>(null);
  const [selectedConversation, setSelectedConversation] = useState<Conversation | null>(null);
  const [chatKey, setChatKey] = useState(0); // Key to force Chat component remount

  const handleAgentSelect = (agent: { platform: string; niche: string; goal: string; personality?: string; audience?: string[]; reference?: string }) => {
    setSelectedAgent(agent);
    setSelectedConversation(null); // Clear conversation when selecting new agent
  };

  const handleLoadConversation = (conversation: Conversation) => {
    setSelectedConversation(conversation);
    setSelectedAgent(null); // Clear agent when loading conversation
    setChatKey(prev => prev + 1); // Force remount to load conversation
  };

  const handleHome = () => {
    setSelectedAgent(null);
    setSelectedConversation(null);
    setChatKey(prev => prev + 1); // Force Chat component to remount and reset
  };

  return (
    <div className="flex h-screen bg-[var(--background)]">
      <Sidebar 
        isOpen={sidebarOpen} 
        onToggle={() => setSidebarOpen(!sidebarOpen)}
        onAgentSelect={handleAgentSelect}
        onHome={handleHome}
        onLoadConversation={handleLoadConversation}
      />
      <main className="flex-1 flex flex-col overflow-hidden">
        <Chat 
          key={chatKey} 
          initialAgent={selectedAgent} 
          initialConversation={selectedConversation}
        />
      </main>
    </div>
  );
}

