'use client';

import { useState } from 'react';
import { X, TrendingUp, Download, Loader2, ArrowUpDown } from 'lucide-react';
import { sortContent, exportContentData, ContentSortRequest, ContentItem } from '@/lib/api';

interface ContentSorterProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function ContentSorter({ isOpen, onClose }: ContentSorterProps) {
  const [username, setUsername] = useState('');
  const [platform, setPlatform] = useState('instagram');
  const [sortBy, setSortBy] = useState('views');
  const [limit, setLimit] = useState(10); // Lower default for faster results
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [exporting, setExporting] = useState(false);

  const handleSort = async () => {
    if (!username.trim()) {
      setError('Please enter a username');
      return;
    }

    setLoading(true);
    setError(null);
    setResults(null);

    try {
      // Clean username - remove @ if present (backend will handle it, but clean here too)
      const cleanUsername = username.trim().replace(/^@+/, '');
      
      const request: ContentSortRequest = {
        username: cleanUsername,
        platform: platform,
        sort_by: sortBy,
        limit: limit,
      };
      const result = await sortContent(request);
      setResults(result);
    } catch (err) {
      let errorMessage = 'Failed to sort content';
      if (err instanceof Error) {
        errorMessage = err.message;
        // Provide more helpful error messages
        if (errorMessage.includes('500')) {
          errorMessage = 'Server error. This might be due to Instagram rate limiting or the profile being private. Please try again in a few minutes.';
        } else if (errorMessage.includes('403')) {
          errorMessage = 'This profile is private or requires authentication. Please use a public profile.';
        } else if (errorMessage.includes('404')) {
          errorMessage = 'Profile not found. Please check the username and try again.';
        }
      }
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (format: string) => {
    if (!results?.content) {
      setError('No content to export');
      return;
    }

    setExporting(true);
    try {
      const result = await exportContentData(results.content, format);
      // Create download link
      const link = document.createElement('a');
      link.href = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}${result.file_path}`;
      link.download = `content_export.${format}`;
      link.click();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to export');
    } finally {
      setExporting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-[#1a1a1a] rounded-lg shadow-xl max-w-6xl w-full p-6 text-white max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <ArrowUpDown size={28} />
            Content Sorter
          </h2>
          <button onClick={onClose} className="text-white/70 hover:text-white transition-colors">
            <X size={24} />
          </button>
        </div>

        {error && (
          <div className="mb-4 p-4 bg-red-500/20 border border-red-500/50 rounded-lg text-red-300">
            {error}
          </div>
        )}

        {/* Input Form */}
        <div className="mb-8 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Platform</label>
              <select
                value={platform}
                onChange={(e) => setPlatform(e.target.value)}
                className="w-full p-3 bg-[#0f0f0f] border border-white/10 rounded-lg text-white"
              >
                <option value="instagram">Instagram</option>
                <option value="tiktok">TikTok</option>
                <option value="youtube">YouTube</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Sort By</label>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="w-full p-3 bg-[#0f0f0f] border border-white/10 rounded-lg text-white"
              >
                <option value="views">Views</option>
                <option value="likes">Likes</option>
                <option value="comments">Comments</option>
                <option value="engagement_rate">Engagement Rate</option>
                <option value="date">Date</option>
              </select>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                {platform === 'youtube' ? 'Channel (@username or URL)' : 'Username'}
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder={platform === 'youtube' ? '@username (e.g., @MrBeast) or channel URL' : '@username'}
                className="w-full p-3 bg-[#0f0f0f] border border-white/10 rounded-lg text-white placeholder-white/40"
              />
              {platform === 'youtube' && (
                <div className="text-xs text-white/60 mt-1">
                  You can use @username (e.g., @MrBeast) or the full channel URL
                </div>
              )}
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Limit</label>
              <input
                type="number"
                value={limit}
                onChange={(e) => setLimit(parseInt(e.target.value) || 10)}
                min="1"
                max="30"
                className="w-full p-3 bg-[#0f0f0f] border border-white/10 rounded-lg text-white"
              />
              <p className="mt-1 text-xs text-white/60">
                ⚡ Lower = faster. 10 posts ≈ 15-30s, 20 posts ≈ 30-45s, 30 posts ≈ 45-60s
              </p>
            </div>
          </div>
          <button
            onClick={handleSort}
            disabled={loading}
            className="w-full px-4 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:opacity-90 transition-all disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <Loader2 size={20} className="animate-spin" />
                Fetching {limit} posts from Instagram... (15-45 seconds)
              </>
            ) : (
              <>
                <TrendingUp size={20} />
                Sort Content
              </>
            )}
          </button>
        </div>

        {/* Results */}
        {results && results.content && Array.isArray(results.content) && (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <div>
                <h3 className="text-xl font-semibold">Results</h3>
                <p className="text-sm text-white/60">
                  {(results.total_posts || results.total_videos || results.content.length || 0)} items sorted by {results.sorted_by || 'default'}
                </p>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => handleExport('csv')}
                  disabled={exporting}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:opacity-90 transition-all disabled:opacity-50 flex items-center gap-2"
                >
                  <Download size={16} />
                  CSV
                </button>
                <button
                  onClick={() => handleExport('json')}
                  disabled={exporting}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:opacity-90 transition-all disabled:opacity-50 flex items-center gap-2"
                >
                  <Download size={16} />
                  JSON
                </button>
                <button
                  onClick={() => handleExport('excel')}
                  disabled={exporting}
                  className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:opacity-90 transition-all disabled:opacity-50 flex items-center gap-2"
                >
                  <Download size={16} />
                  Excel
                </button>
              </div>
            </div>

            <div className="bg-[#0f0f0f] rounded-lg border border-white/10 overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-[#1a1a1a]">
                    <tr>
                      <th className="px-4 py-3 text-left text-sm font-semibold">Caption</th>
                      <th className="px-4 py-3 text-left text-sm font-semibold">Views</th>
                      <th className="px-4 py-3 text-left text-sm font-semibold">Likes</th>
                      <th className="px-4 py-3 text-left text-sm font-semibold">Comments</th>
                      <th className="px-4 py-3 text-left text-sm font-semibold">Engagement</th>
                      <th className="px-4 py-3 text-left text-sm font-semibold">Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.content?.slice(0, 20).map((item: ContentItem, idx: number) => {
                      // Safely handle numeric values
                      const views = typeof item.views === 'number' ? item.views : 0;
                      const likes = typeof item.likes === 'number' ? item.likes : 0;
                      const comments = typeof item.comments === 'number' ? item.comments : 0;
                      const engagementRate = typeof item.engagement_rate === 'number' ? item.engagement_rate : 0;
                      
                      // Safely handle date
                      let dateString = 'N/A';
                      try {
                        if (item.created_at) {
                          const date = new Date(item.created_at);
                          if (!isNaN(date.getTime())) {
                            dateString = date.toLocaleDateString();
                          }
                        }
                      } catch (e) {
                        // Date parsing failed, use N/A
                      }
                      
                      return (
                        <tr key={item.id || idx} className="border-t border-white/5 hover:bg-white/5">
                          <td className="px-4 py-3 text-sm text-white/80 max-w-xs truncate">
                            {item.caption || 'No caption'}
                          </td>
                          <td className="px-4 py-3 text-sm">{views.toLocaleString()}</td>
                          <td className="px-4 py-3 text-sm">{likes.toLocaleString()}</td>
                          <td className="px-4 py-3 text-sm">{comments.toLocaleString()}</td>
                          <td className="px-4 py-3 text-sm">
                            {engagementRate.toFixed(2)}%
                          </td>
                          <td className="px-4 py-3 text-sm text-white/60">
                            {dateString}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
              {results.content && results.content.length > 20 && (
                <div className="p-4 text-center text-sm text-white/60">
                  Showing 20 of {results.content.length} items
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

