'use client';

import { useState } from 'react';
import { Menu, X, Plus, History, Settings, Database, Bot, Sparkles, Home } from 'lucide-react';
import AgentManager from './AgentManager';
import RandomIdeaRoaster from './RandomIdeaRoaster';
import ConversationHistory from './ConversationHistory';

interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
  onAgentSelect?: (agent: { platform: string; niche: string; goal: string; personality?: string; audience?: string[]; reference?: string }) => void;
  onHome?: () => void;
  onLoadConversation?: (conversation: any) => void;
}

export default function Sidebar({ isOpen, onToggle, onAgentSelect, onHome, onLoadConversation }: SidebarProps) {
  const [showAgents, setShowAgents] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [showLibrary, setShowLibrary] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [showIdeaRoaster, setShowIdeaRoaster] = useState(false);

  const handleAgentSelect = (agent: any) => {
    if (onAgentSelect) {
      onAgentSelect({
        platform: agent.platform,
        niche: agent.niche,
        goal: agent.goal,
        personality: agent.personality,
        audience: agent.audience,
        reference: agent.reference
      });
    }
  };

  return (
    <>
      {/* Mobile toggle button */}
      <button
        onClick={onToggle}
        className="lg:hidden fixed top-4 left-4 z-50 p-2 bg-gray-800 text-white rounded-md"
      >
        {isOpen ? <X size={20} /> : <Menu size={20} />}
      </button>

      {/* Sidebar */}
      <aside
        className={`
          fixed lg:static inset-y-0 left-0 z-40
          w-64 bg-[#0f0f0f] dark:bg-[#0a0a0a] text-white
          transform transition-transform duration-300 ease-in-out
          luxury-shadow-lg
          ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        `}
      >
        <div className="flex flex-col h-full p-5">
          {/* Logo */}
          <div className="mb-8 mt-4">
            <h1 className="text-2xl font-bold text-white tracking-tight">CreatorFlow AI</h1>
            <p className="text-white/60 text-xs tracking-wide uppercase mt-1">Content Creation Platform</p>
          </div>

          {/* Navigation */}
          <nav className="flex-1 space-y-2">
            <button 
              onClick={() => onHome?.()}
              className="w-full flex items-center gap-3 px-4 py-3 luxury-accent hover:opacity-90 text-white rounded-lg transition-all luxury-shadow"
            >
              <Home size={20} />
              <span className="font-medium">Home</span>
            </button>

            <button 
              onClick={() => setShowAgents(true)}
              className="w-full flex items-center gap-3 px-4 py-3 bg-white/5 hover:bg-white/10 text-white/90 rounded-lg transition-all luxury-border"
            >
              <Plus size={20} />
              <span>New Project</span>
            </button>

            <button 
              onClick={() => setShowIdeaRoaster(true)}
              className="w-full flex items-center gap-3 px-4 py-3 bg-white/5 hover:bg-white/10 text-white/90 rounded-lg transition-all luxury-border"
            >
              <Sparkles size={20} />
              <span>Random Idea Roaster</span>
            </button>

            <button 
              onClick={() => setShowAgents(true)}
              className="w-full flex items-center gap-3 px-4 py-3 text-white/70 rounded-lg hover:bg-white/5 transition-all"
            >
              <Bot size={20} />
              <span>My Agents</span>
            </button>

            <button 
              onClick={() => setShowHistory(true)}
              className="w-full flex items-center gap-3 px-4 py-3 bg-white/5 hover:bg-white/10 text-white/90 rounded-lg transition-all luxury-border"
            >
              <History size={20} />
              <span>History</span>
            </button>

            <button 
              onClick={() => setShowLibrary(true)}
              className="w-full flex items-center gap-3 px-4 py-3 text-gray-300 rounded-lg hover:bg-gray-800 dark:hover:bg-gray-900 transition"
            >
              <Database size={20} />
              <span>My Content Library</span>
            </button>

            <button 
              onClick={() => setShowSettings(true)}
              className="w-full flex items-center gap-3 px-4 py-3 text-gray-300 rounded-lg hover:bg-gray-800 dark:hover:bg-gray-900 transition"
            >
              <Settings size={20} />
              <span>Settings</span>
            </button>
          </nav>

          {/* Footer */}
          <div className="mt-auto pt-4 border-t border-gray-700">
            <p className="text-gray-400 text-xs text-center">
              Version 1.0.0
            </p>
          </div>
        </div>
      </aside>

      {/* Overlay for mobile */}
      {isOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-black bg-opacity-50 z-30"
          onClick={onToggle}
        />
      )}

      {/* Random Idea Roaster Modal */}
      {showIdeaRoaster && (
        <RandomIdeaRoaster
          isOpen={showIdeaRoaster}
          onClose={() => setShowIdeaRoaster(false)}
          onSelectIdea={(idea) => {
            handleAgentSelect(idea);
            setShowIdeaRoaster(false);
          }}
        />
      )}

      {/* Agent Manager Modal */}
      <AgentManager
        isOpen={showAgents}
        onClose={() => setShowAgents(false)}
        onSelectAgent={handleAgentSelect}
      />

      {/* History Modal */}
      {showHistory && (
        <ConversationHistory
          isOpen={showHistory}
          onClose={() => setShowHistory(false)}
          onLoadConversation={(conv) => {
            if (onLoadConversation) {
              onLoadConversation(conv);
            }
            setShowHistory(false);
          }}
        />
      )}

      {/* Content Library Modal */}
      {showLibrary && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-2xl font-bold">My Content Library</h2>
              <button onClick={() => setShowLibrary(false)} className="text-gray-500 hover:text-gray-700">
                <X size={24} />
              </button>
            </div>
            <p className="text-gray-600 mb-4">Upload your best-performing content to improve RAG results.</p>
            <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
              Upload Content
            </button>
          </div>
        </div>
      )}

      {/* Settings Modal */}
      {showSettings && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-2xl font-bold">Settings</h2>
              <button onClick={() => setShowSettings(false)} className="text-gray-500 hover:text-gray-700">
                <X size={24} />
              </button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">API URL</label>
                <input
                  type="text"
                  defaultValue={process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}
                  className="w-full p-3 border border-gray-300 rounded-lg"
                  readOnly
                />
              </div>
              <p className="text-gray-600 text-sm">More settings coming soon!</p>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
