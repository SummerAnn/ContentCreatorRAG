'use client';

import { useState } from 'react';
import Chat from '@/components/Chat';
import Sidebar from '@/components/Sidebar';
import { Conversation } from '@/lib/history';

export default function Home() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState<{ platform: string; niche: string; goal: string; personality?: string; audience?: string[]; reference?: string } | null>(null);
  const [selectedConversation, setSelectedConversation] = useState<Conversation | null>(null);
  const [chatKey, setChatKey] = useState(0); // Key to force Chat component remount
  const [ideaToDevelop, setIdeaToDevelop] = useState<string | null>(null);

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
    setIdeaToDevelop(null);
    setChatKey(prev => prev + 1); // Force Chat component to remount and reset
  };

  const handleDevelopIdea = (idea: string) => {
    setIdeaToDevelop(idea);
    setSelectedAgent(null);
    setSelectedConversation(null);
    setChatKey(prev => prev + 1); // Force Chat component to remount with new idea
  };

  return (
    <div className="w-screen h-screen overflow-hidden">
      <div className="flex h-full bg-[var(--background)] scale-[0.9] origin-top-left" style={{ width: '111.11%', height: '111.11%' }}>
        <Sidebar 
          isOpen={sidebarOpen}
          isCollapsed={sidebarCollapsed}
          onToggle={() => setSidebarOpen(!sidebarOpen)}
          onCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
          onAgentSelect={handleAgentSelect}
          onHome={handleHome}
          onLoadConversation={handleLoadConversation}
          onDevelopIdea={handleDevelopIdea}
        />
        <main className="flex-1 flex flex-col overflow-hidden">
          <Chat 
            key={chatKey} 
            initialAgent={selectedAgent} 
            initialConversation={selectedConversation}
            initialIdea={ideaToDevelop}
          />
        </main>
      </div>
    </div>
  );
}

