'use client';

import { useState } from 'react';
import { X, Settings, RefreshCw } from 'lucide-react';
import PlatformSelector from './PlatformSelector';
import PersonalitySelector from './PersonalitySelector';
import AudienceSelector from './AudienceSelector';
import ReferenceInput from './ReferenceInput';

interface SettingsPanelProps {
  isOpen: boolean;
  onClose: () => void;
  platform: string;
  niche: string;
  goal: string;
  personality: string;
  audience: string[];
  reference: string;
  hasVoiceover: boolean;
  userId?: string;
  onSave: (settings: {
    platform: string;
    niche: string;
    goal: string;
    personality: string;
    audience: string[];
    reference: string;
    hasVoiceover: boolean;
  }) => void;
  onRegenerate?: () => void;
}

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

export default function SettingsPanel({
  isOpen,
  onClose,
  platform: initialPlatform,
  niche: initialNiche,
  goal: initialGoal,
  personality: initialPersonality,
  audience: initialAudience,
  reference: initialReference,
  hasVoiceover: initialHasVoiceover,
  userId = 'default_user',
  onSave,
  onRegenerate
}: SettingsPanelProps) {
  const [platform, setPlatform] = useState(initialPlatform);
  const [niche, setNiche] = useState(initialNiche);
  const [goal, setGoal] = useState(initialGoal);
  const [personality, setPersonality] = useState(initialPersonality);
  const [audience, setAudience] = useState(initialAudience);
  const [reference, setReference] = useState(initialReference);
  const [hasVoiceover, setHasVoiceover] = useState(initialHasVoiceover);

  const handleSave = async () => {
    // Save to backend profile (async, non-blocking)
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      await fetch(`${apiUrl}/api/profile/save-settings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          platform,
          niche,
          goal,
          personality,
          audience,
          has_voiceover: hasVoiceover
        }),
      });
    } catch (error) {
      console.error('Failed to save profile:', error);
      // Don't block save if profile save fails
    }
    
    onSave({
      platform,
      niche,
      goal,
      personality,
      audience,
      reference,
      hasVoiceover
    });
    onClose();
  };

  const handleSaveAndRegenerate = () => {
    handleSave();
    if (onRegenerate) {
      // Small delay to ensure state is updated
      setTimeout(() => {
        onRegenerate();
      }, 100);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white dark:bg-gray-900 rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b border-gray-200 dark:border-gray-800">
          <div className="flex items-center gap-3">
            <Settings className="w-6 h-6 text-[var(--accent)]" />
            <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-200">Content Settings</h2>
            <span className="text-sm text-gray-500 dark:text-gray-400">
              Adjust your settings - these will be saved as your defaults
            </span>
          </div>
          <button 
            onClick={onClose} 
            className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition"
          >
            <X size={24} />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Platform */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
              Platform *
            </label>
            <PlatformSelector value={platform} onChange={setPlatform} />
          </div>

          {/* Niche */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Niche *
            </label>
            <input
              type="text"
              value={niche}
              onChange={(e) => setNiche(e.target.value)}
              placeholder="e.g., travel, food, tech, beauty"
              className="w-full p-3 luxury-border bg-white dark:bg-[#1a1a1a] text-[var(--foreground)] rounded-lg focus:ring-2 focus:ring-[var(--accent)] focus:border-[var(--accent)] transition luxury-shadow"
            />
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Add keywords or topics: e.g., "beauty skincare routine morning"
            </p>
          </div>

          {/* Personality */}
          <PersonalitySelector personality={personality} onChange={setPersonality} />

          {/* Audience */}
          <AudienceSelector audience={audience} onChange={setAudience} />

          {/* Goal */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Content Goal *
            </label>
            <select
              value={goal}
              onChange={(e) => setGoal(e.target.value)}
              className="w-full p-3 luxury-border bg-white dark:bg-[#1a1a1a] text-[var(--foreground)] rounded-lg focus:ring-2 focus:ring-[var(--accent)] focus:border-[var(--accent)] transition luxury-shadow"
            >
              {goals.map((g) => (
                <option key={g.id} value={g.id}>{g.label}</option>
              ))}
            </select>
          </div>

          {/* Reference */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Reference / Content Idea
            </label>
            <ReferenceInput value={reference} onChange={setReference} />
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
              Add more keywords, details, or modify your content idea here
            </p>
          </div>

          {/* Voiceover / Talking Option */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
              Audio Style *
            </label>
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={() => setHasVoiceover(true)}
                className={`
                  p-4 border-2 rounded-xl text-left transition-all luxury-shadow
                  ${hasVoiceover
                    ? 'border-[var(--accent)] bg-[var(--accent)]/10 dark:bg-[var(--accent)]/20'
                    : 'luxury-border hover:border-[var(--accent)]/50 bg-white dark:bg-[#1a1a1a]'
                  }
                `}
              >
                <div className="font-semibold text-sm text-gray-800 dark:text-gray-200 mb-1">
                  With Voiceover / Talking
                </div>
                <div className="text-xs text-gray-600 dark:text-gray-400">
                  Script includes spoken narration, voiceover, or talking. Perfect for tutorials, explanations, and storytelling.
                </div>
              </button>
              <button
                onClick={() => setHasVoiceover(false)}
                className={`
                  p-4 border-2 rounded-xl text-left transition-all luxury-shadow
                  ${!hasVoiceover
                    ? 'border-[var(--accent)] bg-[var(--accent)]/10 dark:bg-[var(--accent)]/20'
                    : 'luxury-border hover:border-[var(--accent)]/50 bg-white dark:bg-[#1a1a1a]'
                  }
                `}
              >
                <div className="font-semibold text-sm text-gray-800 dark:text-gray-200 mb-1">
                  No Talking / Silent
                </div>
                <div className="text-xs text-gray-600 dark:text-gray-400">
                  Text overlays, captions, and music only. No voiceover. Great for aesthetic content, ASMR, or music-focused videos.
                </div>
              </button>
            </div>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="border-t border-gray-200 dark:border-gray-800 p-6 flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 px-6 py-3 bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="flex-1 px-6 py-3 bg-[var(--accent)] text-white rounded-lg hover:opacity-90 transition luxury-shadow"
          >
            Save Settings
          </button>
          {onRegenerate && (
            <button
              onClick={handleSaveAndRegenerate}
              className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition flex items-center justify-center gap-2 luxury-shadow"
            >
              <RefreshCw className="w-4 h-4" />
              Save & Regenerate
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

