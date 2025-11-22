'use client';

import { useState, useEffect } from 'react';
import { X, Sparkles, Loader2, Filter } from 'lucide-react';

interface TemplateLibraryProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectTemplate: (template: { id: string; name: string; description: string; platforms: string[]; niches: string[] }) => void;
}

interface Template {
  id: string;
  name: string;
  description: string;
  category: string;
  platforms: string[];
  niches: string[];
}

export default function TemplateLibrary({ isOpen, onClose, onSelectTemplate }: TemplateLibraryProps) {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [filteredTemplates, setFilteredTemplates] = useState<Template[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedPlatform, setSelectedPlatform] = useState<string>('');
  const [selectedNiche, setSelectedNiche] = useState<string>('');
  const [selectedCategory, setSelectedCategory] = useState<string>('');

  useEffect(() => {
    if (isOpen) {
      loadTemplates();
    }
  }, [isOpen]);

  useEffect(() => {
    filterTemplates();
  }, [templates, selectedPlatform, selectedNiche, selectedCategory]);

  const loadTemplates = async () => {
    setIsLoading(true);
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const params = new URLSearchParams();
      if (selectedPlatform) params.append('platform', selectedPlatform);
      if (selectedNiche) params.append('niche', selectedNiche);
      if (selectedCategory) params.append('category', selectedCategory);

      const response = await fetch(`${apiUrl}/api/templates/?${params.toString()}`);
      if (response.ok) {
        const data = await response.json();
        setTemplates(data.templates || []);
      }
    } catch (error) {
      console.error('Error loading templates:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const filterTemplates = () => {
    let filtered = templates;

    if (selectedPlatform) {
      filtered = filtered.filter(t => t.platforms.includes(selectedPlatform));
    }
    if (selectedNiche) {
      filtered = filtered.filter(t => t.niches.includes(selectedNiche));
    }
    if (selectedCategory) {
      filtered = filtered.filter(t => t.category === selectedCategory);
    }

    setFilteredTemplates(filtered);
  };

  const handleUseTemplate = (template: Template) => {
    onSelectTemplate(template);
    onClose();
  };

  const categories = Array.from(new Set(templates.map(t => t.category)));

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white dark:bg-gray-900 rounded-lg shadow-xl w-full max-w-6xl max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b border-gray-200 dark:border-gray-800">
          <div className="flex items-center gap-3">
            <Sparkles className="w-6 h-6 text-[var(--accent)]" />
            <div>
              <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-200">Template Library</h2>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                {filteredTemplates.length} ready-to-use templates for instant content creation
              </p>
            </div>
          </div>
          <button 
            onClick={onClose} 
            className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition"
          >
            <X size={24} />
          </button>
        </div>

        {/* Filters */}
        <div className="p-4 border-b border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-800">
          <div className="flex items-center gap-4 flex-wrap">
            <div className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-gray-500" />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Filters:</span>
            </div>
            
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-sm"
            >
              <option value="">All Categories</option>
              {categories.map(cat => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>

            <input
              type="text"
              placeholder="Filter by platform..."
              value={selectedPlatform}
              onChange={(e) => setSelectedPlatform(e.target.value)}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-sm flex-1 max-w-xs"
            />

            <input
              type="text"
              placeholder="Filter by niche..."
              value={selectedNiche}
              onChange={(e) => setSelectedNiche(e.target.value)}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-sm flex-1 max-w-xs"
            />

            {(selectedPlatform || selectedNiche || selectedCategory) && (
              <button
                onClick={() => {
                  setSelectedPlatform('');
                  setSelectedNiche('');
                  setSelectedCategory('');
                }}
                className="px-3 py-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200"
              >
                Clear filters
              </button>
            )}
          </div>
        </div>

        {/* Templates Grid */}
        <div className="flex-1 overflow-y-auto p-6">
          {isLoading ? (
            <div className="flex items-center justify-center h-64">
              <Loader2 className="w-8 h-8 animate-spin text-[var(--accent)]" />
            </div>
          ) : filteredTemplates.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-500 dark:text-gray-400">No templates found. Try adjusting your filters.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredTemplates.map((template) => (
                <div
                  key={template.id}
                  className="p-4 border-2 border-gray-200 dark:border-gray-700 rounded-xl hover:border-[var(--accent)] transition-all cursor-pointer bg-white dark:bg-gray-800 luxury-shadow"
                  onClick={() => handleUseTemplate(template)}
                >
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="font-semibold text-gray-800 dark:text-gray-200">
                      {template.name}
                    </h3>
                    <span className="text-xs px-2 py-1 bg-[var(--accent)]/10 text-[var(--accent)] rounded">
                      {template.category}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                    {template.description}
                  </p>
                  <div className="flex flex-wrap gap-2 text-xs">
                    <span className="text-gray-500 dark:text-gray-500">Platforms:</span>
                    {template.platforms.slice(0, 3).map(platform => (
                      <span key={platform} className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded text-gray-700 dark:text-gray-300">
                        {platform.replace('_', ' ')}
                      </span>
                    ))}
                    {template.platforms.length > 3 && (
                      <span className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded text-gray-500">
                        +{template.platforms.length - 3}
                      </span>
                    )}
                  </div>
                  <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleUseTemplate(template);
                      }}
                      className="w-full px-4 py-2 bg-[var(--accent)] text-white rounded-lg hover:opacity-90 transition text-sm font-medium luxury-shadow"
                    >
                      Use Template
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

