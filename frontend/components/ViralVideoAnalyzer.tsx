'use client';

import { useState } from 'react';
import { X, Play, Download, TrendingUp, Sparkles, Loader2, Search, Video } from 'lucide-react';
import { analyzeViralVideo, batchAnalyzeChannel, listInstagramVideos, listYouTubeVideos, listTikTokVideos, VideoAnalysisRequest, VideoAnalysisResponse, InstagramVideo, YouTubeVideo, TikTokVideo } from '@/lib/api';

interface ViralVideoAnalyzerProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function ViralVideoAnalyzer({ isOpen, onClose }: ViralVideoAnalyzerProps) {
  const [url, setUrl] = useState('');
  const [platform, setPlatform] = useState('youtube');
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState<VideoAnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [channelUrl, setChannelUrl] = useState('');
  const [batchLoading, setBatchLoading] = useState(false);
  const [batchResults, setBatchResults] = useState<any>(null);
  const [instagramUsername, setInstagramUsername] = useState('');
  const [instagramVideos, setInstagramVideos] = useState<InstagramVideo[]>([]);
  const [youtubeChannel, setYoutubeChannel] = useState('');
  const [youtubeVideos, setYoutubeVideos] = useState<YouTubeVideo[]>([]);
  const [tiktokUsername, setTiktokUsername] = useState('');
  const [tiktokVideos, setTiktokVideos] = useState<TikTokVideo[]>([]);
  const [loadingVideos, setLoadingVideos] = useState(false);

  const handleAnalyze = async () => {
    if (!url.trim()) {
      setError('Please enter a video URL');
      return;
    }

    setLoading(true);
    setError(null);
    setAnalysis(null);

    try {
      const request: VideoAnalysisRequest = {
        url: url.trim(),
        platform: platform,
      };
      const result = await analyzeViralVideo(request);
      setAnalysis(result);
    } catch (err) {
      let errorMessage = 'Failed to analyze video';
      if (err instanceof Error) {
        errorMessage = err.message;
        // Provide more helpful error messages
        if (errorMessage.includes('profile URL')) {
          errorMessage = 'This is a profile URL, not a video URL. Please provide a specific post or reel URL.\n\n' +
                        'To get a post/reel URL:\n' +
                        '1. Go to the Instagram post/reel you want to analyze\n' +
                        '2. Click the three dots (⋯) or share button\n' +
                        '3. Select "Copy link"\n' +
                        '4. Use that URL (should look like: https://www.instagram.com/p/SHORTCODE/)';
        } else if (errorMessage.includes('400')) {
          errorMessage = 'Invalid URL format. Please use a specific post or reel URL, not a profile URL.';
        }
      }
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleBatchAnalyze = async () => {
    if (!channelUrl.trim()) {
      setError('Please enter a channel username or URL');
      return;
    }

    setBatchLoading(true);
    setError(null);
    setBatchResults(null);

    try {
      // Check if it's Instagram - show helpful message
      if (channelUrl.toLowerCase().includes('instagram.com')) {
        setError('Instagram profiles are not supported for batch analysis. Please use YouTube channels (e.g., @username)');
        setBatchLoading(false);
        return;
      }
      
      // The backend now handles @username format automatically
      const result = await batchAnalyzeChannel(channelUrl.trim(), 10);
      setBatchResults(result);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to analyze channel';
      // Provide helpful error message for Instagram
      if (errorMessage.includes('404') && channelUrl.toLowerCase().includes('instagram')) {
        setError('Instagram profiles are not supported for batch analysis. Please use YouTube channels (e.g., @username) instead.');
      } else {
        setError(errorMessage);
      }
    } finally {
      setBatchLoading(false);
    }
  };

  const handleFetchInstagramVideos = async () => {
    if (!instagramUsername.trim()) {
      setError('Please enter an Instagram username');
      return;
    }

    setLoadingVideos(true);
    setError(null);
    setInstagramVideos([]);

    try {
      const result = await listInstagramVideos(instagramUsername.trim(), 20);
      setInstagramVideos(result.videos || []);
      if (result.videos && result.videos.length === 0) {
        setError('No videos found for this username. Make sure the profile is public and has videos/reels.');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch videos');
    } finally {
      setLoadingVideos(false);
    }
  };

  const handleFetchYouTubeVideos = async () => {
    if (!youtubeChannel.trim()) {
      setError('Please enter a YouTube channel (@username or channel URL)');
      return;
    }

    setLoadingVideos(true);
    setError(null);
    setYoutubeVideos([]);

    try {
      const result = await listYouTubeVideos(youtubeChannel.trim(), 20);
      setYoutubeVideos(result.videos || []);
      if (result.videos && result.videos.length === 0) {
        setError('No videos found for this channel.');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch videos');
    } finally {
      setLoadingVideos(false);
    }
  };

  const handleFetchTikTokVideos = async () => {
    if (!tiktokUsername.trim()) {
      setError('Please enter a TikTok username');
      return;
    }

    setLoadingVideos(true);
    setError(null);
    setTiktokVideos([]);

    try {
      const result = await listTikTokVideos(tiktokUsername.trim(), 20);
      setTiktokVideos(result.videos || []);
      if (result.videos && result.videos.length === 0) {
        setError('No videos found for this username. Make sure the account is public.');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch videos');
    } finally {
      setLoadingVideos(false);
    }
  };

  const handleSelectVideo = (videoUrl: string, videoPlatform: string) => {
    setUrl(videoUrl);
    setPlatform(videoPlatform);
    // Auto-analyze when video is selected
    setTimeout(() => {
      handleAnalyze();
    }, 100);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-[#1a1a1a] rounded-lg shadow-xl max-w-6xl w-full p-6 text-white max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <TrendingUp size={28} />
            Viral Video Analyzer
          </h2>
          <button onClick={onClose} className="text-white/70 hover:text-white transition-colors">
            <X size={24} />
          </button>
        </div>

        {error && (
          <div className="mb-4 p-4 bg-red-500/20 border border-red-500/50 rounded-lg text-red-300">
            <div className="font-semibold mb-2">Error:</div>
            <div>{error}</div>
          </div>
        )}

        {/* Quick Access: Search by Username (All Platforms) */}
        <div className="mb-6 p-4 bg-purple-500/10 border border-purple-500/30 rounded-lg">
          <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
            <Search size={20} />
            Quick Access: Search by Username
          </h3>
          
          {/* Instagram Search */}
          {platform === 'instagram' && (
            <div className="flex gap-2">
              <input
                type="text"
                value={instagramUsername}
                onChange={(e) => setInstagramUsername(e.target.value)}
                placeholder="@username (e.g., @mrbeast)"
                className="flex-1 p-3 bg-[#0f0f0f] border border-white/10 rounded-lg text-white placeholder-white/40"
                onKeyPress={(e) => e.key === 'Enter' && handleFetchInstagramVideos()}
              />
              <button
                onClick={handleFetchInstagramVideos}
                disabled={loadingVideos}
                className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 flex items-center gap-2"
              >
                {loadingVideos ? (
                  <Loader2 size={20} className="animate-spin" />
                ) : (
                  <Search size={20} />
                )}
                {loadingVideos ? 'Loading...' : 'Fetch Videos'}
              </button>
            </div>
          )}
          
          {/* YouTube Search */}
          {platform === 'youtube' && (
            <div className="flex gap-2">
              <input
                type="text"
                value={youtubeChannel}
                onChange={(e) => setYoutubeChannel(e.target.value)}
                placeholder="@username or channel URL (e.g., @MrBeast)"
                className="flex-1 p-3 bg-[#0f0f0f] border border-white/10 rounded-lg text-white placeholder-white/40"
                onKeyPress={(e) => e.key === 'Enter' && handleFetchYouTubeVideos()}
              />
              <button
                onClick={handleFetchYouTubeVideos}
                disabled={loadingVideos}
                className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 flex items-center gap-2"
              >
                {loadingVideos ? (
                  <Loader2 size={20} className="animate-spin" />
                ) : (
                  <Search size={20} />
                )}
                {loadingVideos ? 'Loading...' : 'Fetch Videos'}
              </button>
            </div>
          )}
          
          {/* TikTok Search */}
          {platform === 'tiktok' && (
            <div className="flex gap-2">
              <input
                type="text"
                value={tiktokUsername}
                onChange={(e) => setTiktokUsername(e.target.value)}
                placeholder="@username (e.g., @mrbeast)"
                className="flex-1 p-3 bg-[#0f0f0f] border border-white/10 rounded-lg text-white placeholder-white/40"
                onKeyPress={(e) => e.key === 'Enter' && handleFetchTikTokVideos()}
              />
              <button
                onClick={handleFetchTikTokVideos}
                disabled={loadingVideos}
                className="px-6 py-3 bg-black text-white rounded-lg hover:bg-gray-900 disabled:opacity-50 flex items-center gap-2"
              >
                {loadingVideos ? (
                  <Loader2 size={20} className="animate-spin" />
                ) : (
                  <Search size={20} />
                )}
                {loadingVideos ? 'Loading...' : 'Fetch Videos'}
              </button>
            </div>
          )}
          
          {/* Video Lists */}
          {instagramVideos.length > 0 && platform === 'instagram' && (
            <div className="mt-4">
              <div className="text-sm text-white/70 mb-3">
                Found {instagramVideos.length} videos. Click any video to analyze:
              </div>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3 max-h-64 overflow-y-auto">
                {instagramVideos.map((video) => (
                  <button
                    key={video.shortcode}
                    onClick={() => handleSelectVideo(video.url, 'instagram')}
                    className="p-3 bg-[#0f0f0f] border border-white/10 rounded-lg hover:border-purple-500/50 transition-all text-left"
                  >
                    <div className="text-xs text-white/60 mb-1 truncate">
                      {video.views > 0 ? `${(video.views / 1000).toFixed(0)}K views` : ''} • {video.likes} likes
                    </div>
                    <div className="text-sm text-white truncate font-medium">
                      {video.caption || 'No caption'}
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}
          
          {youtubeVideos.length > 0 && platform === 'youtube' && (
            <div className="mt-4">
              <div className="text-sm text-white/70 mb-3">
                Found {youtubeVideos.length} videos. Click any video to analyze:
              </div>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3 max-h-64 overflow-y-auto">
                {youtubeVideos.map((video) => (
                  <button
                    key={video.video_id}
                    onClick={() => handleSelectVideo(video.url, 'youtube')}
                    className="p-3 bg-[#0f0f0f] border border-white/10 rounded-lg hover:border-red-500/50 transition-all text-left"
                  >
                    <div className="text-xs text-white/60 mb-1 truncate">
                      {video.view_count > 0 ? `${(video.view_count / 1000000).toFixed(1)}M views` : ''}
                    </div>
                    <div className="text-sm text-white truncate font-medium">
                      {video.title}
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}
          
          {tiktokVideos.length > 0 && platform === 'tiktok' && (
            <div className="mt-4">
              <div className="text-sm text-white/70 mb-3">
                Found {tiktokVideos.length} videos. Click any video to analyze:
              </div>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3 max-h-64 overflow-y-auto">
                {tiktokVideos.map((video) => (
                  <button
                    key={video.video_id}
                    onClick={() => handleSelectVideo(video.url, 'tiktok')}
                    className="p-3 bg-[#0f0f0f] border border-white/10 rounded-lg hover:border-gray-500/50 transition-all text-left"
                  >
                    <div className="text-xs text-white/60 mb-1 truncate">
                      {video.view_count > 0 ? `${(video.view_count / 1000).toFixed(0)}K views` : ''} • {video.likes} likes
                    </div>
                    <div className="text-sm text-white truncate font-medium">
                      {video.title || 'No title'}
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Single Video Analysis */}
        <div className="mb-8">
          <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <Play size={20} />
            Analyze Single Video
          </h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Platform</label>
              <select
                value={platform}
                onChange={(e) => {
                  setPlatform(e.target.value);
                  // Clear all video lists when switching platforms
                  setInstagramVideos([]);
                  setInstagramUsername('');
                  setYoutubeVideos([]);
                  setYoutubeChannel('');
                  setTiktokVideos([]);
                  setTiktokUsername('');
                }}
                className="w-full p-3 bg-[#0f0f0f] border border-white/10 rounded-lg text-white"
              >
                <option value="youtube">YouTube</option>
                <option value="tiktok">TikTok</option>
                <option value="instagram">Instagram</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Video URL</label>
              <input
                type="text"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder={platform === 'instagram' ? 'https://instagram.com/p/... or use username search above' : 'https://youtube.com/watch?v=...'}
                className="w-full p-3 bg-[#0f0f0f] border border-white/10 rounded-lg text-white placeholder-white/40"
              />
            </div>
            <button
              onClick={handleAnalyze}
              disabled={loading}
              className="w-full px-4 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:opacity-90 transition-all disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 size={20} className="animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Sparkles size={20} />
                  Analyze Video
                </>
              )}
            </button>
          </div>
        </div>

        {/* Analysis Results */}
        {analysis && (
          <div className="mb-8 p-6 bg-[#0f0f0f] rounded-lg border border-white/10">
            <h3 className="text-xl font-semibold mb-4">Analysis Results</h3>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-[#1a1a1a] p-4 rounded-lg">
                <div className="text-sm text-white/60">Title</div>
                <div className="text-lg font-semibold">{analysis.title}</div>
              </div>
              <div className="bg-[#1a1a1a] p-4 rounded-lg">
                <div className="text-sm text-white/60">Views</div>
                <div className="text-lg font-semibold">{analysis.views.toLocaleString()}</div>
              </div>
              <div className="bg-[#1a1a1a] p-4 rounded-lg">
                <div className="text-sm text-white/60">Likes</div>
                <div className="text-lg font-semibold">{analysis.likes.toLocaleString()}</div>
              </div>
              <div className="bg-[#1a1a1a] p-4 rounded-lg">
                <div className="text-sm text-white/60">Duration</div>
                <div className="text-lg font-semibold">{analysis.duration}s</div>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <h4 className="font-semibold mb-2">Hook (First 3 seconds)</h4>
                <p className="text-white/80 bg-[#1a1a1a] p-3 rounded-lg">{analysis.hook}</p>
              </div>

              <div>
                <h4 className="font-semibold mb-2">Story Structure</h4>
                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-[#1a1a1a] p-3 rounded-lg">
                    <div className="text-sm text-white/60 mb-1">Setup</div>
                    <div className="text-white/80">{analysis.story_structure.setup}</div>
                  </div>
                  <div className="bg-[#1a1a1a] p-3 rounded-lg">
                    <div className="text-sm text-white/60 mb-1">Conflict</div>
                    <div className="text-white/80">{analysis.story_structure.conflict}</div>
                  </div>
                  <div className="bg-[#1a1a1a] p-3 rounded-lg">
                    <div className="text-sm text-white/60 mb-1">Resolution</div>
                    <div className="text-white/80">{analysis.story_structure.resolution}</div>
                  </div>
                  <div className="bg-[#1a1a1a] p-3 rounded-lg">
                    <div className="text-sm text-white/60 mb-1">CTA</div>
                    <div className="text-white/80">{analysis.story_structure.cta}</div>
                  </div>
                </div>
              </div>

              <div>
                <h4 className="font-semibold mb-2">Visual Style</h4>
                <p className="text-white/80 bg-[#1a1a1a] p-3 rounded-lg">{analysis.visual_style}</p>
              </div>

              <div>
                <h4 className="font-semibold mb-2">Key Moments</h4>
                <div className="space-y-2">
                  {analysis.key_moments.map((moment, idx) => (
                    <div key={idx} className="bg-[#1a1a1a] p-3 rounded-lg">
                      <div className="flex items-start gap-3">
                        <span className="text-purple-400 font-mono text-sm">{moment.timestamp}</span>
                        <div className="flex-1">
                          <div className="font-medium mb-1">{moment.description}</div>
                          <div className="text-sm text-white/60">{moment.why_it_works}</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h4 className="font-semibold mb-2">Remix Suggestions</h4>
                <ul className="space-y-2">
                  {analysis.remix_suggestions.map((suggestion, idx) => (
                    <li key={idx} className="bg-[#1a1a1a] p-3 rounded-lg text-white/80">
                      • {suggestion}
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <h4 className="font-semibold mb-2">Transcript</h4>
                <div className="bg-[#1a1a1a] p-3 rounded-lg text-white/80 text-sm max-h-40 overflow-y-auto">
                  {analysis.transcript}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Batch Channel Analysis */}
        <div className="border-t border-white/10 pt-8">
          <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <Download size={20} />
            Batch Channel Analysis
          </h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Channel/Creator (@username or URL)</label>
              <input
                type="text"
                value={channelUrl}
                onChange={(e) => setChannelUrl(e.target.value)}
                placeholder="@username (e.g., @MrBeast) or https://www.youtube.com/@username/videos"
                className="w-full p-3 bg-[#0f0f0f] border border-white/10 rounded-lg text-white placeholder-white/40"
              />
              <div className="text-xs text-white/60 mt-1">
                You can use just @username (e.g., @MrBeast) or the full URL
              </div>
            </div>
            <button
              onClick={handleBatchAnalyze}
              disabled={batchLoading}
              className="w-full px-4 py-3 bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-lg hover:opacity-90 transition-all disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {batchLoading ? (
                <>
                  <Loader2 size={20} className="animate-spin" />
                  Analyzing Channel...
                </>
              ) : (
                <>
                  <TrendingUp size={20} />
                  Analyze Channel
                </>
              )}
            </button>
          </div>

          {batchResults && (
            <div className="mt-6 p-6 bg-[#0f0f0f] rounded-lg border border-white/10">
              <h4 className="font-semibold mb-4">Channel: {batchResults.channel}</h4>
              <div className="text-sm text-white/60 mb-4">Total Videos: {batchResults.total_videos}</div>
              
              <div className="space-y-3">
                <h5 className="font-medium">Top Performers:</h5>
                {batchResults.top_performers?.map((video: any, idx: number) => (
                  <div key={idx} className="bg-[#1a1a1a] p-3 rounded-lg">
                    <div className="font-medium mb-1">{video.title}</div>
                    <div className="text-sm text-white/60">
                      {video.view_count?.toLocaleString()} views • {video.like_count?.toLocaleString()} likes
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

