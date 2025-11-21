'use client';

import { useState, useEffect } from 'react';
import { X, Trash2, MessageSquare, Calendar } from 'lucide-react';
import { historyStorage, Conversation } from '@/lib/history';

interface ConversationHistoryProps {
  isOpen: boolean;
  onClose: () => void;
  onLoadConversation: (conversation: Conversation) => void;
}

export default function ConversationHistory({ isOpen, onClose, onLoadConversation }: ConversationHistoryProps) {
  const [conversations, setConversations] = useState<Conversation[]>([]);

  useEffect(() => {
    if (isOpen) {
      setConversations(historyStorage.getAll());
    }
  }, [isOpen]);

  const handleDelete = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm('Delete this conversation?')) {
      historyStorage.delete(id);
      setConversations(historyStorage.getAll());
    }
  };

  const formatDate = (timestamp: number) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white dark:bg-gray-900 rounded-lg shadow-lg w-full max-w-3xl max-h-[80vh] flex flex-col">
        <div className="flex justify-between items-center p-4 border-b border-gray-200 dark:border-gray-800">
          <div className="flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-[#d4a574]" />
            <h2 className="text-xl font-bold text-gray-800 dark:text-gray-200">Conversation History</h2>
          </div>
          <button 
            onClick={onClose} 
            className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
          >
            <X size={24} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4">
          {conversations.length === 0 ? (
            <div className="text-center py-12">
              <MessageSquare className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 dark:text-gray-400">No conversations yet</p>
              <p className="text-sm text-gray-500 dark:text-gray-500 mt-2">Start creating content to see your history here</p>
            </div>
          ) : (
            <div className="space-y-2">
              {conversations.map((conv) => (
                <div
                  key={conv.id}
                  onClick={() => {
                    onLoadConversation(conv);
                    onClose();
                  }}
                  className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:border-[#d4a574] hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer transition"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-gray-800 dark:text-gray-200 truncate mb-1">
                        {conv.title}
                      </h3>
                      <div className="flex flex-wrap gap-2 text-xs text-gray-600 dark:text-gray-400 mb-2">
                        <span className="capitalize">{conv.platform.replace('_', ' ')}</span>
                        <span>•</span>
                        <span className="capitalize">{conv.niche}</span>
                        <span>•</span>
                        <span className="capitalize">{conv.personality.replace('_', ' ')}</span>
                      </div>
                      <div className="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-500">
                        <div className="flex items-center gap-1">
                          <MessageSquare className="w-3 h-3" />
                          <span>{conv.messages.length} messages</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Calendar className="w-3 h-3" />
                          <span>{formatDate(conv.updatedAt)}</span>
                        </div>
                      </div>
                    </div>
                    <button
                      onClick={(e) => handleDelete(conv.id, e)}
                      className="p-2 text-gray-400 hover:text-red-600 dark:hover:text-red-400 transition"
                      title="Delete conversation"
                    >
                      <Trash2 size={16} />
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

