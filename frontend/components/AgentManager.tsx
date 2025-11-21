'use client';

import { useState, useEffect } from 'react';
import { X, Plus, Edit2, Trash2, Sparkles } from 'lucide-react';

interface Agent {
  id: string;
  name: string;
  platform: string;
  niche: string;
  goal: string;
  description?: string;
  brand_voice?: any;
  created_at?: string;
}

interface AgentManagerProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectAgent: (agent: Agent) => void;
}

const platforms = [
  { id: 'youtube_short', label: 'YouTube Shorts' },
  { id: 'youtube', label: 'YouTube Long' },
  { id: 'tiktok', label: 'TikTok' },
  { id: 'instagram_reel', label: 'Instagram Reels' },
  { id: 'instagram_carousel', label: 'Instagram Carousel' },
  { id: 'linkedin', label: 'LinkedIn' },
  { id: 'twitter_thread', label: 'Twitter/X Thread' },
  { id: 'pinterest', label: 'Pinterest Pin' },
  { id: 'podcast_clip', label: 'Podcast Clip' },
];

const goals = [
  { id: 'grow_followers', label: 'Grow Followers' },
  { id: 'drive_traffic', label: 'Drive Traffic' },
  { id: 'educate', label: 'Educate Audience' },
  { id: 'sell_product', label: 'Sell Product/Service' },
  { id: 'build_authority', label: 'Build Authority' },
  { id: 'viral_reach', label: 'Viral Reach' },
  { id: 'community_engagement', label: 'Community Engagement' },
  { id: 'ugc', label: 'UGC (User Generated Content)' },
  { id: 'brand_deal', label: 'Brand Deal / Sponsored Content' },
  { id: 'entertainment', label: 'Entertainment' },
  { id: 'engagement', label: 'Maximize Engagement' },
];

export default function AgentManager({ isOpen, onClose, onSelectAgent }: AgentManagerProps) {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingAgent, setEditingAgent] = useState<Agent | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    platform: '',
    niche: '',
    goal: '',
    description: '',
  });

  useEffect(() => {
    if (isOpen) {
      loadAgents();
    }
  }, [isOpen]);

  const loadAgents = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/agents/`);
      const data = await response.json();
      setAgents(data.agents || []);
    } catch (error) {
      console.error('Error loading agents:', error);
    }
  };

  const handleCreate = async () => {
    if (!formData.name || !formData.platform || !formData.niche) {
      alert('Please fill in name, platform, and niche');
      return;
    }

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/agents/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        await loadAgents();
        setFormData({ name: '', platform: '', niche: '', goal: '', description: '' });
        setShowCreateForm(false);
      }
    } catch (error) {
      console.error('Error creating agent:', error);
      alert('Failed to create agent');
    }
  };

  const handleDelete = async (agentId: string) => {
    if (!confirm('Are you sure you want to delete this agent?')) return;

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/agents/${agentId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        await loadAgents();
      }
    } catch (error) {
      console.error('Error deleting agent:', error);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <div className="flex items-center gap-3">
            <Sparkles className="w-6 h-6 text-blue-600" />
            <h2 className="text-2xl font-bold text-gray-800">Digital Agents</h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {!showCreateForm && !editingAgent ? (
            <>
              <div className="mb-4 flex justify-between items-center">
                <p className="text-gray-600">Create specialized agents for different content types</p>
                <button
                  onClick={() => setShowCreateForm(true)}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
                >
                  <Plus className="w-4 h-4" />
                  New Agent
                </button>
              </div>

              {agents.length === 0 ? (
                <div className="text-center py-12">
                  <Sparkles className="w-16 h-16 mx-auto text-gray-300 mb-4" />
                  <p className="text-gray-500 mb-4">No agents yet. Create your first one!</p>
                  <button
                    onClick={() => setShowCreateForm(true)}
                    className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    Create Agent
                  </button>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {agents.map((agent) => (
                    <div
                      key={agent.id}
                      className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition"
                    >
                      <div className="flex justify-between items-start mb-2">
                        <h3 className="text-lg font-semibold text-gray-800">{agent.name}</h3>
                        <div className="flex gap-2">
                          <button
                            onClick={() => {
                              setEditingAgent(agent);
                              setFormData({
                                name: agent.name,
                                platform: agent.platform,
                                niche: agent.niche,
                                goal: agent.goal,
                                description: agent.description || '',
                              });
                            }}
                            className="p-1 text-blue-600 hover:bg-blue-50 rounded"
                            title="Edit"
                          >
                            <Edit2 className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleDelete(agent.id)}
                            className="p-1 text-red-600 hover:bg-red-50 rounded"
                            title="Delete"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                      <div className="space-y-1 text-sm text-gray-600">
                        <p><span className="font-medium">Platform:</span> {platforms.find(p => p.id === agent.platform)?.label || agent.platform}</p>
                        <p><span className="font-medium">Niche:</span> {agent.niche}</p>
                        <p><span className="font-medium">Goal:</span> {goals.find(g => g.id === agent.goal)?.label || agent.goal}</p>
                        {agent.description && <p className="text-gray-500 mt-2">{agent.description}</p>}
                      </div>
                      <button
                        onClick={() => {
                          onSelectAgent(agent);
                          onClose();
                        }}
                        className="mt-4 w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                      >
                        Use This Agent
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </>
          ) : (
            <div className="max-w-2xl mx-auto">
              <h3 className="text-xl font-semibold mb-4">
                {editingAgent ? 'Edit Agent' : 'Create New Agent'}
              </h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Agent Name *
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    placeholder="e.g., Science & Tech YouTube"
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Platform *
                  </label>
                  <select
                    value={formData.platform}
                    onChange={(e) => setFormData({ ...formData, platform: e.target.value })}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Select platform</option>
                    {platforms.map((p) => (
                      <option key={p.id} value={p.id}>{p.label}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Niche *
                  </label>
                  <input
                    type="text"
                    value={formData.niche}
                    onChange={(e) => setFormData({ ...formData, niche: e.target.value })}
                    placeholder="e.g., science, tech, horror, travel"
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Goal
                  </label>
                  <select
                    value={formData.goal}
                    onChange={(e) => setFormData({ ...formData, goal: e.target.value })}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Select goal</option>
                    {goals.map((g) => (
                      <option key={g.id} value={g.id}>{g.label}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Description (optional)
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    placeholder="Describe this agent's focus and style..."
                    rows={3}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div className="flex gap-3">
                  <button
                    onClick={editingAgent ? async () => {
                      try {
                        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
                        const response = await fetch(`${apiUrl}/api/agents/${editingAgent.id}`, {
                          method: 'PUT',
                          headers: { 'Content-Type': 'application/json' },
                          body: JSON.stringify(formData),
                        });
                        if (response.ok) {
                          await loadAgents();
                          setEditingAgent(null);
                          setFormData({ name: '', platform: '', niche: '', goal: '', description: '' });
                        }
                      } catch (error) {
                        console.error('Error updating agent:', error);
                      }
                    } : handleCreate}
                    className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    {editingAgent ? 'Update Agent' : 'Create Agent'}
                  </button>
                  <button
                    onClick={() => {
                      setShowCreateForm(false);
                      setEditingAgent(null);
                      setFormData({ name: '', platform: '', niche: '', goal: '', description: '' });
                    }}
                    className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

