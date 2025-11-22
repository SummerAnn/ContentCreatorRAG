'use client';

import { useState, useEffect } from 'react';
import { 
  User, 
  Sparkles, 
  Target, 
  MessageSquare, 
  Calendar,
  Shield,
  Trash2,
  Save,
  Upload,
  CheckCircle2,
  AlertCircle,
  Settings as SettingsIcon,
  Loader2
} from 'lucide-react';

interface UserProfile {
  user_id: string;
  name?: string;
  creator_type?: string;
  primary_platforms: string[];
  secondary_platforms: string[];
  primary_niches: string[];
  target_audience?: {
    age?: string;
    gender?: string;
    interests?: string[];
  };
  audience_size?: string;
  brand_voice?: {
    tone?: string;
    energy?: string;
    uses_humor?: boolean;
    speaking_style?: string;
  };
  content_style?: string;
  personality_traits: string[];
  primary_goals: string[];
  posting_frequency?: string;
  avoid_topics: string[];
  preferred_video_length?: string;
  uses_face_on_camera?: boolean;
  onboarding_completed?: boolean;
}

export default function SettingsPage() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [activeTab, setActiveTab] = useState('profile');
  const [sampleTexts, setSampleTexts] = useState(['', '', '']);
  const [isAnalyzingVoice, setIsAnalyzingVoice] = useState(false);

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    const userId = localStorage.getItem('user_id') || 'default_user';

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/profile/${userId}`);
      if (response.ok) {
        const data = await response.json();
        setProfile({
          ...data,
          primary_platforms: data.primary_platforms || [],
          secondary_platforms: data.secondary_platforms || [],
          primary_niches: data.primary_niches || [],
          personality_traits: data.personality_traits || [],
          primary_goals: data.primary_goals || [],
          avoid_topics: data.avoid_topics || [],
          target_audience: data.target_audience || {},
          brand_voice: data.brand_voice || {}
        });
      }
    } catch (error) {
      console.error('Failed to load profile:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const saveProfile = async () => {
    if (!profile) return;
    
    setIsSaving(true);
    setSaveSuccess(false);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/profile/save`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...profile,
          profile_completed: true
        })
      });

      if (response.ok) {
        setSaveSuccess(true);
        setTimeout(() => setSaveSuccess(false), 3000);
      }
    } catch (error) {
      console.error('Failed to save profile:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const analyzeVoice = async () => {
    if (!profile) return;

    const validSamples = sampleTexts.filter(text => text.trim().length > 0);
    
    if (validSamples.length === 0) {
      alert('Please provide at least one sample text');
      return;
    }

    setIsAnalyzingVoice(true);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/profile/analyze-voice`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: profile.user_id,
          sample_texts: validSamples
        })
      });

      if (response.ok) {
        const data = await response.json();
        
        // Update profile with analyzed voice
        setProfile({
          ...profile,
          brand_voice: data.voice_analysis || profile.brand_voice,
          personality_traits: data.voice_analysis?.personality_traits || profile.personality_traits
        });

        alert('Voice analyzed! Your brand voice has been updated.');
        setSampleTexts(['', '', '']); // Clear samples
      }
    } catch (error) {
      console.error('Voice analysis failed:', error);
      alert('Failed to analyze voice. Please try again.');
    } finally {
      setIsAnalyzingVoice(false);
    }
  };

  const toggleArrayItem = (field: keyof UserProfile, value: string) => {
    if (!profile) return;
    
    const current = (profile[field] as string[]) || [];
    if (current.includes(value)) {
      setProfile({
        ...profile,
        [field]: current.filter(v => v !== value)
      });
    } else {
      setProfile({
        ...profile,
        [field]: [...current, value]
      });
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-[var(--background)]">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-[var(--accent)] mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Loading settings...</p>
        </div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-[var(--background)]">
        <div className="text-center bg-white dark:bg-[#1a1a1a] rounded-lg shadow-xl p-8 max-w-md">
          <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold mb-2 text-gray-800 dark:text-gray-200">No Profile Found</h2>
          <p className="text-gray-600 dark:text-gray-400 mb-4">Your profile will be created automatically when you save settings.</p>
        </div>
      </div>
    );
  }

  const platforms = [
    { id: 'tiktok', name: 'TikTok' },
    { id: 'youtube_short', name: 'YouTube Shorts' },
    { id: 'instagram_reel', name: 'Instagram Reels' },
    { id: 'youtube_long', name: 'YouTube Long' },
    { id: 'linkedin', name: 'LinkedIn' },
    { id: 'twitter', name: 'Twitter/X' }
  ];

  const niches = [
    'travel', 'food', 'tech', 'beauty', 'fitness', 'gaming',
    'education', 'finance', 'art', 'lifestyle', 'entertainment', 'pets'
  ];

  const goals = [
    { id: 'grow_followers', label: 'Grow Followers' },
    { id: 'monetization', label: 'Make Money' },
    { id: 'brand_deals', label: 'Get Brand Deals' },
    { id: 'build_authority', label: 'Build Authority' },
    { id: 'drive_traffic', label: 'Drive Traffic' },
    { id: 'community', label: 'Build Community' }
  ];

  return (
    <div className="min-h-screen bg-[var(--background)]">
      {/* Header */}
      <div className="bg-white dark:bg-[#1a1a1a] border-b luxury-border">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <SettingsIcon className="w-8 h-8 text-[var(--accent)]" />
              <div>
                <h1 className="text-3xl font-bold text-gray-800 dark:text-gray-200">Settings</h1>
                <p className="text-gray-600 dark:text-gray-400">Customize your CreatorFlow experience</p>
              </div>
            </div>
            
            <button
              onClick={saveProfile}
              disabled={isSaving}
              className="flex items-center gap-2 px-6 py-3 luxury-accent text-white rounded-lg hover:opacity-90 disabled:opacity-50 transition-all luxury-shadow"
            >
              {isSaving ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Saving...
                </>
              ) : saveSuccess ? (
                <>
                  <CheckCircle2 className="w-5 h-5" />
                  Saved!
                </>
              ) : (
                <>
                  <Save className="w-5 h-5" />
                  Save Changes
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="flex gap-6">
          {/* Sidebar */}
          <div className="w-64 flex-shrink-0">
            <div className="bg-white dark:bg-[#1a1a1a] rounded-lg shadow-sm luxury-border overflow-hidden">
              {[
                { id: 'profile', label: 'Profile Info', icon: User },
                { id: 'platforms', label: 'Platforms & Niches', icon: Target },
                { id: 'voice', label: 'Brand Voice', icon: MessageSquare },
                { id: 'goals', label: 'Goals & Preferences', icon: Calendar },
                { id: 'advanced', label: 'Advanced', icon: Shield }
              ].map(tab => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3 text-left transition-colors luxury-border ${
                    activeTab === tab.id
                      ? 'bg-[var(--accent)]/10 text-[var(--accent)] border-l-4 border-[var(--accent)]'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-[#2a2a2a]'
                  }`}
                >
                  <tab.icon className="w-5 h-5" />
                  {tab.label}
                </button>
              ))}
            </div>
          </div>

          {/* Main Content */}
          <div className="flex-1">
            <div className="bg-white dark:bg-[#1a1a1a] rounded-lg shadow-sm luxury-border p-8">
              
              {/* Profile Info Tab */}
              {activeTab === 'profile' && (
                <div className="space-y-6">
                  <h2 className="text-2xl font-bold mb-6 text-gray-800 dark:text-gray-200">Profile Information</h2>
                  
                  <div>
                    <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">Name / Brand Name</label>
                    <input
                      type="text"
                      value={profile.name || ''}
                      onChange={(e) => setProfile({...profile, name: e.target.value})}
                      className="w-full p-3 luxury-border bg-white dark:bg-[#1a1a1a] text-[var(--foreground)] rounded-lg focus:ring-2 focus:ring-[var(--accent)] focus:border-[var(--accent)] transition luxury-shadow"
                      placeholder="Your name or brand name"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">Creator Type</label>
                    <div className="grid grid-cols-3 gap-3">
                      {['solo_creator', 'business', 'agency'].map(type => (
                        <button
                          key={type}
                          onClick={() => setProfile({...profile, creator_type: type})}
                          className={`p-4 rounded-lg border-2 transition-all capitalize luxury-shadow ${
                            profile.creator_type === type
                              ? 'border-[var(--accent)] bg-[var(--accent)]/10'
                              : 'luxury-border hover:border-[var(--accent)]/50'
                          }`}
                        >
                          {type.replace('_', ' ').split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">Current Audience Size</label>
                    <select
                      value={profile.audience_size || ''}
                      onChange={(e) => setProfile({...profile, audience_size: e.target.value})}
                      className="w-full p-3 luxury-border bg-white dark:bg-[#1a1a1a] text-[var(--foreground)] rounded-lg focus:ring-2 focus:ring-[var(--accent)] transition luxury-shadow"
                    >
                      <option value="">Select range</option>
                      <option value="0-1k">0 - 1,000</option>
                      <option value="1k-10k">1,000 - 10,000</option>
                      <option value="10k-50k">10,000 - 50,000</option>
                      <option value="50k-100k">50,000 - 100,000</option>
                      <option value="100k+">100,000+</option>
                    </select>
                  </div>
                </div>
              )}

              {/* Platforms & Niches Tab */}
              {activeTab === 'platforms' && (
                <div className="space-y-6">
                  <h2 className="text-2xl font-bold mb-6 text-gray-800 dark:text-gray-200">Platforms & Niches</h2>
                  
                  <div>
                    <label className="block text-sm font-medium mb-3 text-gray-700 dark:text-gray-300">Primary Platforms</label>
                    <div className="grid grid-cols-3 gap-3">
                      {platforms.map(platform => (
                        <button
                          key={platform.id}
                          onClick={() => toggleArrayItem('primary_platforms', platform.id)}
                          className={`p-4 rounded-lg border-2 transition-all luxury-shadow ${
                            profile.primary_platforms.includes(platform.id)
                              ? 'border-[var(--accent)] bg-[var(--accent)]/10'
                              : 'luxury-border hover:border-[var(--accent)]/50'
                          }`}
                        >
                          <div className="text-sm font-medium">{platform.name}</div>
                        </button>
                      ))}
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-3 text-gray-700 dark:text-gray-300">Content Niches</label>
                    <div className="grid grid-cols-4 gap-2">
                      {niches.map(niche => (
                        <button
                          key={niche}
                          onClick={() => toggleArrayItem('primary_niches', niche)}
                          className={`p-3 rounded-lg border-2 transition-all text-sm capitalize luxury-shadow ${
                            profile.primary_niches.includes(niche)
                              ? 'border-[var(--accent)] bg-[var(--accent)]/10'
                              : 'luxury-border hover:border-[var(--accent)]/50'
                          }`}
                        >
                          {niche}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">Target Audience Age</label>
                    <select
                      value={profile.target_audience?.age || ''}
                      onChange={(e) => setProfile({
                        ...profile,
                        target_audience: {...profile.target_audience, age: e.target.value}
                      })}
                      className="w-full p-3 luxury-border bg-white dark:bg-[#1a1a1a] text-[var(--foreground)] rounded-lg focus:ring-2 focus:ring-[var(--accent)] transition luxury-shadow"
                    >
                      <option value="">Select age range</option>
                      <option value="13-17">13-17 (Gen Z)</option>
                      <option value="18-24">18-24 (Young Adults)</option>
                      <option value="25-34">25-34 (Millennials)</option>
                      <option value="35-44">35-44</option>
                      <option value="45+">45+</option>
                      <option value="all">All Ages</option>
                    </select>
                  </div>
                </div>
              )}

              {/* Brand Voice Tab */}
              {activeTab === 'voice' && (
                <div className="space-y-6">
                  <h2 className="text-2xl font-bold mb-6 text-gray-800 dark:text-gray-200">Brand Voice & Style</h2>
                  
                  <div>
                    <label className="block text-sm font-medium mb-3 text-gray-700 dark:text-gray-300">Content Tone</label>
                    <div className="grid grid-cols-3 gap-3">
                      {['casual', 'professional', 'friendly', 'humorous', 'authoritative'].map(tone => (
                        <button
                          key={tone}
                          onClick={() => setProfile({
                            ...profile,
                            brand_voice: {...profile.brand_voice, tone}
                          })}
                          className={`p-4 rounded-lg border-2 transition-all capitalize luxury-shadow ${
                            profile.brand_voice?.tone === tone
                              ? 'border-[var(--accent)] bg-[var(--accent)]/10'
                              : 'luxury-border hover:border-[var(--accent)]/50'
                          }`}
                        >
                          {tone}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-3 text-gray-700 dark:text-gray-300">Energy Level</label>
                    <div className="grid grid-cols-3 gap-3">
                      {['high', 'medium', 'calm'].map(energy => (
                        <button
                          key={energy}
                          onClick={() => setProfile({
                            ...profile,
                            brand_voice: {...profile.brand_voice, energy}
                          })}
                          className={`p-4 rounded-lg border-2 transition-all capitalize luxury-shadow ${
                            profile.brand_voice?.energy === energy
                              ? 'border-[var(--accent)] bg-[var(--accent)]/10'
                              : 'luxury-border hover:border-[var(--accent)]/50'
                          }`}
                        >
                          {energy}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="flex items-center gap-3 p-4 bg-gray-50 dark:bg-[#2a2a2a] rounded-lg">
                    <input
                      type="checkbox"
                      checked={profile.brand_voice?.uses_humor || false}
                      onChange={(e) => setProfile({
                        ...profile,
                        brand_voice: {...profile.brand_voice, uses_humor: e.target.checked}
                      })}
                      className="w-5 h-5 text-[var(--accent)]"
                    />
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300">I use humor in my content</label>
                  </div>

                  {/* Voice Analysis Section */}
                  <div className="border-t luxury-border pt-6 mt-6">
                    <h3 className="text-lg font-bold mb-3 flex items-center gap-2 text-gray-800 dark:text-gray-200">
                      <Sparkles className="w-5 h-5 text-[var(--accent)]" />
                      AI Voice Analysis
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                      Paste 3 examples of your content (captions, scripts, etc.) and we'll analyze your unique voice.
                    </p>
                    
                    {sampleTexts.map((text, i) => (
                      <div key={i} className="mb-3">
                        <label className="block text-xs font-medium mb-1 text-gray-700 dark:text-gray-300">Sample {i + 1}</label>
                        <textarea
                          value={text}
                          onChange={(e) => {
                            const newSamples = [...sampleTexts];
                            newSamples[i] = e.target.value;
                            setSampleTexts(newSamples);
                          }}
                          placeholder="Paste your content here..."
                          className="w-full p-3 luxury-border bg-white dark:bg-[#1a1a1a] text-[var(--foreground)] rounded-lg text-sm focus:ring-2 focus:ring-[var(--accent)] transition luxury-shadow"
                          rows={3}
                        />
                      </div>
                    ))}

                    <button
                      onClick={analyzeVoice}
                      disabled={isAnalyzingVoice}
                      className="w-full mt-4 px-4 py-3 luxury-accent text-white rounded-lg hover:opacity-90 transition-shadow disabled:opacity-50 flex items-center justify-center gap-2 luxury-shadow"
                    >
                      {isAnalyzingVoice ? (
                        <>
                          <Loader2 className="w-5 h-5 animate-spin" />
                          Analyzing Voice...
                        </>
                      ) : (
                        <>
                          <Sparkles className="w-5 h-5" />
                          Analyze My Voice
                        </>
                      )}
                    </button>
                  </div>
                </div>
              )}

              {/* Goals & Preferences Tab */}
              {activeTab === 'goals' && (
                <div className="space-y-6">
                  <h2 className="text-2xl font-bold mb-6 text-gray-800 dark:text-gray-200">Goals & Preferences</h2>
                  
                  <div>
                    <label className="block text-sm font-medium mb-3 text-gray-700 dark:text-gray-300">Primary Goals</label>
                    <div className="grid grid-cols-2 gap-3">
                      {goals.map(goal => (
                        <button
                          key={goal.id}
                          onClick={() => toggleArrayItem('primary_goals', goal.id)}
                          className={`p-4 rounded-lg border-2 transition-all text-left luxury-shadow ${
                            profile.primary_goals.includes(goal.id)
                              ? 'border-[var(--accent)] bg-[var(--accent)]/10'
                              : 'luxury-border hover:border-[var(--accent)]/50'
                          }`}
                        >
                          <div className="font-medium text-gray-800 dark:text-gray-200">{goal.label}</div>
                        </button>
                      ))}
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">Posting Frequency</label>
                    <select
                      value={profile.posting_frequency || ''}
                      onChange={(e) => setProfile({...profile, posting_frequency: e.target.value})}
                      className="w-full p-3 luxury-border bg-white dark:bg-[#1a1a1a] text-[var(--foreground)] rounded-lg focus:ring-2 focus:ring-[var(--accent)] transition luxury-shadow"
                    >
                      <option value="">Select frequency</option>
                      <option value="daily">Daily</option>
                      <option value="3x_week">3x per week</option>
                      <option value="weekly">Weekly</option>
                      <option value="occasional">Occasional</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">Preferred Video Length</label>
                    <select
                      value={profile.preferred_video_length || ''}
                      onChange={(e) => setProfile({...profile, preferred_video_length: e.target.value})}
                      className="w-full p-3 luxury-border bg-white dark:bg-[#1a1a1a] text-[var(--foreground)] rounded-lg focus:ring-2 focus:ring-[var(--accent)] transition luxury-shadow"
                    >
                      <option value="">Select length</option>
                      <option value="15-30s">15-30 seconds</option>
                      <option value="30-60s">30-60 seconds</option>
                      <option value="60-90s">60-90 seconds</option>
                      <option value="90s+">90+ seconds</option>
                    </select>
                  </div>

                  <div className="flex items-center gap-3 p-4 bg-gray-50 dark:bg-[#2a2a2a] rounded-lg">
                    <input
                      type="checkbox"
                      checked={profile.uses_face_on_camera || false}
                      onChange={(e) => setProfile({...profile, uses_face_on_camera: e.target.checked})}
                      className="w-5 h-5 text-[var(--accent)]"
                    />
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300">I show my face on camera</label>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">Topics to Avoid (comma-separated)</label>
                    <input
                      type="text"
                      value={profile.avoid_topics.join(', ')}
                      onChange={(e) => setProfile({
                        ...profile,
                        avoid_topics: e.target.value.split(',').map(t => t.trim()).filter(Boolean)
                      })}
                      placeholder="politics, religion, controversial topics"
                      className="w-full p-3 luxury-border bg-white dark:bg-[#1a1a1a] text-[var(--foreground)] rounded-lg focus:ring-2 focus:ring-[var(--accent)] transition luxury-shadow"
                    />
                  </div>
                </div>
              )}

              {/* Advanced Tab */}
              {activeTab === 'advanced' && (
                <div className="space-y-6">
                  <h2 className="text-2xl font-bold mb-6 text-gray-800 dark:text-gray-200">Advanced Settings</h2>
                  
                  <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
                    <h3 className="font-medium text-yellow-800 dark:text-yellow-200 mb-2">⚠️ Warning</h3>
                    <p className="text-sm text-yellow-700 dark:text-yellow-300">
                      These actions cannot be undone. Please be careful.
                    </p>
                  </div>

                  <div className="border luxury-border rounded-lg p-6">
                    <h3 className="font-medium mb-2 text-gray-800 dark:text-gray-200">Reset Profile</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                      This will mark your profile as incomplete.
                    </p>
                    <button
                      onClick={() => {
                        if (confirm('Are you sure you want to reset your profile?')) {
                          setProfile({...profile, onboarding_completed: false});
                          saveProfile();
                        }
                      }}
                      className="px-4 py-2 bg-yellow-500 hover:bg-yellow-600 text-white rounded-lg transition"
                    >
                      Reset Profile
                    </button>
                  </div>

                  <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                    <h3 className="font-medium text-blue-800 dark:text-blue-200 mb-2">📊 Your Data</h3>
                    <p className="text-sm text-blue-700 dark:text-blue-300 mb-3">
                      Your profile data is stored locally and used to personalize content generation.
                    </p>
                    <button
                      onClick={() => {
                        const dataStr = JSON.stringify(profile, null, 2);
                        const blob = new Blob([dataStr], { type: 'application/json' });
                        const url = URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = 'creatorflow-profile.json';
                        a.click();
                      }}
                      className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg flex items-center gap-2 transition"
                    >
                      <Upload className="w-4 h-4" />
                      Export Profile Data
                    </button>
                  </div>
                </div>
              )}

            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

