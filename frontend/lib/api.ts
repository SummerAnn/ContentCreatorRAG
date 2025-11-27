const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface GenerateRequest {
  user_id: string;
  platform: string;
  niche: string;
  goal: string;
  reference_text?: string;
  reference_image?: string;
  content_type: string;
  options?: Record<string, any>;
}

export async function generateContent(
  endpoint: string,
  request: GenerateRequest,
  onChunk: (chunk: string) => void,
  onDone: () => void,
  onError: (error: string) => void
) {
  try {
    const response = await fetch(`${API_URL}/api/generate/${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    if (!reader) {
      throw new Error('No response body');
    }

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6));
            if (data.chunk) {
              onChunk(data.chunk);
            }
            if (data.done) {
              onDone();
              return;
            }
            if (data.error) {
              onError(data.error);
              return;
            }
          } catch (e) {
            // Skip invalid JSON
          }
        }
      }
    }
  } catch (error) {
    onError(error instanceof Error ? error.message : 'Unknown error');
  }
}

// Viral Video Analyzer API
export interface VideoAnalysisRequest {
  url: string;
  platform: string;
}

export interface VideoAnalysisResponse {
  title: string;
  views: number;
  likes: number;
  duration: number;
  transcript: string;
  hook: string;
  story_structure: {
    setup: string;
    conflict: string;
    resolution: string;
    cta: string;
  };
  visual_style: string;
  key_moments: Array<{
    timestamp: string;
    description: string;
    why_it_works: string;
  }>;
  remix_suggestions: string[];
}

export async function analyzeViralVideo(request: VideoAnalysisRequest): Promise<VideoAnalysisResponse> {
  const response = await fetch(`${API_URL}/api/viral-analyzer/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
}

export async function batchAnalyzeChannel(channelUrl: string, limit: number = 10) {
  const response = await fetch(`${API_URL}/api/viral-analyzer/batch-analyze?channel_url=${encodeURIComponent(channelUrl)}&limit=${limit}`, {
    method: 'POST',
  });
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
}

// List Instagram videos from a username
export interface InstagramVideo {
  shortcode: string;
  url: string;
  caption: string;
  views: number;
  likes: number;
  comments: number;
  created_at: string;
  thumbnail: string;
}

export async function listInstagramVideos(username: string, limit: number = 20) {
  const cleanUsername = username.trim().replace('@', '');
  const response = await fetch(`${API_URL}/api/viral-analyzer/list-videos?username=${encodeURIComponent(cleanUsername)}&limit=${limit}`);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
}

// List YouTube videos from a channel
export interface YouTubeVideo {
  video_id: string;
  url: string;
  title: string;
  view_count: number;
  duration: number;
  thumbnail: string;
}

export async function listYouTubeVideos(channelIdentifier: string, limit: number = 20) {
  const response = await fetch(`${API_URL}/api/viral-analyzer/list-youtube-videos?channel_identifier=${encodeURIComponent(channelIdentifier)}&limit=${limit}`);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
}

// List TikTok videos from a username
export interface TikTokVideo {
  video_id: string;
  url: string;
  title: string;
  view_count: number;
  likes: number;
  comments: number;
  thumbnail: string;
}

export async function listTikTokVideos(username: string, limit: number = 20) {
  const cleanUsername = username.trim().replace('@', '');
  const response = await fetch(`${API_URL}/api/viral-analyzer/list-tiktok-videos?username=${encodeURIComponent(cleanUsername)}&limit=${limit}`);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
}

// Content Sorter API
export interface ContentSortRequest {
  username: string;
  platform: string;
  sort_by?: string;
  limit?: number;
}

export interface ContentItem {
  id: string;
  caption: string;
  views: number;
  likes: number;
  comments: number;
  shares: number;
  engagement_rate: number;
  created_at: string;
  url: string;
  thumbnail: string;
}

export async function sortContent(request: ContentSortRequest) {
  const response = await fetch(`${API_URL}/api/content-sorter/sort-content`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
}

export async function exportContentData(data: ContentItem[], format: string = 'csv') {
  const response = await fetch(`${API_URL}/api/content-sorter/export-data?format=${format}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
}

// Transcription API
export interface TranscriptionResponse {
  text: string;
  language: string;
  segments: Array<{
    start: number;
    end: number;
    text: string;
  }>;
  word_count: number;
  duration: number;
}

export async function transcribeFile(file: File): Promise<TranscriptionResponse> {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(`${API_URL}/api/transcription/transcribe-file`, {
    method: 'POST',
    body: formData,
  });
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
}

export async function transcribeUrl(url: string) {
  const response = await fetch(`${API_URL}/api/transcription/transcribe-url?url=${encodeURIComponent(url)}`, {
    method: 'POST',
  });
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
}

export async function generateCaptions(text: string, format: string = 'srt') {
  const response = await fetch(`${API_URL}/api/transcription/generate-captions?text=${encodeURIComponent(text)}&format=${format}`, {
    method: 'POST',
  });
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
}

// Viral Title Generator API
export interface TitleRequest {
  topic: string;
  platform: string;
  niche: string;
  vibe?: string;
}

export interface TitleResponse {
  title: string;
  viral_score: number;
  platform: string;
}

export async function generateViralTitles(request: TitleRequest) {
  const response = await fetch(`${API_URL}/api/viral-titles/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
}

export async function getTrendingPatterns(platform: string, niche?: string) {
  const url = `${API_URL}/api/viral-titles/trending-patterns/${platform}${niche ? `?niche=${encodeURIComponent(niche)}` : ''}`;
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
}

// Trend Detector API
export interface TrendRequest {
  platform: string;
  niche: string;
  region?: string;
}

export async function detectTrends(request: TrendRequest) {
  const response = await fetch(`${API_URL}/api/trend-detector/detect`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
}

export async function getNicheTrends(niche: string) {
  const response = await fetch(`${API_URL}/api/trend-detector/niche-trends/${encodeURIComponent(niche)}`);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
}

