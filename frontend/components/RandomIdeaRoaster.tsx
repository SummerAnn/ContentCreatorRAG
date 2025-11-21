'use client';

import { useState } from 'react';
import { X, Sparkles, Loader2 } from 'lucide-react';

interface RandomIdeaRoasterProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectIdea: (idea: { platform: string; niche: string; personality: string; audience: string[]; reference: string }) => void;
}

const platformOptions = ['youtube_short', 'youtube', 'tiktok', 'instagram_reel', 'instagram_carousel', 'linkedin'];
const nicheOptions = ['fitness', 'cooking', 'travel', 'tech', 'beauty', 'education', 'business', 'lifestyle', 'gaming', 'music', 'fashion', 'health', 'finance', 'relationship', 'comedy'];
const personalityOptions = ['friendly', 'educational', 'motivational', 'funny', 'rage_bait', 'storytelling', 'authentic', 'luxury', 'minimalist', 'energetic', 'calm', 'quirky', 'professional', 'relatable'];
const audienceOptions = ['gen_z', 'millennials', 'gen_x', 'professionals', 'students', 'parents', 'creators', 'general'];
const genderOptions = ['female', 'male', 'all'];

const ideaTemplates = [
  { topic: 'morning routine', niches: ['lifestyle', 'productivity', 'health'] },
  { topic: 'product review', niches: ['tech', 'beauty', 'fashion'] },
  { topic: 'travel vlog', niches: ['travel', 'lifestyle'] },
  { topic: 'recipe tutorial', niches: ['cooking', 'lifestyle'] },
  { topic: 'workout challenge', niches: ['fitness', 'health'] },
  { topic: 'tech tutorial', niches: ['tech', 'education'] },
  { topic: 'beauty transformation', niches: ['beauty', 'lifestyle'] },
  { topic: 'budget tips', niches: ['finance', 'lifestyle', 'education'] },
  { topic: 'study methods', niches: ['education', 'productivity'] },
  { topic: 'career advice', niches: ['business', 'education'] },
  { topic: 'dating tips', niches: ['relationship', 'lifestyle'] },
  { topic: 'gaming highlight', niches: ['gaming', 'entertainment'] },
  { topic: 'music reaction', niches: ['music', 'entertainment'] },
  { topic: 'fashion haul', niches: ['fashion', 'lifestyle'] },
  { topic: 'home organization', niches: ['lifestyle', 'productivity'] },
];

export default function RandomIdeaRoaster({ isOpen, onClose, onSelectIdea }: RandomIdeaRoasterProps) {
  const [isGenerating, setIsGenerating] = useState(false);
  const [currentIdea, setCurrentIdea] = useState<any>(null);

  const generateRandomIdea = async () => {
    setIsGenerating(true);
    
    // Simulate generation delay for UX
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // Random selections
    const platform = platformOptions[Math.floor(Math.random() * platformOptions.length)];
    const template = ideaTemplates[Math.floor(Math.random() * ideaTemplates.length)];
    const niche = template.niches[Math.floor(Math.random() * template.niches.length)];
    const personality = personalityOptions[Math.floor(Math.random() * personalityOptions.length)];
    
    // Select 1-2 random audiences
    const numAudiences = Math.floor(Math.random() * 2) + 1;
    const selectedAudiences = [];
    const shuffledAudiences = [...audienceOptions].sort(() => 0.5 - Math.random());
    for (let i = 0; i < numAudiences && i < shuffledAudiences.length; i++) {
      selectedAudiences.push(shuffledAudiences[i]);
    }
    
    // Add gender
    const gender = genderOptions[Math.floor(Math.random() * genderOptions.length)];
    const audiences = [...selectedAudiences, gender];
    
    // Generate reference based on template and niche
    const references = [
      `${template.topic} for ${niche} enthusiasts`,
      `${template.topic} in the ${niche} space`,
      `Creative ${template.topic} ideas for ${niche}`,
      `${template.topic} with a ${personality} twist for ${niche}`,
      `${niche} content: ${template.topic} edition`,
    ];
    const reference = references[Math.floor(Math.random() * references.length)];
    
    const idea = {
      platform,
      niche,
      personality,
      audience: audiences,
      reference,
      goal: 'viral_reach'
    };
    
    setCurrentIdea(idea);
    setIsGenerating(false);
  };

  const handleUseIdea = () => {
    if (currentIdea) {
      onSelectIdea(currentIdea);
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white dark:bg-gray-900 rounded-lg shadow-lg w-full max-w-md flex flex-col">
        <div className="flex justify-between items-center p-4 border-b border-gray-200 dark:border-gray-800">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-[var(--accent)]" />
            <h2 className="text-xl font-bold text-gray-800 dark:text-gray-200">Random Idea Roaster</h2>
          </div>
          <button 
            onClick={onClose} 
            className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
          >
            <X size={24} />
          </button>
        </div>

        <div className="p-6 flex-1">
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
            Get a random content idea combination to spark your creativity!
          </p>

          {!currentIdea && !isGenerating && (
            <button
              onClick={generateRandomIdea}
              className="w-full px-4 py-3 luxury-accent hover:opacity-90 text-white rounded-xl transition-all font-medium flex items-center justify-center gap-2 luxury-shadow"
            >
              <Sparkles className="w-5 h-5" />
              Generate Random Idea
            </button>
          )}

          {isGenerating && (
            <div className="flex items-center justify-center gap-2 py-8">
                  <Loader2 className="w-5 h-5 animate-spin text-[var(--accent)]" />
              <span className="text-gray-600 dark:text-gray-400">Generating idea...</span>
            </div>
          )}

          {currentIdea && !isGenerating && (
            <div className="space-y-4">
              <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 space-y-3">
                <div>
                  <span className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">Platform</span>
                  <p className="text-sm font-medium text-gray-800 dark:text-gray-200 capitalize">
                    {currentIdea.platform.replace('_', ' ')}
                  </p>
                </div>
                
                <div>
                  <span className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">Niche</span>
                  <p className="text-sm font-medium text-gray-800 dark:text-gray-200 capitalize">{currentIdea.niche}</p>
                </div>
                
                <div>
                  <span className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">Personality</span>
                  <p className="text-sm font-medium text-gray-800 dark:text-gray-200 capitalize">
                    {currentIdea.personality.replace('_', ' ')}
                  </p>
                </div>
                
                <div>
                  <span className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">Audience</span>
                  <p className="text-sm font-medium text-gray-800 dark:text-gray-200">
                    {currentIdea.audience.map((a: string) => a.replace('_', ' ')).join(', ')}
                  </p>
                </div>
                
                <div>
                  <span className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">Idea</span>
                  <p className="text-sm text-gray-700 dark:text-gray-300">{currentIdea.reference}</p>
                </div>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={generateRandomIdea}
                  className="flex-1 px-4 py-2 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 rounded-lg transition"
                >
                  Generate Another
                </button>
                <button
                  onClick={handleUseIdea}
                  className="flex-1 px-4 py-2 luxury-accent hover:opacity-90 text-white rounded-xl transition-all font-medium luxury-shadow"
                >
                  Use This Idea
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

