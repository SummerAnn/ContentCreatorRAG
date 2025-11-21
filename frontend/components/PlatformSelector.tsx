'use client';

interface PlatformSelectorProps {
  value: string;
  onChange: (value: string) => void;
}

const platforms = [
  { id: 'youtube_short', label: 'YouTube Shorts' },
  { id: 'youtube', label: 'YouTube Long' },
  { id: 'tiktok', label: 'TikTok' },
  { id: 'instagram_reel', label: 'Instagram Reels' },
  { id: 'instagram_carousel', label: 'Instagram Carousel' },
  { id: 'linkedin', label: 'LinkedIn' },
  { id: 'twitter_thread', label: 'Twitter/X Thread' },
  { id: 'pinterest', label: 'Pinterest Pin' },
  { id: 'podcast_clip', label: 'Podcast Clip' },
];

export default function PlatformSelector({ value, onChange }: PlatformSelectorProps) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
      {platforms.map((platform) => (
        <button
          key={platform.id}
          onClick={() => onChange(platform.id)}
          className={`
            p-4 border-2 rounded-xl transition-all luxury-shadow
            ${value === platform.id
              ? 'border-[var(--accent)] bg-[var(--accent)]/10 dark:bg-[var(--accent)]/20 text-[var(--accent-dark)] dark:text-[var(--accent)]'
              : 'luxury-border hover:border-[var(--accent)]/50 text-[var(--foreground)]/80 bg-white dark:bg-[#1a1a1a]'
            }
          `}
        >
          <div className="text-sm font-medium">{platform.label}</div>
        </button>
      ))}
    </div>
  );
}
