'use client';

import { useState } from 'react';
import { Sparkles, TrendingUp, AlertCircle, X, Copy, Check } from 'lucide-react';
import { generateViralTitles, detectTrends, getNicheTrends, type TitleRequest } from '../lib/api';

interface ViralTitleGeneratorProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function ViralTitleGenerator({ isOpen, onClose }: ViralTitleGeneratorProps) {
  const [topic, setTopic] = useState('');
  const [platform, setPlatform] = useState('tiktok');
  const [niche, setNiche] = useState('');
  const [vibe, setVibe] = useState('pov');
  const [titles, setTitles] = useState<any[]>([]);
  const [trends, setTrends] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingTrends, setIsLoadingTrends] = useState(false);
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  const generateTitles = async () => {
    if (!topic.trim()) {
      alert('Please enter a topic');
      return;
    }

    setIsLoading(true);
    setTitles([]);
    
    try {
      const request: TitleRequest = {
        topic: topic.trim(),
        platform,
        niche: niche.trim() || 'general',
        vibe
      };
      
      const data = await generateViralTitles(request);
      setTitles(data.titles || []);
    } catch (error) {
      console.error('Failed to generate titles:', error);
      alert(`Failed to generate titles: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsLoading(false);
    }
  };

  const getTrends = async () => {
    if (!niche.trim()) {
      alert('Please enter a niche to get trends');
      return;
    }

    setIsLoadingTrends(true);
    
    try {
      const data = await detectTrends({
        platform,
        niche: niche.trim(),
        region: 'US'
      });
      setTrends(data);
    } catch (error) {
      console.error('Failed to get trends:', error);
      alert(`Failed to get trends: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsLoadingTrends(false);
    }
  };

  const copyToClipboard = async (text: string, index: number) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedIndex(index);
      setTimeout(() => setCopiedIndex(null), 2000);
    } catch (error) {
      console.error('Failed to copy:', error);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white dark:bg-[#1a1a1a] rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white dark:bg-[#1a1a1a] border-b border-gray-200 dark:border-gray-700 p-6 flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Viral Title Generator</h2>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              Generate titles that actually go viral using proven patterns
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
          >
            <X size={24} />
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* Trend Alert */}
          {trends && trends.ai_analysis && trends.ai_analysis.trending_now && (
            <div className="p-4 bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg">
              <div className="flex items-center gap-2 mb-3">
                <TrendingUp className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                <h3 className="font-bold text-purple-900 dark:text-purple-300">Trending Now</h3>
              </div>
              <div className="space-y-2">
                {trends.ai_analysis.trending_now.slice(0, 3).map((trend: any, i: number) => (
                  <div key={i} className="text-sm text-purple-800 dark:text-purple-200">
                    <span className="font-medium">{trend.topic}</span>
                    <span className="text-purple-600 dark:text-purple-400"> - {trend.why_trending}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Input Form */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Topic
              </label>
              <input
                type="text"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="e.g., dark academia study playlist"
                className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-[#0f0f0f] text-gray-900 dark:text-white"
                onKeyPress={(e) => e.key === 'Enter' && generateTitles()}
              />
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Platform
                </label>
                <select
                  value={platform}
                  onChange={(e) => setPlatform(e.target.value)}
                  className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-[#0f0f0f] text-gray-900 dark:text-white"
                >
                  <option value="tiktok">TikTok</option>
                  <option value="youtube">YouTube</option>
                  <option value="instagram">Instagram</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Vibe
                </label>
                <select
                  value={vibe}
                  onChange={(e) => setVibe(e.target.value)}
                  className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-[#0f0f0f] text-gray-900 dark:text-white"
                >
                  <option value="pov">POV</option>
                  <option value="aesthetic">Aesthetic</option>
                  <option value="story">Story</option>
                  <option value="simple">Simple</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Niche
                </label>
                <input
                  type="text"
                  value={niche}
                  onChange={(e) => setNiche(e.target.value)}
                  placeholder="e.g., dark academia"
                  className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-[#0f0f0f] text-gray-900 dark:text-white"
                />
              </div>

              <div className="flex items-end">
                <button
                  onClick={getTrends}
                  disabled={isLoadingTrends || !niche.trim()}
                  className="w-full px-4 py-3 border border-purple-500 text-purple-600 dark:text-purple-400 rounded-lg hover:bg-purple-50 dark:hover:bg-purple-900/20 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {isLoadingTrends ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-purple-600"></div>
                      Loading...
                    </>
                  ) : (
                    <>
                      <TrendingUp className="w-4 h-4" />
                      Trends
                    </>
                  )}
                </button>
              </div>
            </div>

            <button
              onClick={generateTitles}
              disabled={isLoading || !topic.trim()}
              className="w-full px-6 py-3 bg-purple-500 text-white rounded-lg hover:bg-purple-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-white"></div>
                  Generating...
                </>
              ) : (
                <>
                  <Sparkles className="w-5 h-5" />
                  Generate Viral Titles
                </>
              )}
            </button>
          </div>

          {/* Generated Titles */}
          {titles.length > 0 && (
            <div className="space-y-3 mt-6">
              <h3 className="font-bold text-lg text-gray-900 dark:text-white">
                Generated Titles (Ranked by Virality)
              </h3>
              {titles.map((item, i) => (
                <div
                  key={i}
                  className="p-4 border-2 border-gray-200 dark:border-gray-700 rounded-lg hover:border-purple-300 dark:hover:border-purple-600 transition-all cursor-pointer group"
                >
                  <div className="flex items-start justify-between mb-2">
                    <span className="font-medium text-lg text-gray-900 dark:text-white flex-1 pr-4">
                      {item.title}
                    </span>
                    <div className="flex items-center gap-2">
                      <span className={`px-3 py-1 rounded-full text-sm font-bold ${
                        item.viral_score >= 80 ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400' :
                        item.viral_score >= 60 ? 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400' :
                        'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400'
                      }`}>
                        {item.viral_score.toFixed(0)}% Viral
                      </span>
                      <button
                        onClick={() => copyToClipboard(item.title, i)}
                        className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                        title="Copy title"
                      >
                        {copiedIndex === i ? (
                          <Check className="w-4 h-4 text-green-600 dark:text-green-400" />
                        ) : (
                          <Copy className="w-4 h-4 text-gray-500 dark:text-gray-400" />
                        )}
                      </button>
                    </div>
                  </div>
                  
                  {item.viral_score < 60 && (
                    <div className="flex items-start gap-2 mt-2 p-2 bg-yellow-50 dark:bg-yellow-900/20 rounded text-sm">
                      <AlertCircle className="w-4 h-4 text-yellow-600 dark:text-yellow-400 mt-0.5 flex-shrink-0" />
                      <span className="text-yellow-700 dark:text-yellow-300">
                        Low viral score - Consider using more casual language or adding POV
                      </span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

