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
  agent_type?: string;
  team?: string;
  template_id?: string;
}

interface Template {
  name: string;
  description: string;
  agent_type: string;
  team: string;
  specialized_platforms: string[];
  capabilities: string[];
  temperature?: number;
  max_tokens?: number;
  template_id?: string;
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
  const [templates, setTemplates] = useState<Template[]>([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showTemplates, setShowTemplates] = useState(true); // Show templates by default
  const [selectedTeam, setSelectedTeam] = useState<string>('all');
  const [editingAgent, setEditingAgent] = useState<Agent | null>(null);
  const [hiringTeam, setHiringTeam] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    platform: '',
    niche: '',
    goal: '',
    description: '',
  });

  const teams = [
    { id: 'all', label: 'All Teams' },
    { id: 'Strategy', label: 'Strategy' },
    { id: 'Content', label: 'Content' },
    { id: 'Creative', label: 'Creative' },
    { id: 'Analytics', label: 'Analytics' },
    { id: 'Distribution', label: 'Distribution' },
    { id: 'Leadership', label: 'Leadership' },
  ];

  useEffect(() => {
    if (isOpen) {
      loadAgents();
      loadTemplates();
    }
  }, [isOpen]);

  const loadTemplates = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/agents/templates`);
      const data = await response.json();
      setTemplates(data.templates || []);
    } catch (error) {
      console.error('Error loading templates:', error);
    }
  };

  const createFromTemplate = async (templateId: string, platform: string = 'tiktok', niche: string = 'general', goal: string = 'grow_followers', silent: boolean = false) => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const params = new URLSearchParams({
        template_id: templateId,
        platform: platform,
        niche: niche,
        goal: goal
      });
      const response = await fetch(`${apiUrl}/api/agents/from-template?${params.toString()}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });

      if (response.ok) {
        const data = await response.json();
        if (!silent) {
          await loadAgents();
          // Get friendly name from template or use formatted templateId
          const templates = await fetch(`${apiUrl}/api/agents/templates`).then(r => r.json()).catch(() => ({ templates: [] }));
          const template = templates.templates?.find((t: any) => t.template_id === templateId);
          const agentName = template?.name || templateId.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase());
          alert(`${agentName} hired successfully!`);
        }
        return data; // Return the created agent data
      } else {
        throw new Error('Failed to create agent');
      }
    } catch (error) {
      console.error('Error creating from template:', error);
      if (!silent) {
        alert('Failed to hire agent. Please try again.');
      }
      throw error;
    }
  };

  const hireFullTeam = async () => {
    if (!confirm('Hire all 16 marketing team members? This will create agents for Strategy, Content, Creative, Analytics, Distribution, and Leadership teams.')) {
      return;
    }

    setHiringTeam(true);
    
    // Map template IDs to friendly names for success messages
    const templateMap: Record<string, string> = {
      'chief_strategy_officer': 'Chief Strategy Officer',
      'brand_strategist': 'Brand Strategist',
      'audience_researcher': 'Audience Research Analyst',
      'creative_director': 'Creative Director',
      'copywriter': 'Senior Copywriter',
      'scriptwriter': 'Video Script Writer',
      'content_editor': 'Content Editor',
      'hook_creator': 'Hook Specialist',
      'thumbnail_designer': 'Thumbnail Designer',
      'performance_analyst': 'Performance Analyst',
      'growth_hacker': 'Growth Hacker',
      'ab_testing_specialist': 'A/B Testing Specialist',
      'platform_optimizer': 'Platform Optimizer',
      'seo_hashtag_specialist': 'SEO & Hashtag Specialist',
      'community_manager': 'Community Manager',
      'campaign_manager': 'Campaign Manager'
    };
    
    const templateIds = [
      'chief_strategy_officer', 'brand_strategist', 'audience_researcher',
      'creative_director', 'copywriter', 'scriptwriter', 'content_editor',
      'hook_creator', 'thumbnail_designer',
      'performance_analyst', 'growth_hacker', 'ab_testing_specialist',
      'platform_optimizer', 'seo_hashtag_specialist', 'community_manager',
      'campaign_manager'
    ];

    // Get user's current settings
    const userId = localStorage.getItem('user_id') || 'default_user';
    let platform = 'tiktok';
    let niche = 'general';
    let goal = 'grow_followers';
    
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const profileRes = await fetch(`${apiUrl}/api/profile/${userId}/defaults`);
      if (profileRes.ok) {
        const profileData = await profileRes.json();
        if (profileData.has_profile && profileData.defaults) {
          platform = profileData.defaults.platform || platform;
          niche = profileData.defaults.niche || niche;
          goal = profileData.defaults.goal || goal;
        }
      }
    } catch (e) {
      // Use defaults if profile fetch fails
    }

    // Ask user to confirm or update settings
    const userPlatform = prompt(`Enter platform (current: ${platform}):`, platform) || platform;
    const userNiche = prompt(`Enter niche (current: ${niche}):`, niche) || niche;
    const userGoal = prompt(`Enter goal (current: ${goal}):`, goal) || goal;

    let successCount = 0;
    let failed: Array<{ id: string; name: string }> = [];
    
    for (const templateId of templateIds) {
      try {
        const agent = await createFromTemplate(templateId, userPlatform, userNiche, userGoal);
        successCount++;
        const agentName = templateMap[templateId] || templateId;
        console.log(`✅ ${agentName} hired successfully!`);
        // Show success message in console and optionally in UI
        if (agent && agent.name) {
          console.log(`   → Agent ID: ${agent.id}, Name: ${agent.name}`);
        }
        await new Promise(resolve => setTimeout(resolve, 200)); // Small delay between requests
      } catch (error) {
        const agentName = templateMap[templateId] || templateId;
        console.error(`❌ Failed to hire ${agentName}:`, error);
        failed.push({ id: templateId, name: agentName });
      }
    }

    setHiringTeam(false);
    
    // Show final summary
    if (failed.length > 0) {
      console.warn(`⚠️ Hired ${successCount}/${templateIds.length} team members.`);
      console.warn(`   Failed: ${failed.map(f => f.name).join(', ')}`);
      alert(`Hired ${successCount}/${templateIds.length} team members.\n\nFailed:\n${failed.map(f => `• ${f.name}`).join('\n')}`);
    } else {
      console.log(`🎉 Successfully hired all ${successCount} team members!`);
      alert(`Successfully hired all ${successCount} team members!`);
    }
    
    await loadAgents();
  };

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
      <div className="bg-[var(--background)] rounded-lg luxury-shadow-lg max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col luxury-border">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b luxury-border">
          <div className="flex items-center gap-3">
            <Sparkles className="w-6 h-6 text-[var(--accent)]" />
            <h2 className="text-2xl font-bold text-[var(--foreground)] tracking-tight">Marketing Team</h2>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setShowTemplates(!showTemplates)}
              className="px-4 py-2 luxury-accent hover:opacity-90 text-white rounded-lg text-sm transition luxury-shadow"
            >
              {showTemplates ? 'Show My Agents' : 'Hire Team Members'}
            </button>
            <button
              onClick={onClose}
              className="p-2 hover:bg-[var(--muted)] rounded-lg transition text-[var(--foreground)]/60 hover:text-[var(--foreground)]"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 bg-[var(--background)]">
          {showTemplates ? (
            <>
              {/* Hire Full Team Banner */}
              <div className="mb-8 p-6 luxury-accent text-white rounded-xl luxury-shadow-lg border border-[var(--accent)]/30">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-2xl font-bold mb-2 tracking-tight">Hire Your Complete Marketing Team</h2>
                    <p className="text-white/90">
                      Get all 16 specialists working for you instantly
                    </p>
                  </div>
                  <button
                    onClick={hireFullTeam}
                    disabled={hiringTeam}
                    className="px-6 py-3 bg-white text-[var(--accent-dark)] rounded-lg font-bold hover:bg-[var(--accent-light)] transition-colors whitespace-nowrap disabled:opacity-50 luxury-shadow"
                  >
                    {hiringTeam ? 'Hiring Team...' : 'Hire Full Team'}
                  </button>
                </div>
              </div>

              {/* Team Filter */}
              <div className="mb-6 flex gap-2 overflow-x-auto pb-2">
                {teams.map(team => (
                  <button
                    key={team.id}
                    onClick={() => setSelectedTeam(team.id)}
                    className={`px-4 py-2 rounded-lg whitespace-nowrap transition-all luxury-shadow ${
                      selectedTeam === team.id
                        ? 'luxury-accent text-white'
                        : 'bg-white dark:bg-[#1a1a1a] text-[var(--foreground)] hover:border-[var(--accent)]/50 luxury-border'
                    }`}
                  >
                    {team.label}
                  </button>
                ))}
              </div>

              {/* Templates Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {templates
                  .filter(t => selectedTeam === 'all' || t.team === selectedTeam)
                  .map((template, idx) => (
                    <div
                      key={idx}
                      className="luxury-border rounded-lg p-4 hover:border-[var(--accent)]/50 transition bg-white dark:bg-[#1a1a1a] luxury-shadow"
                    >
                      <div className="flex items-start gap-3 mb-3">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <h3 className="font-bold text-lg text-[var(--foreground)]">{template.name}</h3>
                            <span className="px-2 py-1 bg-[var(--accent)]/10 text-[var(--accent)] rounded text-xs font-medium border border-[var(--accent)]/30">
                              {template.team}
                            </span>
                          </div>
                          <div className="text-xs text-[var(--foreground)]/60 mb-2">
                            {template.agent_type.replace(/_/g, ' ')}
                          </div>
                        </div>
                      </div>
                      
                      <p className="text-sm text-[var(--foreground)]/80 mb-4">{template.description}</p>
                      
                      <div className="mb-4">
                        <div className="text-xs font-medium text-[var(--foreground)]/60 mb-1">Capabilities:</div>
                        <div className="flex flex-wrap gap-1">
                          {template.capabilities.slice(0, 3).map((cap, i) => (
                            <span key={i} className="px-2 py-1 bg-[var(--muted)] text-[var(--foreground)] rounded text-xs luxury-border">
                              {cap.replace(/_/g, ' ')}
                            </span>
                          ))}
                          {template.capabilities.length > 3 && (
                            <span className="px-2 py-1 bg-[var(--muted)] text-[var(--foreground)] rounded text-xs luxury-border">
                              +{template.capabilities.length - 3} more
                            </span>
                          )}
                        </div>
                      </div>

                      <button
                        onClick={async () => {
                          // Get user's current settings or prompt
                          const userId = localStorage.getItem('user_id') || 'default_user';
                          let platform = 'tiktok';
                          let niche = 'general';
                          let goal = 'grow_followers';
                          
                          // Try to get from user profile defaults
                          try {
                            const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
                            const profileRes = await fetch(`${apiUrl}/api/profile/${userId}/defaults`);
                            if (profileRes.ok) {
                              const profileData = await profileRes.json();
                              if (profileData.has_profile && profileData.defaults) {
                                platform = profileData.defaults.platform || platform;
                                niche = profileData.defaults.niche || niche;
                                goal = profileData.defaults.goal || goal;
                              }
                            }
                          } catch (e) {
                            // Use defaults if profile fetch fails
                          }
                          
                          // Use template_id if available, otherwise derive from name
                          const templateId = template.template_id || template.name
                            .toLowerCase()
                            .replace(/[&]/g, '')
                            .replace(/\s+/g, '_')
                            .replace(/\//g, '_')
                            .replace(/\s*&\s*/g, 'and_');
                          
                          await createFromTemplate(templateId, platform, niche, goal);
                        }}
                        className="w-full px-4 py-2 luxury-accent hover:opacity-90 text-white rounded-lg transition text-sm font-medium luxury-shadow"
                      >
                        Hire This Agent
                      </button>
                    </div>
                  ))}
              </div>
            </>
          ) : !showCreateForm && !editingAgent ? (
            <>
              <div className="mb-4 flex justify-between items-center">
                <p className="text-[var(--foreground)]/80">Your hired marketing team members</p>
                <button
                  onClick={() => setShowCreateForm(true)}
                  className="px-4 py-2 luxury-accent hover:opacity-90 text-white rounded-lg flex items-center gap-2 transition luxury-shadow"
                >
                  <Plus className="w-4 h-4" />
                  Custom Agent
                </button>
              </div>

              {agents.length === 0 ? (
                <div className="text-center py-12">
                  <Sparkles className="w-16 h-16 mx-auto text-[var(--accent)]/40 mb-4" />
                  <p className="text-[var(--foreground)]/60 mb-4">No agents yet. Create your first one!</p>
                  <button
                    onClick={() => setShowCreateForm(true)}
                    className="px-6 py-3 luxury-accent hover:opacity-90 text-white rounded-lg transition luxury-shadow"
                  >
                    Create Agent
                  </button>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {agents.map((agent) => (
                    <div
                      key={agent.id}
                      className="luxury-border rounded-lg p-4 hover:border-[var(--accent)]/50 transition bg-white dark:bg-[#1a1a1a] luxury-shadow"
                    >
                      <div className="flex items-start gap-3 mb-3">
                        <div className="flex-1">
                          <div className="flex justify-between items-start mb-1">
                            <div className="flex-1">
                              <h3 className="text-lg font-semibold text-[var(--foreground)]">{agent.name}</h3>
                              {agent.team && (
                                <span className="inline-block px-2 py-1 bg-[var(--accent)]/10 text-[var(--accent)] rounded text-xs font-medium mt-1 border border-[var(--accent)]/30">
                                  {agent.team}
                                </span>
                              )}
                            </div>
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
                                className="p-1 text-[var(--accent)] hover:bg-[var(--accent)]/10 rounded transition"
                                title="Edit"
                              >
                                <Edit2 className="w-4 h-4" />
                              </button>
                              <button
                                onClick={() => handleDelete(agent.id)}
                                className="p-1 text-red-400 hover:bg-red-500/20 rounded transition"
                                title="Delete"
                              >
                                <Trash2 className="w-4 h-4" />
                              </button>
                            </div>
                          </div>
                        </div>
                      </div>
                      <div className="space-y-1 text-sm text-[var(--foreground)]/80">
                        <p><span className="font-medium text-[var(--foreground)]">Platform:</span> {platforms.find(p => p.id === agent.platform)?.label || agent.platform}</p>
                        <p><span className="font-medium text-[var(--foreground)]">Niche:</span> {agent.niche}</p>
                        <p><span className="font-medium text-[var(--foreground)]">Goal:</span> {goals.find(g => g.id === agent.goal)?.label || agent.goal}</p>
                        {agent.description && <p className="text-[var(--foreground)]/60 mt-2">{agent.description}</p>}
                      </div>
                      <button
                        onClick={() => {
                          onSelectAgent(agent);
                          onClose();
                        }}
                        className="mt-4 w-full px-4 py-2 luxury-accent hover:opacity-90 text-white rounded-lg transition luxury-shadow"
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
              <h3 className="text-xl font-semibold mb-4 text-[var(--foreground)] tracking-tight">
                {editingAgent ? 'Edit Agent' : 'Create New Agent'}
              </h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-[var(--foreground)]/80 mb-1">
                    Agent Name *
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    placeholder="e.g., Science & Tech YouTube"
                    className="w-full p-3 luxury-border bg-white dark:bg-[#1a1a1a] text-[var(--foreground)] rounded-lg focus:ring-2 focus:ring-[var(--accent)] focus:border-[var(--accent)] transition luxury-shadow"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-[var(--foreground)]/80 mb-1">
                    Platform *
                  </label>
                  <select
                    value={formData.platform}
                    onChange={(e) => setFormData({ ...formData, platform: e.target.value })}
                    className="w-full p-3 luxury-border bg-white dark:bg-[#1a1a1a] text-[var(--foreground)] rounded-lg focus:ring-2 focus:ring-[var(--accent)] focus:border-[var(--accent)] transition luxury-shadow"
                  >
                    <option value="">Select platform</option>
                    {platforms.map((p) => (
                      <option key={p.id} value={p.id}>{p.label}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-[var(--foreground)]/80 mb-1">
                    Niche *
                  </label>
                  <input
                    type="text"
                    value={formData.niche}
                    onChange={(e) => setFormData({ ...formData, niche: e.target.value })}
                    placeholder="e.g., science, tech, horror, travel"
                    className="w-full p-3 luxury-border bg-white dark:bg-[#1a1a1a] text-[var(--foreground)] rounded-lg focus:ring-2 focus:ring-[var(--accent)] focus:border-[var(--accent)] transition luxury-shadow"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-[var(--foreground)]/80 mb-1">
                    Goal
                  </label>
                  <select
                    value={formData.goal}
                    onChange={(e) => setFormData({ ...formData, goal: e.target.value })}
                    className="w-full p-3 luxury-border bg-white dark:bg-[#1a1a1a] text-[var(--foreground)] rounded-lg focus:ring-2 focus:ring-[var(--accent)] focus:border-[var(--accent)] transition luxury-shadow"
                  >
                    <option value="">Select goal</option>
                    {goals.map((g) => (
                      <option key={g.id} value={g.id}>{g.label}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-[var(--foreground)]/80 mb-1">
                    Description (optional)
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    placeholder="Describe this agent's focus and style..."
                    rows={3}
                    className="w-full p-3 luxury-border bg-white dark:bg-[#1a1a1a] text-[var(--foreground)] rounded-lg focus:ring-2 focus:ring-[var(--accent)] focus:border-[var(--accent)] transition luxury-shadow"
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
                    className="flex-1 px-6 py-3 luxury-accent hover:opacity-90 text-white rounded-lg transition luxury-shadow"
                  >
                    {editingAgent ? 'Update Agent' : 'Create Agent'}
                  </button>
                  <button
                    onClick={() => {
                      setShowCreateForm(false);
                      setEditingAgent(null);
                      setFormData({ name: '', platform: '', niche: '', goal: '', description: '' });
                    }}
                    className="px-6 py-3 bg-white dark:bg-[#1a1a1a] text-[var(--foreground)] rounded-lg hover:bg-[var(--muted)] transition luxury-border luxury-shadow"
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

