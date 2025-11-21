export interface Conversation {
  id: string;
  title: string;
  platform: string;
  niche: string;
  goal?: string;
  personality: string;
  audience: string[];
  messages: Array<{
    role: 'user' | 'assistant';
    content: string;
    type?: string;
    timestamp: number;
  }>;
  createdAt: number;
  updatedAt: number;
}

const STORAGE_KEY = 'creatorflow_conversations';

export const historyStorage = {
  getAll: (): Conversation[] => {
    if (typeof window === 'undefined') return [];
    try {
      const data = localStorage.getItem(STORAGE_KEY);
      return data ? JSON.parse(data) : [];
    } catch {
      return [];
    }
  },

  getById: (id: string): Conversation | null => {
    const conversations = historyStorage.getAll();
    return conversations.find(c => c.id === id) || null;
  },

  save: (conversation: Conversation): void => {
    if (typeof window === 'undefined') return;
    try {
      const conversations = historyStorage.getAll();
      const existingIndex = conversations.findIndex(c => c.id === conversation.id);
      
      if (existingIndex >= 0) {
        conversations[existingIndex] = conversation;
      } else {
        conversations.unshift(conversation); // Add to beginning
      }
      
      // Sort by updatedAt descending
      conversations.sort((a, b) => b.updatedAt - a.updatedAt);
      
      // Keep only last 100 conversations
      const trimmed = conversations.slice(0, 100);
      
      localStorage.setItem(STORAGE_KEY, JSON.stringify(trimmed));
    } catch (error) {
      console.error('Failed to save conversation:', error);
    }
  },

  delete: (id: string): void => {
    if (typeof window === 'undefined') return;
    try {
      const conversations = historyStorage.getAll();
      const filtered = conversations.filter(c => c.id !== id);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered));
    } catch (error) {
      console.error('Failed to delete conversation:', error);
    }
  },

  clear: (): void => {
    if (typeof window === 'undefined') return;
    localStorage.removeItem(STORAGE_KEY);
  },
};

