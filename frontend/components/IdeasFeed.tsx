'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { Sparkles, TrendingUp, Users, Zap, Heart, MessageCircle, BarChart3, RefreshCw, X } from 'lucide-react';

interface IdeaCard {
  id: string;
  idea: string;
  platform: string;
  niche: string;
  hook_preview: string;
  viral_score: number;
  category: 'trending' | 'saved' | 'competitor' | 'wildcard';
  timestamp: string;
  source: string;
}

export default function IdeasFeed({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  const [ideas, setIdeas] = useState<IdeaCard[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const [niche, setNiche] = useState('lifestyle');
  const [platform, setPlatform] = useState('tiktok');
  
  const observerRef = useRef<IntersectionObserver | null>(null);
  const loadMoreRef = useRef<HTMLDivElement | null>(null);

  // Fetch ideas
  const fetchIdeas = async (reset = false) => {
    if (isLoading || (!hasMore && !reset)) return;
    
    setIsLoading(true);
    const currentOffset = reset ? 0 : offset;
    
    try {
      const response = await fetch(
        `http://localhost:8000/api/ideas-feed/generate?niche=${niche}&platform=${platform}&limit=20&offset=${currentOffset}`
      );
      const data = await response.json();
      
      if (reset) {
        setIdeas(data.ideas);
        setOffset(20);
      } else {
        setIdeas(prev => [...prev, ...data.ideas]);
        setOffset(prev => prev + 20);
      }
      
      setHasMore(data.has_more);
    } catch (error) {
      console.error('Failed to fetch ideas:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Initial load
  useEffect(() => {
    if (isOpen) {
      fetchIdeas(true);
    }
  }, [niche, platform, isOpen]);

  // Infinite scroll
  useEffect(() => {
    if (!isOpen) return;

    observerRef.current = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && hasMore && !isLoading) {
          fetchIdeas();
        }
      },
      { threshold: 0.1 }
    );

    if (loadMoreRef.current) {
      observerRef.current.observe(loadMoreRef.current);
    }

    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, [hasMore, isLoading, offset, isOpen]);

  // Category icons
  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'trending': return <TrendingUp className="w-4 h-4" />;
      case 'saved': return <Heart className="w-4 h-4" />;
      case 'competitor': return <Users className="w-4 h-4" />;
      case 'wildcard': return <Zap className="w-4 h-4" />;
      default: return <Sparkles className="w-4 h-4" />;
    }
  };

  // Category colors
  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'trending': return 'bg-red-100 text-red-700 border-red-200';
      case 'saved': return 'bg-purple-100 text-purple-700 border-purple-200';
      case 'competitor': return 'bg-blue-100 text-blue-700 border-blue-200';
      case 'wildcard': return 'bg-yellow-100 text-yellow-700 border-yellow-200';
      default: return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  // Save idea
  const saveIdea = async (ideaId: string) => {
    try {
      await fetch('http://localhost:8000/api/ideas-feed/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ idea_id: ideaId, user_id: 'demo_user' })
      });
      // Show success toast
      alert('Idea saved to swipe file!');
    } catch (error) {
      console.error('Failed to save idea:', error);
    }
  };

  // Develop idea
  const developIdea = async (idea: IdeaCard) => {
    try {
      // Send to chat interface
      window.location.href = `/chat?idea=${encodeURIComponent(idea.idea)}&niche=${idea.niche}&platform=${idea.platform}`;
    } catch (error) {
      console.error('Failed to develop idea:', error);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-[#1a1a1a] rounded-lg shadow-xl max-w-6xl w-full p-6 text-white max-h-[90vh] flex flex-col">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <Sparkles size={28} />
            Content Ideas Feed
          </h2>
          <div className="flex gap-2">
            <button
              onClick={() => fetchIdeas(true)}
              className="text-white/70 hover:text-white transition-colors p-2 hover:bg-white/10 rounded-lg"
              title="Refresh ideas"
            >
              <RefreshCw size={20} />
            </button>
            <button onClick={onClose} className="text-white/70 hover:text-white transition-colors">
              <X size={24} />
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className="flex gap-3 mb-6">
          <select
            value={niche}
            onChange={(e) => setNiche(e.target.value)}
            className="px-4 py-2 bg-[#2a2a2a] border border-gray-700 rounded-lg text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          >
            <option value="lifestyle">Lifestyle</option>
            <option value="beauty">Beauty</option>
            <option value="fashion">Fashion</option>
            <option value="business">Business</option>
            <option value="finance">Finance</option>
            <option value="education">Education</option>
            <option value="gaming">Gaming</option>
            <option value="entertainment">Entertainment</option>
            <option value="travel">Travel</option>
            <option value="food">Food</option>
            <option value="tech">Tech</option>
            <option value="fitness">Fitness</option>
          </select>

          <select
            value={platform}
            onChange={(e) => setPlatform(e.target.value)}
            className="px-4 py-2 bg-[#2a2a2a] border border-gray-700 rounded-lg text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          >
            <option value="tiktok">TikTok</option>
            <option value="instagram">Instagram</option>
            <option value="youtube">YouTube</option>
          </select>
        </div>

        {/* Ideas Feed */}
        <div className="flex-1 overflow-y-auto">
          <div className="space-y-4">
            {ideas.map((idea, index) => (
              <div
                key={`${idea.id}-${index}`}
                className="bg-[#2a2a2a] rounded-lg border border-gray-700 p-6 hover:border-purple-500/50 transition-all"
              >
                {/* Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium border flex items-center gap-1 ${
                      idea.category === 'trending' ? 'bg-red-500/20 text-red-300 border-red-500/50' :
                      idea.category === 'saved' ? 'bg-purple-500/20 text-purple-300 border-purple-500/50' :
                      idea.category === 'competitor' ? 'bg-blue-500/20 text-blue-300 border-blue-500/50' :
                      'bg-yellow-500/20 text-yellow-300 border-yellow-500/50'
                    }`}>
                      {getCategoryIcon(idea.category)}
                      {idea.category}
                    </span>
                    <span className="text-xs text-white/60">{idea.source}</span>
                  </div>
                  
                  <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                    idea.viral_score >= 80 ? 'bg-green-500/20 text-green-300 border border-green-500/50' :
                    idea.viral_score >= 60 ? 'bg-yellow-500/20 text-yellow-300 border border-yellow-500/50' :
                    'bg-gray-500/20 text-gray-300 border border-gray-500/50'
                  }`}>
                    {idea.viral_score.toFixed(0)}% Viral
                  </span>
                </div>

                {/* Content */}
                <h3 className="text-lg font-bold text-white mb-2">
                  {idea.idea}
                </h3>
                
                <p className="text-sm text-white/70 mb-4">
                  {idea.hook_preview}
                </p>

                {/* Meta */}
                <div className="flex items-center gap-4 text-xs text-white/50 mb-4">
                  <span className="flex items-center gap-1">
                    <BarChart3 className="w-3 h-3" />
                    {idea.platform}
                  </span>
                  <span>•</span>
                  <span>{idea.niche}</span>
                </div>

                {/* Actions */}
                <div className="flex gap-3">
                  <button
                    onClick={() => developIdea(idea)}
                    className="flex-1 px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition-colors font-medium"
                  >
                    Develop with AI
                  </button>
                  
                  <button
                    onClick={() => saveIdea(idea.id)}
                    className="px-4 py-2 border border-purple-500 text-purple-400 rounded-lg hover:bg-purple-500/20 transition-colors"
                  >
                    <Heart className="w-5 h-5" />
                  </button>
                </div>
              </div>
            ))}

            {/* Loading indicator */}
            {isLoading && (
              <div className="flex justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-purple-500"></div>
              </div>
            )}

            {/* Load more trigger */}
            <div ref={loadMoreRef} className="h-4"></div>

            {/* End message */}
            {!hasMore && ideas.length > 0 && (
              <div className="text-center py-8 text-white/60">
                <p>You've seen all ideas. Refresh for more!</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

