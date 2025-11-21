'use client';

import { Copy, Download, Check, Edit, CheckCheck, ArrowRight, RefreshCw } from 'lucide-react';
import { useState } from 'react';
import clsx from 'clsx';

interface GeneratedContentProps {
      type: 'hooks' | 'script' | 'shotlist' | 'music' | 'titles' | 'description' | 'tags' | 'thumbnails' | 'beatmap' | 'cta' | 'tools';
  content: string;
  isStreaming: boolean;
  selectedHook?: string;
  onSelectHook?: (hook: string) => void;
  messageId?: number;
  onEdit?: (id: number, content: string) => void;
  onUseForNext?: (content: string, type: string) => void;
  onRegenerate?: () => void;
}

const typeConfig: Record<string, any> = {
  hooks: { 
    title: 'Viral Hooks', 
    bgColor: 'bg-blue-50 dark:bg-blue-950/20', 
    borderColor: 'border-blue-200 dark:border-blue-800', 
    textColor: 'text-blue-800 dark:text-blue-200',
    buttonClass: 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 hover:bg-blue-200 dark:hover:bg-blue-800',
  },
  script: { 
    title: 'Video Script', 
    bgColor: 'bg-green-50 dark:bg-green-950/20', 
    borderColor: 'border-green-200 dark:border-green-800', 
    textColor: 'text-green-800 dark:text-green-200',
    buttonClass: 'bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 hover:bg-green-200 dark:hover:bg-green-800',
  },
  shotlist: { 
    title: 'Shot List', 
    bgColor: 'bg-purple-50 dark:bg-purple-950/20', 
    borderColor: 'border-purple-200 dark:border-purple-800', 
    textColor: 'text-purple-800 dark:text-purple-200',
    buttonClass: 'bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-300 hover:bg-purple-200 dark:hover:bg-purple-800',
  },
  music: { 
    title: 'Music Recommendations', 
    bgColor: 'bg-orange-50 dark:bg-orange-950/20', 
    borderColor: 'border-orange-200 dark:border-orange-800', 
    textColor: 'text-orange-800 dark:text-orange-200',
    buttonClass: 'bg-orange-100 dark:bg-orange-900 text-orange-700 dark:text-orange-300 hover:bg-orange-200 dark:hover:bg-orange-800',
  },
  titles: {
    title: 'SEO Titles',
    bgColor: 'bg-indigo-50 dark:bg-indigo-950/20',
    borderColor: 'border-indigo-200 dark:border-indigo-800',
    textColor: 'text-indigo-800 dark:text-indigo-200',
    buttonClass: 'bg-indigo-100 dark:bg-indigo-900 text-indigo-700 dark:text-indigo-300 hover:bg-indigo-200 dark:hover:bg-indigo-800',
  },
  description: {
    title: 'Video Description',
    bgColor: 'bg-teal-50 dark:bg-teal-950/20',
    borderColor: 'border-teal-200 dark:border-teal-800',
    textColor: 'text-teal-800 dark:text-teal-200',
    buttonClass: 'bg-teal-100 dark:bg-teal-900 text-teal-700 dark:text-teal-300 hover:bg-teal-200 dark:hover:bg-teal-800',
  },
  tags: {
    title: 'Tags & Hashtags',
    bgColor: 'bg-cyan-50 dark:bg-cyan-950/20',
    borderColor: 'border-cyan-200 dark:border-cyan-800',
    textColor: 'text-cyan-800 dark:text-cyan-200',
    buttonClass: 'bg-cyan-100 dark:bg-cyan-900 text-cyan-700 dark:text-cyan-300 hover:bg-cyan-200 dark:hover:bg-cyan-800',
  },
  thumbnails: {
    title: 'Thumbnail Concepts',
    bgColor: 'bg-yellow-50 dark:bg-yellow-950/20',
    borderColor: 'border-yellow-200 dark:border-yellow-800',
    textColor: 'text-yellow-800 dark:text-yellow-200',
    buttonClass: 'bg-yellow-100 dark:bg-yellow-900 text-yellow-700 dark:text-yellow-300 hover:bg-yellow-200 dark:hover:bg-yellow-800',
  },
  beatmap: {
    title: 'Beat Map / Retention',
    bgColor: 'bg-pink-50 dark:bg-pink-950/20',
    borderColor: 'border-pink-200 dark:border-pink-800',
    textColor: 'text-pink-800 dark:text-pink-200',
    buttonClass: 'bg-pink-100 dark:bg-pink-900 text-pink-700 dark:text-pink-300 hover:bg-pink-200 dark:hover:bg-pink-800',
  },
  cta: {
    title: 'Call-to-Actions',
    bgColor: 'bg-red-50 dark:bg-red-950/20',
    borderColor: 'border-red-200 dark:border-red-800',
    textColor: 'text-red-800 dark:text-red-200',
    buttonClass: 'bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300 hover:bg-red-200 dark:hover:bg-red-800',
  },
  tools: {
    title: 'Tool Recommendations',
    bgColor: 'bg-amber-50 dark:bg-amber-950/20',
    borderColor: 'border-amber-200 dark:border-amber-800',
    textColor: 'text-amber-800 dark:text-amber-200',
    buttonClass: 'bg-amber-100 dark:bg-amber-900 text-amber-700 dark:text-amber-300 hover:bg-amber-200 dark:hover:bg-amber-800',
  },
};

export default function GeneratedContent({ 
  type, 
  content, 
  isStreaming, 
  selectedHook, 
  onSelectHook,
  messageId,
  onEdit,
  onUseForNext,
  onRegenerate
}: GeneratedContentProps) {
  const [copied, setCopied] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editedContent, setEditedContent] = useState(content);
  const config = typeConfig[type];

  // Parse hooks for selection - handles both quoted and unquoted formats
  const parseHooks = (text: string): Array<{ num: number; text: string }> => {
    const lines = text.split('\n').filter(line => line.trim());
    const hooks: Array<{ num: number; text: string }> = [];
    
    lines.forEach(line => {
      // Try quoted format first: "1. "Hook text""
      let match = line.match(/^(\d+)\.\s+"(.+)"\s*$/);
      if (match) {
        hooks.push({ num: parseInt(match[1]), text: match[2] });
      } else {
        // Try unquoted format: "1. Hook text."
        match = line.match(/^(\d+)\.\s+(.+?)(?:\.\s*)?$/);
        if (match) {
          hooks.push({ num: parseInt(match[1]), text: match[2].trim() });
        }
      }
    });
    
    return hooks;
  };

  const hooks = type === 'hooks' ? parseHooks(content) : [];

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(editedContent || content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const handleDownload = () => {
    const blob = new Blob([editedContent || content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${type}_${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleSaveEdit = () => {
    if (onEdit && messageId !== undefined) {
      onEdit(messageId, editedContent);
    }
    setIsEditing(false);
  };

  const handleUseForNext = () => {
    if (onUseForNext) {
      onUseForNext(editedContent || content, type);
    }
  };

  return (
    <div className="max-w-3xl">
      <div className={clsx(config.bgColor, config.borderColor, 'border-2 rounded-xl p-6 luxury-shadow-lg')}>
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <h3 className={clsx('text-lg font-semibold', config.textColor)}>
              {config.title}
            </h3>
            {isStreaming && (
              <span className="text-xs text-gray-500 dark:text-gray-400 animate-pulse">Generating...</span>
            )}
            {type === 'hooks' && selectedHook && (
              <span className="text-xs bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 px-2 py-1 rounded">
                Hook #{hooks.findIndex(h => h.text === selectedHook) + 1} selected
              </span>
            )}
          </div>
          <div className="flex gap-2">
            {onRegenerate && !isStreaming && !isEditing && (
              <button
                onClick={onRegenerate}
                className={clsx('p-2 rounded-lg transition flex items-center gap-1.5', config.buttonClass)}
                title="Regenerate content"
              >
                <RefreshCw className="w-4 h-4" />
                <span className="text-xs font-medium hidden sm:inline">Regenerate</span>
              </button>
            )}
            {!isEditing && onEdit && messageId !== undefined && (
              <button
                onClick={() => setIsEditing(true)}
                className={clsx('p-2 rounded-lg transition', config.buttonClass)}
                title="Edit content"
              >
                <Edit className="w-4 h-4" />
              </button>
            )}
            {isEditing && (
              <button
                onClick={handleSaveEdit}
                className={clsx('p-2 rounded-lg transition', config.buttonClass)}
                title="Save changes"
              >
                <CheckCheck className="w-4 h-4" />
              </button>
            )}
            <button
              onClick={handleCopy}
              className={clsx('p-2 rounded-lg transition', config.buttonClass)}
              title="Copy to clipboard"
            >
              {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
            </button>
            <button
              onClick={handleDownload}
              className={clsx('p-2 rounded-lg transition', config.buttonClass)}
              title="Download"
            >
              <Download className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className={clsx('bg-white dark:bg-gray-900 rounded-lg p-4 border', config.borderColor)}>
          {isEditing ? (
            <textarea
              value={editedContent}
              onChange={(e) => setEditedContent(e.target.value)}
              className="w-full h-64 p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 font-sans text-sm focus:ring-2 focus:ring-[#d4a574] focus:border-[#d4a574]"
            />
          ) : (
            <>
              {type === 'hooks' && hooks.length > 0 ? (
                <div className="space-y-2">
                  <p className="text-xs font-medium text-[var(--foreground)]/70 mb-2 tracking-tight">Click a hook to select it:</p>
                  {hooks.map((hook) => (
                    <button
                      key={hook.num}
                      onClick={() => {
                        if (onSelectHook) {
                          onSelectHook(hook.text);
                        }
                      }}
                      className={clsx(
                        'w-full text-left p-3 rounded-xl border-2 transition-all luxury-shadow cursor-pointer',
                        selectedHook === hook.text
                          ? 'border-[var(--accent)] bg-[var(--accent)]/10 dark:bg-[var(--accent)]/20'
                          : 'luxury-border hover:border-[var(--accent)]/50 bg-white dark:bg-[#1a1a1a]'
                      )}
                    >
                      <div className="flex items-start gap-2">
                        <span className="text-xs font-semibold text-[var(--foreground)]/60 min-w-[24px]">
                          {hook.num}.
                        </span>
                        <span className="text-sm text-[var(--foreground)] flex-1 tracking-tight">
                          {hook.text}
                        </span>
                        {selectedHook === hook.text && (
                          <Check className="w-4 h-4 text-[var(--accent)] flex-shrink-0 mt-0.5" />
                        )}
                      </div>
                    </button>
                  ))}
                  {selectedHook && (
                    <div className="mt-4 p-3 bg-[var(--accent)]/10 dark:bg-[var(--accent)]/20 border border-[var(--accent)] rounded-xl luxury-shadow">
                      <p className="text-sm text-[var(--foreground)] mb-3 tracking-tight">
                        <strong>Selected Hook:</strong> "{selectedHook}"
                      </p>
                      {onUseForNext && (
                        <button
                          onClick={() => {
                            onUseForNext(selectedHook, 'hooks');
                          }}
                          className="w-full flex items-center justify-center gap-2 px-4 py-2 luxury-accent hover:opacity-90 text-white rounded-xl transition-all text-sm font-medium luxury-shadow"
                        >
                          Use This Hook to Generate Script <ArrowRight className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  )}
                </div>
              ) : (
                <pre className="whitespace-pre-wrap text-sm text-gray-800 dark:text-gray-200 font-sans">
                  {content || (isStreaming ? 'Generating...' : 'No content generated')}
                </pre>
              )}
            </>
          )}
        </div>

        {/* Action buttons for non-hook content */}
        {type !== 'hooks' && onUseForNext && !isEditing && (
          <div className="mt-4">
            <button
              onClick={handleUseForNext}
              className={clsx(
                'w-full flex items-center justify-center gap-2 px-4 py-2 rounded-lg transition text-sm font-medium',
                type === 'script' 
                  ? 'bg-purple-600 hover:bg-purple-700 text-white'
                  : config.buttonClass
              )}
            >
              Use This to Generate Next Step <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
