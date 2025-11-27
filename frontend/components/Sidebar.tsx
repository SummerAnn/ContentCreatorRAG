'use client';

import { useState } from 'react';
import { Menu, X, Plus, History, Settings, Database, Sparkles, Home, ChevronLeft, ChevronRight, FileText, Layers, TrendingUp, ArrowUpDown, Mic, Type } from 'lucide-react';
import AgentManager from './AgentManager';
import RandomIdeaRoaster from './RandomIdeaRoaster';
import ConversationHistory from './ConversationHistory';
import IdeaNotes from './IdeaNotes';
import TemplateLibrary from './TemplateLibrary';
import SwipeFileComponent from './SwipeFile';
import ViralVideoAnalyzer from './ViralVideoAnalyzer';
import ContentSorter from './ContentSorter';
import Transcription from './Transcription';
import ContentLibraryChat from './ContentLibraryChat';
import ViralTitleGenerator from './ViralTitleGenerator';

interface SidebarProps {
  isOpen: boolean;
  isCollapsed?: boolean;
  onToggle: () => void;
  onCollapse?: () => void;
  onAgentSelect?: (agent: { platform: string; niche: string; goal: string; personality?: string; audience?: string[]; reference?: string }) => void;
  onHome?: () => void;
  onLoadConversation?: (conversation: any) => void;
  onDevelopIdea?: (idea: string) => void;
}

export default function Sidebar({ isOpen, isCollapsed = false, onToggle, onCollapse, onAgentSelect, onHome, onLoadConversation, onDevelopIdea }: SidebarProps) {
  const [showAgents, setShowAgents] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [showLibrary, setShowLibrary] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [showIdeaRoaster, setShowIdeaRoaster] = useState(false);
  const [showIdeaNotes, setShowIdeaNotes] = useState(false);
  const [showTemplateLibrary, setShowTemplateLibrary] = useState(false);
  const [showSwipeFile, setShowSwipeFile] = useState(false);
  const [showViralAnalyzer, setShowViralAnalyzer] = useState(false);
  const [showContentSorter, setShowContentSorter] = useState(false);
  const [showTranscription, setShowTranscription] = useState(false);
  const [showTitleGenerator, setShowTitleGenerator] = useState(false);

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
          ${isCollapsed ? 'w-16' : 'w-64'} bg-[#0f0f0f] dark:bg-[#0a0a0a] text-white
          transform transition-all duration-300 ease-in-out
          luxury-shadow-lg
          ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        `}
      >
        <div className="flex flex-col h-full p-4">
          {/* Collapse Button - Desktop Only */}
          <div className="hidden lg:flex justify-end mb-4">
            <button
              onClick={onCollapse}
              className="p-2 rounded-lg hover:bg-white/10 text-white/70 hover:text-white transition-all"
              title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            >
              {isCollapsed ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
            </button>
          </div>

          {/* Logo */}
          {!isCollapsed && (
            <div className="mb-8 mt-2">
              <h1 className="text-2xl font-bold text-white tracking-tight">CreatorFlow AI</h1>
              <p className="text-white/60 text-xs tracking-wide uppercase mt-1">Content Creation Platform</p>
            </div>
          )}

          {/* Navigation */}
          <nav className="flex-1 space-y-2">
            <button 
              onClick={() => onHome?.()}
              className={`w-full flex items-center ${isCollapsed ? 'justify-center px-2' : 'gap-3 px-4'} py-3 luxury-accent hover:opacity-90 text-white rounded-lg transition-all luxury-shadow group relative`}
              title={isCollapsed ? 'Home' : undefined}
            >
              <Home size={20} />
              {!isCollapsed && <span className="font-medium">Home</span>}
              {isCollapsed && (
                <span className="absolute left-full ml-2 px-2 py-1 bg-[#1a1a1a] text-white text-sm rounded-lg opacity-0 group-hover:opacity-100 pointer-events-none whitespace-nowrap z-50 luxury-shadow">
                  Home
                </span>
              )}
            </button>

            <button 
              onClick={() => setShowAgents(true)}
              className={`w-full flex items-center ${isCollapsed ? 'justify-center px-2' : 'gap-3 px-4'} py-3 bg-white/5 hover:bg-white/10 text-white/90 rounded-lg transition-all luxury-border group relative`}
              title={isCollapsed ? 'New Project' : undefined}
            >
              <Plus size={20} />
              {!isCollapsed && <span>New Project</span>}
              {isCollapsed && (
                <span className="absolute left-full ml-2 px-2 py-1 bg-[#1a1a1a] text-white text-sm rounded-lg opacity-0 group-hover:opacity-100 pointer-events-none whitespace-nowrap z-50 luxury-shadow">
                  New Project
                </span>
              )}
            </button>

            <button 
              onClick={() => setShowIdeaRoaster(true)}
              className={`w-full flex items-center ${isCollapsed ? 'justify-center px-2' : 'gap-3 px-4'} py-3 bg-white/5 hover:bg-white/10 text-white/90 rounded-lg transition-all luxury-border group relative`}
              title={isCollapsed ? 'Random Idea Roaster' : undefined}
            >
              <Sparkles size={20} />
              {!isCollapsed && <span>Random Idea Roaster</span>}
              {isCollapsed && (
                <span className="absolute left-full ml-2 px-2 py-1 bg-[#1a1a1a] text-white text-sm rounded-lg opacity-0 group-hover:opacity-100 pointer-events-none whitespace-nowrap z-50 luxury-shadow">
                  Random Idea Roaster
                </span>
              )}
            </button>

            <button 
              onClick={() => setShowTemplateLibrary(true)}
              className={`w-full flex items-center ${isCollapsed ? 'justify-center px-2' : 'gap-3 px-4'} py-3 bg-white/5 hover:bg-white/10 text-white/90 rounded-lg transition-all luxury-border group relative`}
              title={isCollapsed ? 'Template Library' : undefined}
            >
              <Layers size={20} />
              {!isCollapsed && <span>Template Library</span>}
              {isCollapsed && (
                <span className="absolute left-full ml-2 px-2 py-1 bg-[#1a1a1a] text-white text-sm rounded-lg opacity-0 group-hover:opacity-100 pointer-events-none whitespace-nowrap z-50 luxury-shadow">
                  Template Library
                </span>
              )}
            </button>

            <button 
              onClick={() => setShowIdeaNotes(true)}
              className={`w-full flex items-center ${isCollapsed ? 'justify-center px-2' : 'gap-3 px-4'} py-3 bg-white/5 hover:bg-white/10 text-white/90 rounded-lg transition-all luxury-border group relative`}
              title={isCollapsed ? 'Idea Notes' : undefined}
            >
              <FileText size={20} />
              {!isCollapsed && <span>Idea Notes</span>}
              {isCollapsed && (
                <span className="absolute left-full ml-2 px-2 py-1 bg-[#1a1a1a] text-white text-sm rounded-lg opacity-0 group-hover:opacity-100 pointer-events-none whitespace-nowrap z-50 luxury-shadow">
                  Idea Notes
                </span>
              )}
            </button>

            <button 
              onClick={() => setShowSwipeFile(true)}
              className={`w-full flex items-center ${isCollapsed ? 'justify-center px-2' : 'gap-3 px-4'} py-3 bg-white/5 hover:bg-white/10 text-white/90 rounded-lg transition-all luxury-border group relative`}
              title={isCollapsed ? 'Swipe File' : undefined}
            >
              <Database size={20} />
              {!isCollapsed && <span>Swipe File</span>}
              {isCollapsed && (
                <span className="absolute left-full ml-2 px-2 py-1 bg-[#1a1a1a] text-white text-sm rounded-lg opacity-0 group-hover:opacity-100 pointer-events-none whitespace-nowrap z-50 luxury-shadow">
                  Swipe File
                </span>
              )}
            </button>

            <button 
              onClick={() => setShowViralAnalyzer(true)}
              className={`w-full flex items-center ${isCollapsed ? 'justify-center px-2' : 'gap-3 px-4'} py-3 bg-white/5 hover:bg-white/10 text-white/90 rounded-lg transition-all luxury-border group relative`}
              title={isCollapsed ? 'Viral Video Analyzer' : undefined}
            >
              <TrendingUp size={20} />
              {!isCollapsed && <span>Viral Video Analyzer</span>}
              {isCollapsed && (
                <span className="absolute left-full ml-2 px-2 py-1 bg-[#1a1a1a] text-white text-sm rounded-lg opacity-0 group-hover:opacity-100 pointer-events-none whitespace-nowrap z-50 luxury-shadow">
                  Viral Video Analyzer
                </span>
              )}
            </button>

            <button 
              onClick={() => setShowContentSorter(true)}
              className={`w-full flex items-center ${isCollapsed ? 'justify-center px-2' : 'gap-3 px-4'} py-3 bg-white/5 hover:bg-white/10 text-white/90 rounded-lg transition-all luxury-border group relative`}
              title={isCollapsed ? 'Content Sorter' : undefined}
            >
              <ArrowUpDown size={20} />
              {!isCollapsed && <span>Content Sorter</span>}
              {isCollapsed && (
                <span className="absolute left-full ml-2 px-2 py-1 bg-[#1a1a1a] text-white text-sm rounded-lg opacity-0 group-hover:opacity-100 pointer-events-none whitespace-nowrap z-50 luxury-shadow">
                  Content Sorter
                </span>
              )}
            </button>

            <button 
              onClick={() => setShowTranscription(true)}
              className={`w-full flex items-center ${isCollapsed ? 'justify-center px-2' : 'gap-3 px-4'} py-3 bg-white/5 hover:bg-white/10 text-white/90 rounded-lg transition-all luxury-border group relative`}
              title={isCollapsed ? 'Transcription' : undefined}
            >
              <Mic size={20} />
              {!isCollapsed && <span>Transcription</span>}
              {isCollapsed && (
                <span className="absolute left-full ml-2 px-2 py-1 bg-[#1a1a1a] text-white text-sm rounded-lg opacity-0 group-hover:opacity-100 pointer-events-none whitespace-nowrap z-50 luxury-shadow">
                  Transcription
                </span>
              )}
            </button>

            <button 
              onClick={() => setShowTitleGenerator(true)}
              className={`w-full flex items-center ${isCollapsed ? 'justify-center px-2' : 'gap-3 px-4'} py-3 bg-white/5 hover:bg-white/10 text-white/90 rounded-lg transition-all luxury-border group relative`}
              title={isCollapsed ? 'Viral Title Generator' : undefined}
            >
              <Type size={20} />
              {!isCollapsed && <span>Viral Title Generator</span>}
              {isCollapsed && (
                <span className="absolute left-full ml-2 px-2 py-1 bg-[#1a1a1a] text-white text-sm rounded-lg opacity-0 group-hover:opacity-100 pointer-events-none whitespace-nowrap z-50 luxury-shadow">
                  Viral Title Generator
                </span>
              )}
            </button>

            <button
              onClick={() => setShowHistory(true)}
              className={`w-full flex items-center ${isCollapsed ? 'justify-center px-2' : 'gap-3 px-4'} py-3 bg-white/5 hover:bg-white/10 text-white/90 rounded-lg transition-all luxury-border group relative`}
              title={isCollapsed ? 'History' : undefined}
            >
              <History size={20} />
              {!isCollapsed && <span>History</span>}
              {isCollapsed && (
                <span className="absolute left-full ml-2 px-2 py-1 bg-[#1a1a1a] text-white text-sm rounded-lg opacity-0 group-hover:opacity-100 pointer-events-none whitespace-nowrap z-50 luxury-shadow">
                  History
                </span>
              )}
            </button>

            <button 
              onClick={() => setShowLibrary(true)}
              className={`w-full flex items-center ${isCollapsed ? 'justify-center px-2' : 'gap-3 px-4'} py-3 text-white/70 rounded-lg hover:bg-white/5 transition-all group relative`}
              title={isCollapsed ? 'My Content Library' : undefined}
            >
              <Database size={20} />
              {!isCollapsed && <span>My Content Library</span>}
              {isCollapsed && (
                <span className="absolute left-full ml-2 px-2 py-1 bg-[#1a1a1a] text-white text-sm rounded-lg opacity-0 group-hover:opacity-100 pointer-events-none whitespace-nowrap z-50 luxury-shadow">
                  My Content Library
                </span>
              )}
            </button>

            <button 
              onClick={() => {
                // Navigate to settings page
                if (typeof window !== 'undefined') {
                  window.location.href = '/settings';
                }
              }}
              className={`w-full flex items-center ${isCollapsed ? 'justify-center px-2' : 'gap-3 px-4'} py-3 text-white/70 rounded-lg hover:bg-white/5 transition-all group relative`}
              title={isCollapsed ? 'Settings' : undefined}
            >
              <Settings size={20} />
              {!isCollapsed && <span>Settings</span>}
              {isCollapsed && (
                <span className="absolute left-full ml-2 px-2 py-1 bg-[#1a1a1a] text-white text-sm rounded-lg opacity-0 group-hover:opacity-100 pointer-events-none whitespace-nowrap z-50 luxury-shadow">
                  Settings
                </span>
              )}
            </button>
          </nav>

          {/* Footer */}
          {!isCollapsed && (
            <div className="mt-auto pt-4 border-t border-gray-700">
              <p className="text-gray-400 text-xs text-center">
                Version 1.0.0
              </p>
            </div>
          )}
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

      {/* Idea Notes Modal */}
      {showIdeaNotes && (
        <IdeaNotes
          isOpen={showIdeaNotes}
          onClose={() => setShowIdeaNotes(false)}
          onDevelopIdea={(idea) => {
            if (onDevelopIdea) {
              onDevelopIdea(idea);
            }
            setShowIdeaNotes(false);
          }}
        />
      )}

      {/* Template Library Modal */}
      {showTemplateLibrary && (
        <TemplateLibrary
          isOpen={showTemplateLibrary}
          onClose={() => setShowTemplateLibrary(false)}
          onSelectTemplate={(template) => {
            // When template is selected, create an agent-like selection
            // The template will be applied when generating content
            if (onAgentSelect) {
              onAgentSelect({
                platform: template.platforms[0] || '',
                niche: template.niches[0] || '',
                goal: 'entertainment',
                personality: 'friendly',
                audience: ['gen_z'],
                reference: template.description
              });
            }
            setShowTemplateLibrary(false);
          }}
        />
      )}

      {/* Swipe File Modal */}
      {showSwipeFile && (
        <SwipeFileComponent
          isOpen={showSwipeFile}
          onClose={() => setShowSwipeFile(false)}
        />
      )}

      {/* Viral Video Analyzer Modal */}
      {showViralAnalyzer && (
        <ViralVideoAnalyzer
          isOpen={showViralAnalyzer}
          onClose={() => setShowViralAnalyzer(false)}
        />
      )}

      {/* Content Sorter Modal */}
      {showContentSorter && (
        <ContentSorter
          isOpen={showContentSorter}
          onClose={() => setShowContentSorter(false)}
        />
      )}

      {/* Transcription Modal */}
      {showTranscription && (
        <Transcription
          isOpen={showTranscription}
          onClose={() => setShowTranscription(false)}
        />
      )}

      {/* Viral Title Generator Modal */}
      {showTitleGenerator && (
        <ViralTitleGenerator
          isOpen={showTitleGenerator}
          onClose={() => setShowTitleGenerator(false)}
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

      {/* Content Library Chat Modal */}
      {showLibrary && (
        <ContentLibraryChat
          isOpen={showLibrary}
          onClose={() => setShowLibrary(false)}
        />
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
