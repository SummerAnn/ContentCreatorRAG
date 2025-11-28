'use client';

import { useState, useEffect } from 'react';
import { Zap, Calendar, CheckCircle2, XCircle, RefreshCw, Settings, Bell, Clock, X } from 'lucide-react';

interface AutopilotConfig {
  user_id: string;
  status: 'active' | 'paused' | 'disabled';
  content_goal: 'daily' | 'frequent' | 'weekly';
  platforms: string[];
  niches: string[];
  post_times: string[];
  auto_approve: boolean;
  notification_enabled: boolean;
}

interface GeneratedContent {
  id: string;
  date: string;
  platform: string;
  niche: string;
  hook: string;
  script: string;
  status: 'pending' | 'approved' | 'rejected';
  viral_score: number;
  created_at: string;
}

export default function ContentAutopilot({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  const [config, setConfig] = useState<AutopilotConfig | null>(null);
  const [contentQueue, setContentQueue] = useState<{
    pending: GeneratedContent[];
    approved: GeneratedContent[];
    total_pending: number;
    total_approved: number;
  } | null>(null);
  const [showSetup, setShowSetup] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // Setup form state
  const [setupForm, setSetupForm] = useState({
    content_goal: 'frequent' as const,
    platforms: ['tiktok'] as string[],
    niches: ['lifestyle'] as string[],
    post_times: ['09:00', '15:00'],
    auto_approve: false,
    notification_enabled: true,
  });

  useEffect(() => {
    if (isOpen) {
      fetchConfig();
      fetchQueue();
    }
  }, [isOpen]);

  const fetchConfig = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/autopilot/config/demo_user');
      if (response.ok) {
        const data = await response.json();
        setConfig(data);
        setShowSetup(false);
      } else {
        setShowSetup(true);
      }
    } catch (error) {
      console.error('Failed to fetch config:', error);
      setShowSetup(true);
    }
  };

  const fetchQueue = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/autopilot/queue/demo_user');
      if (response.ok) {
        const data = await response.json();
        setContentQueue(data);
      }
    } catch (error) {
      console.error('Failed to fetch queue:', error);
    }
  };

  const setupAutopilot = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/autopilot/setup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: 'demo_user',
          status: 'active',
          ...setupForm,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setConfig(data.config);
        setShowSetup(false);
        await fetchQueue();
      }
    } catch (error) {
      console.error('Setup failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleAutopilot = async () => {
    if (!config) return;
    
    const newStatus = config.status === 'active' ? 'paused' : 'active';
    
    try {
      const response = await fetch(
        `http://localhost:8000/api/autopilot/toggle/demo_user?status=${newStatus}`,
        { method: 'POST' }
      );

      if (response.ok) {
        await fetchConfig();
      }
    } catch (error) {
      console.error('Toggle failed:', error);
    }
  };

  const approveContent = async (contentId: string) => {
    try {
      await fetch(`http://localhost:8000/api/autopilot/approve/${contentId}?user_id=demo_user`, {
        method: 'POST',
      });
      await fetchQueue();
    } catch (error) {
      console.error('Approve failed:', error);
    }
  };

  const rejectContent = async (contentId: string) => {
    try {
      await fetch(`http://localhost:8000/api/autopilot/reject/${contentId}?user_id=demo_user`, {
        method: 'POST',
      });
      await fetchQueue();
    } catch (error) {
      console.error('Reject failed:', error);
    }
  };

  const regenerateContent = async (contentId: string) => {
    try {
      await fetch(`http://localhost:8000/api/autopilot/regenerate/${contentId}?user_id=demo_user`, {
        method: 'POST',
      });
      await fetchQueue();
    } catch (error) {
      console.error('Regenerate failed:', error);
    }
  };

  if (!isOpen) return null;

  const availableNiches = ['lifestyle', 'beauty', 'fashion', 'business', 'finance', 'education', 'gaming', 'entertainment', 'travel', 'food', 'tech', 'fitness'];
  const availablePlatforms = ['tiktok', 'instagram', 'youtube'];

  if (showSetup || !config) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4 overflow-y-auto">
        <div className="bg-[#1a1a1a] rounded-lg shadow-xl max-w-4xl w-full p-8 text-white max-h-[90vh] overflow-y-auto">
          <div className="flex justify-between items-center mb-6">
            <div>
              <h1 className="text-3xl font-bold mb-2">Setup Content Autopilot</h1>
              <p className="text-white/70">
                Let AI generate content automatically while you sleep
              </p>
            </div>
            <button onClick={onClose} className="text-white/70 hover:text-white transition-colors">
              <X size={24} />
            </button>
          </div>

          <div className="space-y-6">
            {/* Content Goal */}
            <div>
              <label className="block text-sm font-medium text-white/90 mb-2">
                Content Goal
              </label>
              <select
                value={setupForm.content_goal}
                onChange={(e) => setSetupForm({ ...setupForm, content_goal: e.target.value as any })}
                className="w-full px-4 py-2 bg-[#2a2a2a] border border-gray-700 rounded-lg text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              >
                <option value="daily">Daily (1 post/day)</option>
                <option value="frequent">Frequent (3 posts/week)</option>
                <option value="weekly">Weekly (1 post/week)</option>
              </select>
            </div>

            {/* Platforms */}
            <div>
              <label className="block text-sm font-medium text-white/90 mb-2">
                Platforms
              </label>
              <div className="flex flex-wrap gap-2">
                {availablePlatforms.map((platform) => (
                  <button
                    key={platform}
                    onClick={() => {
                      const platforms = setupForm.platforms.includes(platform)
                        ? setupForm.platforms.filter(p => p !== platform)
                        : [...setupForm.platforms, platform];
                      setSetupForm({ ...setupForm, platforms });
                    }}
                    className={`px-4 py-2 rounded-lg border-2 transition-all capitalize ${
                      setupForm.platforms.includes(platform)
                        ? 'border-purple-500 bg-purple-500/20 text-purple-300'
                        : 'border-gray-700 text-white/70 hover:border-purple-500/50 bg-[#2a2a2a]'
                    }`}
                  >
                    {platform}
                  </button>
                ))}
              </div>
            </div>

            {/* Niches */}
            <div>
              <label className="block text-sm font-medium text-white/90 mb-2">
                Niches
              </label>
              <div className="flex flex-wrap gap-2">
                {availableNiches.map((niche) => (
                  <button
                    key={niche}
                    onClick={() => {
                      const niches = setupForm.niches.includes(niche)
                        ? setupForm.niches.filter(n => n !== niche)
                        : [...setupForm.niches, niche];
                      setSetupForm({ ...setupForm, niches });
                    }}
                    className={`px-4 py-2 rounded-lg border-2 transition-all capitalize ${
                      setupForm.niches.includes(niche)
                        ? 'border-purple-500 bg-purple-500/20 text-purple-300'
                        : 'border-gray-700 text-white/70 hover:border-purple-500/50 bg-[#2a2a2a]'
                    }`}
                  >
                    {niche}
                  </button>
                ))}
              </div>
            </div>

            {/* Options */}
            <div className="space-y-3">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={setupForm.notification_enabled}
                  onChange={(e) => setSetupForm({ ...setupForm, notification_enabled: e.target.checked })}
                  className="w-4 h-4 text-purple-600 border-gray-700 rounded focus:ring-purple-500 bg-[#2a2a2a]"
                />
                <span className="text-sm text-white/90">
                  Notify me when new content is ready
                </span>
              </label>

              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={setupForm.auto_approve}
                  onChange={(e) => setSetupForm({ ...setupForm, auto_approve: e.target.checked })}
                  className="w-4 h-4 text-purple-600 border-gray-700 rounded focus:ring-purple-500 bg-[#2a2a2a]"
                />
                <span className="text-sm text-white/90">
                  Auto-approve all generated content
                </span>
              </label>
            </div>

            {/* Submit */}
            <button
              onClick={setupAutopilot}
              disabled={isLoading || setupForm.platforms.length === 0 || setupForm.niches.length === 0}
              className="w-full px-6 py-3 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-white"></div>
                  Setting up...
                </>
              ) : (
                <>
                  <Zap className="w-5 h-5" />
                  Activate Autopilot
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-[#1a1a1a] rounded-lg shadow-xl max-w-6xl w-full p-6 text-white max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold flex items-center gap-3">
              <Zap size={28} />
              Content Autopilot
              {config.status === 'active' && (
                <span className="px-3 py-1 bg-green-500/20 text-green-300 rounded-full text-sm font-medium border border-green-500/50">
                  Active
                </span>
              )}
            </h1>
            <p className="text-white/60 mt-1">
              AI generates content automatically • {contentQueue?.total_pending || 0} pending review
            </p>
          </div>

          <div className="flex gap-3">
            <button
              onClick={toggleAutopilot}
              className={`px-6 py-2 rounded-lg font-medium transition-colors ${
                config.status === 'active'
                  ? 'bg-yellow-500 text-white hover:bg-yellow-600'
                  : 'bg-green-500 text-white hover:bg-green-600'
              }`}
            >
              {config.status === 'active' ? 'Pause' : 'Activate'}
            </button>

            <button
              onClick={() => setShowSetup(true)}
              className="p-2 border border-gray-700 rounded-lg hover:bg-[#2a2a2a] text-white/70 hover:text-white"
            >
              <Settings className="w-5 h-5" />
            </button>

            <button onClick={onClose} className="text-white/70 hover:text-white transition-colors">
              <X size={24} />
            </button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="bg-[#2a2a2a] rounded-lg border border-gray-700 p-4">
            <div className="flex items-center gap-2 mb-2">
              <Clock className="w-5 h-5 text-blue-400" />
              <span className="text-sm font-medium text-white/70">Content Goal</span>
            </div>
            <p className="text-2xl font-bold capitalize">
              {config.content_goal}
            </p>
          </div>

          <div className="bg-[#2a2a2a] rounded-lg border border-gray-700 p-4">
            <div className="flex items-center gap-2 mb-2">
              <Calendar className="w-5 h-5 text-purple-400" />
              <span className="text-sm font-medium text-white/70">Pending Review</span>
            </div>
            <p className="text-2xl font-bold">
              {contentQueue?.total_pending || 0}
            </p>
          </div>

          <div className="bg-[#2a2a2a] rounded-lg border border-gray-700 p-4">
            <div className="flex items-center gap-2 mb-2">
              <CheckCircle2 className="w-5 h-5 text-green-400" />
              <span className="text-sm font-medium text-white/70">Approved</span>
            </div>
            <p className="text-2xl font-bold">
              {contentQueue?.total_approved || 0}
            </p>
          </div>
        </div>

        {/* Pending Content */}
        {contentQueue && contentQueue.pending.length > 0 && (
          <div className="bg-[#2a2a2a] rounded-lg border border-gray-700 overflow-hidden">
            <div className="p-4 border-b border-gray-700">
              <h2 className="font-bold text-lg">Pending Content</h2>
              <p className="text-sm text-white/60">Review and approve AI-generated content</p>
            </div>

            <div className="divide-y divide-gray-700">
              {contentQueue.pending.map((content) => (
                <div key={content.id} className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <div className="flex items-center gap-2 mb-2">
                        <span className="px-3 py-1 bg-blue-500/20 text-blue-300 rounded-full text-xs font-medium border border-blue-500/50">
                          {content.platform}
                        </span>
                        <span className="px-3 py-1 bg-purple-500/20 text-purple-300 rounded-full text-xs font-medium border border-purple-500/50 capitalize">
                          {content.niche}
                        </span>
                        <span className="text-xs text-white/50">
                          Scheduled: {content.date}
                        </span>
                      </div>
                      <h3 className="font-bold text-lg">{content.hook}</h3>
                    </div>

                    <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                      content.viral_score >= 80 ? 'bg-green-500/20 text-green-300 border border-green-500/50' :
                      content.viral_score >= 60 ? 'bg-yellow-500/20 text-yellow-300 border border-yellow-500/50' :
                      'bg-gray-500/20 text-gray-300 border border-gray-500/50'
                    }`}>
                      {content.viral_score.toFixed(0)}% Viral
                    </span>
                  </div>

                  <div className="bg-[#1a1a1a] rounded-lg p-4 mb-4 border border-gray-700">
                    <pre className="whitespace-pre-wrap text-sm text-white/80">
                      {content.script}
                    </pre>
                  </div>

                  <div className="flex gap-3">
                    <button
                      onClick={() => approveContent(content.id)}
                      className="flex-1 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors font-medium flex items-center justify-center gap-2"
                    >
                      <CheckCircle2 className="w-4 h-4" />
                      Approve
                    </button>

                    <button
                      onClick={() => regenerateContent(content.id)}
                      className="px-4 py-2 border border-gray-600 text-white/90 rounded-lg hover:bg-[#2a2a2a] transition-colors"
                    >
                      <RefreshCw className="w-4 h-4" />
                    </button>

                    <button
                      onClick={() => rejectContent(content.id)}
                      className="px-4 py-2 border border-red-500/50 text-red-300 rounded-lg hover:bg-red-500/20 transition-colors"
                    >
                      <XCircle className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Empty State */}
        {contentQueue && contentQueue.pending.length === 0 && (
          <div className="bg-[#2a2a2a] rounded-lg border border-gray-700 p-12 text-center">
            <Calendar className="w-16 h-16 text-white/30 mx-auto mb-4" />
            <h3 className="text-lg font-medium mb-2">
              No pending content
            </h3>
            <p className="text-white/60">
              Your autopilot will generate new content tomorrow at 6:00 AM
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

