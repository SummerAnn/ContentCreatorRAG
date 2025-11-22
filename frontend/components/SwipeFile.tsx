'use client';

import { useState, useEffect } from 'react';
import { X, Save, ExternalLink, Tag, Trash2, Filter, Loader2 } from 'lucide-react';

interface SwipeFileProps {
  isOpen: boolean;
  onClose: () => void;
  onSaveToSwipeFile?: (url: string) => void;
}

interface SwipeFileVideo {
  id: number;
  url: string;
  title: string | null;
  platform: string | null;
  tags: string[];
  notes: string | null;
  performance_estimate: string | null;
  thumbnail_url: string | null;
  duration: number | null;
  saved_at: string;
}

export default function SwipeFileComponent({ isOpen, onClose, onSaveToSwipeFile }: SwipeFileProps) {
  const [videos, setVideos] = useState<SwipeFileVideo[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [filterPlatform, setFilterPlatform] = useState<string>('');
  const [filterTags, setFilterTags] = useState<string>('');
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [saveUrl, setSaveUrl] = useState('');
  const [saveTitle, setSaveTitle] = useState('');
  const [savePlatform, setSavePlatform] = useState('');
  const [saveTags, setSaveTags] = useState('');
  const [saveNotes, setSaveNotes] = useState('');
  const [userId] = useState('default_user');

  useEffect(() => {
    if (isOpen) {
      loadSwipeFile();
    }
  }, [isOpen, filterPlatform, filterTags]);

  const loadSwipeFile = async () => {
    setIsLoading(true);
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const params = new URLSearchParams({ user_id: userId });
      if (filterPlatform) params.append('platform', filterPlatform);
      if (filterTags) params.append('tags', filterTags);
      
      const response = await fetch(`${apiUrl}/api/swipefile/?${params.toString()}`);
      if (response.ok) {
        const data = await response.json();
        setVideos(data.videos || []);
      }
    } catch (error) {
      console.error('Error loading swipe file:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async () => {
    if (!saveUrl.trim()) return;

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const tags = saveTags.split(',').map(t => t.trim()).filter(Boolean);
      
      const response = await fetch(`${apiUrl}/api/swipefile/save`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          url: saveUrl,
          title: saveTitle || null,
          platform: savePlatform || null,
          tags: tags.length > 0 ? tags : null,
          notes: saveNotes || null,
        }),
      });

      if (response.ok) {
        setShowSaveModal(false);
        setSaveUrl('');
        setSaveTitle('');
        setSavePlatform('');
        setSaveTags('');
        setSaveNotes('');
        loadSwipeFile();
        if (onSaveToSwipeFile) {
          onSaveToSwipeFile(saveUrl);
        }
      }
    } catch (error) {
      console.error('Error saving to swipe file:', error);
    }
  };

  const handleDelete = async (videoId: number) => {
    if (!confirm('Delete this video from your swipe file?')) return;

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/swipefile/delete?user_id=${userId}&video_id=${videoId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        loadSwipeFile();
      }
    } catch (error) {
      console.error('Error deleting video:', error);
    }
  };

  if (!isOpen) return null;

  return (
    <>
      <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
        <div className="bg-white dark:bg-gray-900 rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] flex flex-col">
          {/* Header */}
          <div className="flex justify-between items-center p-6 border-b border-gray-200 dark:border-gray-800">
            <div>
              <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-200">Personal Swipe File</h2>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                Save and organize inspiration videos - {videos.length} saved
              </p>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowSaveModal(true)}
                className="px-4 py-2 bg-[var(--accent)] text-white rounded-lg hover:opacity-90 transition"
              >
                <Save size={18} className="inline mr-2" />
                Save Video
              </button>
              <button 
                onClick={onClose} 
                className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition"
              >
                <X size={24} />
              </button>
            </div>
          </div>

          {/* Filters */}
          <div className="p-4 border-b border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-800">
            <div className="flex items-center gap-4">
              <Filter className="w-4 h-4 text-gray-500" />
              <input
                type="text"
                placeholder="Filter by platform..."
                value={filterPlatform}
                onChange={(e) => setFilterPlatform(e.target.value)}
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-sm flex-1 max-w-xs"
              />
              <input
                type="text"
                placeholder="Filter by tags..."
                value={filterTags}
                onChange={(e) => setFilterTags(e.target.value)}
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-sm flex-1 max-w-xs"
              />
              {(filterPlatform || filterTags) && (
                <button
                  onClick={() => {
                    setFilterPlatform('');
                    setFilterTags('');
                  }}
                  className="px-3 py-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200"
                >
                  Clear
                </button>
              )}
            </div>
          </div>

          {/* Videos List */}
          <div className="flex-1 overflow-y-auto p-6">
            {isLoading ? (
              <div className="flex items-center justify-center h-64">
                <Loader2 className="w-8 h-8 animate-spin text-[var(--accent)]" />
              </div>
            ) : videos.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-gray-500 dark:text-gray-400 mb-4">Your swipe file is empty.</p>
                <button
                  onClick={() => setShowSaveModal(true)}
                  className="px-4 py-2 bg-[var(--accent)] text-white rounded-lg hover:opacity-90 transition"
                >
                  Save Your First Video
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-4">
                {videos.map((video) => (
                  <div
                    key={video.id}
                    className="p-4 border-2 border-gray-200 dark:border-gray-700 rounded-xl hover:border-[var(--accent)] transition-all bg-white dark:bg-gray-800 luxury-shadow"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <a
                            href={video.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="font-semibold text-gray-800 dark:text-gray-200 hover:text-[var(--accent)] flex items-center gap-2"
                          >
                            {video.title || video.url}
                            <ExternalLink size={14} />
                          </a>
                          {video.platform && (
                            <span className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded text-xs text-gray-600 dark:text-gray-400">
                              {video.platform}
                            </span>
                          )}
                        </div>
                        {video.tags && video.tags.length > 0 && (
                          <div className="flex flex-wrap gap-2 mb-2">
                            {video.tags.map((tag, idx) => (
                              <span
                                key={idx}
                                className="px-2 py-1 bg-[var(--accent)]/10 text-[var(--accent)] rounded text-xs flex items-center gap-1"
                              >
                                <Tag size={12} />
                                {tag}
                              </span>
                            ))}
                          </div>
                        )}
                        {video.notes && (
                          <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">{video.notes}</p>
                        )}
                        {video.performance_estimate && (
                          <p className="text-xs text-gray-500 dark:text-gray-500">
                            Performance: {video.performance_estimate}
                          </p>
                        )}
                      </div>
                      <button
                        onClick={() => handleDelete(video.id)}
                        className="ml-4 text-red-500 hover:text-red-700 p-2 hover:bg-red-50 dark:hover:bg-red-900/20 rounded transition"
                      >
                        <Trash2 size={18} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Save Modal */}
      {showSaveModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-[60] flex items-center justify-center p-4">
          <div className="bg-white dark:bg-gray-900 rounded-lg shadow-xl w-full max-w-md p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold text-gray-800 dark:text-gray-200">Save Video to Swipe File</h3>
              <button
                onClick={() => setShowSaveModal(false)}
                className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
              >
                <X size={24} />
              </button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Video URL *
                </label>
                <input
                  type="url"
                  value={saveUrl}
                  onChange={(e) => setSaveUrl(e.target.value)}
                  placeholder="https://..."
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Title (optional)
                </label>
                <input
                  type="text"
                  value={saveTitle}
                  onChange={(e) => setSaveTitle(e.target.value)}
                  placeholder="Video title"
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Platform (optional)
                </label>
                <input
                  type="text"
                  value={savePlatform}
                  onChange={(e) => setSavePlatform(e.target.value)}
                  placeholder="tiktok, youtube, instagram..."
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Tags (comma-separated)
                </label>
                <input
                  type="text"
                  value={saveTags}
                  onChange={(e) => setSaveTags(e.target.value)}
                  placeholder="travel, cinematic, inspiration"
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Notes (optional)
                </label>
                <textarea
                  value={saveNotes}
                  onChange={(e) => setSaveNotes(e.target.value)}
                  placeholder="Your personal notes..."
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
                />
              </div>
              <div className="flex gap-2 pt-2">
                <button
                  onClick={handleSave}
                  className="flex-1 px-4 py-2 bg-[var(--accent)] text-white rounded-lg hover:opacity-90 transition"
                  disabled={!saveUrl.trim()}
                >
                  Save
                </button>
                <button
                  onClick={() => setShowSaveModal(false)}
                  className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

// Helper component for saving from other components
export function SwipeFileButton({ videoUrl, title, platform }: { videoUrl: string; title?: string; platform?: string }) {
  const [isSaving, setIsSaving] = useState(false);
  const [userId] = useState('default_user');

  const saveToSwipeFile = async () => {
    setIsSaving(true);
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      await fetch(`${apiUrl}/api/swipefile/save`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          url: videoUrl,
          title: title,
          platform: platform,
          tags: ['inspiration'],
        }),
      });
    } catch (error) {
      console.error('Error saving to swipe file:', error);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <button
      onClick={saveToSwipeFile}
      disabled={isSaving}
      className="px-3 py-2 bg-[var(--accent)]/10 text-[var(--accent)] rounded-lg hover:bg-[var(--accent)]/20 transition text-sm flex items-center gap-2"
    >
      <Save size={16} />
      {isSaving ? 'Saving...' : 'Save to Swipe File'}
    </button>
  );
}

