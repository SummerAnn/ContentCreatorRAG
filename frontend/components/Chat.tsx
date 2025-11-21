'use client';

import { useState, useRef, useEffect } from 'react';
import ChatMessage from './ChatMessage';
import PlatformSelector from './PlatformSelector';
import ReferenceInput from './ReferenceInput';
import GeneratedContent from './GeneratedContent';
import PersonalitySelector from './PersonalitySelector';
import AudienceSelector from './AudienceSelector';
import { Send, Sparkles } from 'lucide-react';
import { historyStorage, Conversation } from '@/lib/history';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  type?: 'hooks' | 'script' | 'shotlist' | 'music' | 'titles' | 'description' | 'tags' | 'thumbnails' | 'beatmap' | 'cta' | 'tools';
  timestamp?: number;
}

interface ChatProps {
  initialAgent?: { platform: string; niche: string; goal: string; personality?: string; audience?: string[]; reference?: string } | null;
  initialConversation?: Conversation | null;
}

export default function Chat({ initialAgent, initialConversation }: ChatProps) {
  const [conversationId, setConversationId] = useState<string>(() => initialConversation?.id || `conv_${Date.now()}`);
  const [messages, setMessages] = useState<Message[]>(() => {
    if (initialConversation) {
      return initialConversation.messages.map(m => ({
        role: m.role as 'user' | 'assistant',
        content: m.content,
        type: m.type as any,
        timestamp: m.timestamp
      }));
    }
    return [];
  });
  const [platform, setPlatform] = useState(initialAgent?.platform || initialConversation?.platform || '');
  const [niche, setNiche] = useState(initialAgent?.niche || initialConversation?.niche || '');
  const [goal, setGoal] = useState(initialAgent?.goal || initialConversation?.goal || 'grow_followers');
  const [personality, setPersonality] = useState(initialAgent?.personality || initialConversation?.personality || 'friendly');
  const [audience, setAudience] = useState<string[]>(initialAgent?.audience || initialConversation?.audience || ['gen_z']);
  const [reference, setReference] = useState(initialAgent?.reference || initialConversation?.messages[0]?.content || '');
  const [isGenerating, setIsGenerating] = useState(false);
  const [currentGeneration, setCurrentGeneration] = useState<{ type: string; content: string } | null>(null);
  const [selectedHook, setSelectedHook] = useState<string>('');
  const [editingContent, setEditingContent] = useState<{ id: number; content: string } | null>(null);
  const [chatInput, setChatInput] = useState('');
  const [isChatting, setIsChatting] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Update when agent or conversation changes
  useEffect(() => {
    if (initialConversation) {
      setPlatform(initialConversation.platform);
      setNiche(initialConversation.niche);
      setGoal(initialConversation.goal || 'grow_followers');
      setPersonality(initialConversation.personality || 'friendly');
      setAudience(initialConversation.audience || ['gen_z']);
      setConversationId(initialConversation.id);
    } else if (initialAgent) {
      setPlatform(initialAgent.platform);
      setNiche(initialAgent.niche);
      setGoal(initialAgent.goal);
      if (initialAgent.personality) setPersonality(initialAgent.personality);
      if (initialAgent.audience) setAudience(initialAgent.audience);
      if (initialAgent.reference) setReference(initialAgent.reference);
      // Create new conversation ID
      setConversationId(`conv_${Date.now()}`);
    }
  }, [initialAgent, initialConversation]);

  // Save conversation automatically when messages change
  useEffect(() => {
    if (messages.length > 0 && platform && niche) {
      // Generate title from first user message or first content generation
      const firstContent = messages.find(m => m.type)?.content || messages[0]?.content || '';
      const title = firstContent.substring(0, 50) || `${platform} ${niche} content`;
      
      const conversation: Conversation = {
        id: conversationId,
        title: title.length > 50 ? title.substring(0, 50) + '...' : title,
        platform,
        niche,
        goal: goal || 'grow_followers',
        personality,
        audience,
        messages: messages.map(m => ({
          role: m.role,
          content: m.content,
          type: m.type,
          timestamp: m.timestamp || Date.now()
        })),
        createdAt: Date.now(),
        updatedAt: Date.now()
      };
      
      // Debounce saves (only save after 1 second of no changes)
      const timeoutId = setTimeout(() => {
        historyStorage.save(conversation);
      }, 1000);
      
      return () => clearTimeout(timeoutId);
    }
  }, [messages, platform, niche, personality, audience, conversationId, goal]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, currentGeneration]);

  const generateContent = async (contentType: 'hooks' | 'script' | 'shotlist' | 'music' | 'titles' | 'description' | 'tags' | 'thumbnails' | 'beatmap' | 'cta' | 'tools') => {
    if (!platform || !niche || !personality || !audience || audience.length === 0) {
      alert('Please fill in all required fields: platform, niche, personality, and at least one audience!');
      return;
    }

    if (isGenerating) {
      return; // Prevent multiple simultaneous requests
    }

    setIsGenerating(true);
    setCurrentGeneration({ type: contentType, content: '' });

    // Add user message
    const userMessage: Message = {
      role: 'user',
      content: `Generate ${contentType} for ${platform} in ${niche} niche`,
      type: contentType,
      timestamp: Date.now()
    };
    setMessages(prev => [...prev, userMessage]);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      // Map content types to API endpoints
      const endpointMap: Record<string, string> = {
        'shotlist': 'shotlist',
        'music': 'music',
        'titles': 'titles',
        'description': 'description',
        'tags': 'tags',
        'thumbnails': 'thumbnails',
        'beatmap': 'beatmap',
        'cta': 'cta',
        'tools': 'tools',
      };
      const endpoint = endpointMap[contentType] || contentType;

      const response = await fetch(`${apiUrl}/api/generate/${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: 'default_user',
          platform,
          niche,
          goal,
          personality,
          audience,
              reference_text: reference,
              content_type: contentType,
              options: {
                duration: 60,
                chosen_hook: selectedHook || messages.find(m => m.type === 'hooks')?.content.split('\n')[0]?.replace(/^\d+\.\s+"/, '').replace(/"$/, '') || '',
                script: messages.find(m => m.type === 'script')?.content || '',
                content_type: contentType
              }
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let fullContent = '';

      if (reader) {
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
                  fullContent += data.chunk;
                  setCurrentGeneration({ type: contentType, content: fullContent });
                }
                if (data.done) {
      // Add assistant message when done
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: fullContent,
        type: contentType,
        timestamp: Date.now()
      }]);
      setCurrentGeneration(null);
      setIsGenerating(false);
      
      // If hooks were generated, allow selection
      if (contentType === 'hooks') {
        // Auto-select first hook as default (can be changed)
        const firstHook = fullContent.split('\n').find(line => /^\d+\.\s+"/.test(line.trim()));
        if (firstHook) {
          const hookText = firstHook.replace(/^\d+\.\s+"/, '').replace(/"$/, '');
          setSelectedHook(hookText);
        }
      }
                }
                if (data.error) {
                  throw new Error(data.error);
                }
              } catch (e) {
                // Skip invalid JSON
              }
            }
          }
        }
      }
    } catch (error) {
      console.error('Generation error:', error);
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      alert(`Error generating content: ${errorMessage}\n\nMake sure the backend is running at http://localhost:8000`);
      setCurrentGeneration(null);
      setIsGenerating(false);
      // Remove the user message if generation failed
      setMessages(prev => prev.slice(0, -1));
    }
  };

  const handleContinueChat = async (userMessage: string) => {
    if (!platform || !niche || !personality || !audience || audience.length === 0) {
      alert('Please fill in all required fields first!');
      return;
    }

    if (isChatting || isGenerating) {
      return;
    }

    setIsChatting(true);

    // Add user message
    const userMsg: Message = {
      role: 'user',
      content: userMessage,
      timestamp: Date.now()
    };
    
    // Update messages state and get the updated array
    let updatedMessages: Message[];
    setMessages(prev => {
      updatedMessages = [...prev, userMsg, {
        role: 'assistant',
        content: '',
        timestamp: Date.now()
      }];
      return updatedMessages;
    });

    const assistantMsgIndex = updatedMessages!.length - 1;

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      
      const response = await fetch(`${apiUrl}/api/chat/continue`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: 'default_user',
          platform,
          niche,
          goal,
          personality,
          audience,
          reference_text: reference,
          conversation_history: updatedMessages!.slice(0, -1).map(m => ({
            role: m.role,
            content: m.content,
            type: m.type
          })),
          user_message: userMessage,
          context_content: updatedMessages!.find(m => m.type)?.content || ''
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let fullContent = '';

      if (reader) {
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
                  fullContent += data.chunk;
                  setMessages(prev => {
                    const updated = [...prev];
                    if (updated[assistantMsgIndex]) {
                      updated[assistantMsgIndex] = {
                        ...updated[assistantMsgIndex],
                        content: fullContent
                      };
                    }
                    return updated;
                  });
                }
                if (data.done) {
                  setIsChatting(false);
                }
                if (data.error) {
                  throw new Error(data.error);
                }
              } catch (e) {
                // Skip invalid JSON
              }
            }
          }
        }
      }
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      alert(`Error: ${errorMessage}`);
      // Remove the last two messages (user message and placeholder)
      setMessages(prev => prev.slice(0, -2));
      setIsChatting(false);
    }
  };

  const isFirstMessage = messages.length === 0;

  return (
    <div className="flex flex-col h-full bg-[var(--background)]">
      {/* Header */}
      <header className="bg-white dark:bg-[#0f0f0f] border-b luxury-border px-6 py-5 luxury-shadow">
        <h2 className="text-xl font-semibold text-[var(--foreground)] tracking-tight">Content Generator</h2>
      </header>

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-[var(--background)]">
        {isFirstMessage ? (
          <div className="max-w-3xl mx-auto text-center mt-20">
            <div className="mb-8">
              <div className="w-16 h-16 mx-auto mb-4 flex items-center justify-center rounded-full bg-gradient-to-br from-[var(--accent)] to-[var(--accent-dark)] luxury-shadow-lg">
                <Sparkles className="w-8 h-8 text-white" />
              </div>
              <h2 className="text-3xl font-bold text-[var(--foreground)] mb-2 tracking-tight">Create Viral Content</h2>
              <p className="text-[var(--foreground)]/70">Start by selecting your platform and niche</p>
            </div>

            <div className="space-y-4 max-w-2xl mx-auto">
              <PlatformSelector value={platform} onChange={setPlatform} />
              
              <input
                suppressHydrationWarning
                className="w-full p-3 luxury-border bg-white dark:bg-[#1a1a1a] text-[var(--foreground)] rounded-lg focus:ring-2 focus:ring-[var(--accent)] focus:border-[var(--accent)] transition luxury-shadow"
                placeholder="Enter your niche (e.g., travel, food, tech, beauty)"
                value={niche}
                onChange={(e) => setNiche(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && platform && niche && personality && audience) {
                    generateContent('hooks');
                  }
                }}
              />

              <PersonalitySelector personality={personality} onChange={setPersonality} />
              
              <AudienceSelector audience={audience} onChange={setAudience} />

              <select
                className="w-full p-3 luxury-border bg-white dark:bg-[#1a1a1a] text-[var(--foreground)] rounded-lg focus:ring-2 focus:ring-[var(--accent)] focus:border-[var(--accent)] transition luxury-shadow"
                value={goal}
                onChange={(e) => setGoal(e.target.value)}
              >
                <option value="grow_followers">Grow Followers</option>
                <option value="drive_traffic">Drive Traffic</option>
                <option value="educate">Educate Audience</option>
                <option value="sell_product">Sell Product/Service</option>
                <option value="build_authority">Build Authority</option>
                <option value="viral_reach">Viral Reach</option>
                <option value="community_engagement">Community Engagement</option>
                <option value="ugc">UGC (User Generated Content)</option>
                <option value="brand_deal">Brand Deal / Sponsored Content</option>
                <option value="entertainment">Entertainment</option>
                <option value="engagement">Maximize Engagement</option>
              </select>

              <ReferenceInput value={reference} onChange={setReference} />

              {/* Generate Buttons */}
              <div className="pt-4 space-y-3">
                {!reference && (
                  <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg p-3 mb-2">
                    <p className="text-xs text-amber-800 dark:text-amber-200 font-medium">
                      <strong>Tip:</strong> Add a detailed reference above for better, more personalized results!
                    </p>
                  </div>
                )}
                
                <div className="grid grid-cols-2 gap-2">
                  <button
                    onClick={() => generateContent('hooks')}
                    disabled={!platform || !niche || !personality || !audience || audience.length === 0 || isGenerating}
                    className="px-4 py-3 luxury-accent hover:opacity-90 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed font-medium transition-all text-sm luxury-shadow-lg hover:shadow-xl"
                  >
                    {isGenerating ? '...' : 'Hooks'}
                  </button>
                  <button
                    onClick={() => generateContent('script')}
                    disabled={!platform || !niche || !personality || !audience || audience.length === 0 || isGenerating}
                    className="px-4 py-3 bg-[#1a1a1a] dark:bg-[#1a1a1a] hover:bg-[#2a2a2a] dark:hover:bg-[#2a2a2a] text-white rounded-xl disabled:opacity-50 disabled:cursor-not-allowed font-medium transition-all text-sm luxury-shadow"
                  >
                    Script
                  </button>
                </div>
                
                <div className="grid grid-cols-3 gap-2">
                  <button
                    onClick={() => generateContent('shotlist')}
                    disabled={!platform || !niche || !personality || !audience || audience.length === 0 || isGenerating}
                    className="px-3 py-2 bg-[#1a1a1a] dark:bg-[#1a1a1a] hover:bg-[#2a2a2a] dark:hover:bg-[#2a2a2a] text-white rounded-xl disabled:opacity-50 disabled:cursor-not-allowed text-xs transition-all luxury-shadow"
                  >
                    Shots
                  </button>
                  <button
                    onClick={() => generateContent('music')}
                    disabled={!platform || !niche || !personality || !audience || audience.length === 0 || isGenerating}
                    className="px-3 py-2 bg-[#1a1a1a] dark:bg-[#1a1a1a] hover:bg-[#2a2a2a] dark:hover:bg-[#2a2a2a] text-white rounded-xl disabled:opacity-50 disabled:cursor-not-allowed text-xs transition-all luxury-shadow"
                  >
                    Music
                  </button>
                  <button
                    onClick={() => generateContent('beatmap')}
                    disabled={!platform || !niche || !personality || !audience || audience.length === 0 || isGenerating}
                    className="px-3 py-2 bg-[#1a1a1a] dark:bg-[#1a1a1a] hover:bg-[#2a2a2a] dark:hover:bg-[#2a2a2a] text-white rounded-xl disabled:opacity-50 disabled:cursor-not-allowed text-xs transition-all luxury-shadow"
                  >
                    Beat Map
                  </button>
                </div>

                <div className="grid grid-cols-3 gap-2">
                  <button
                    onClick={() => generateContent('titles')}
                    disabled={!platform || !niche || !personality || !audience || audience.length === 0 || isGenerating}
                    className="px-3 py-2 bg-[#1a1a1a] dark:bg-[#1a1a1a] hover:bg-[#2a2a2a] dark:hover:bg-[#2a2a2a] text-white rounded-xl disabled:opacity-50 disabled:cursor-not-allowed text-xs transition-all luxury-shadow"
                  >
                    Titles
                  </button>
                  <button
                    onClick={() => generateContent('description')}
                    disabled={!platform || !niche || !personality || !audience || audience.length === 0 || isGenerating}
                    className="px-3 py-2 bg-[#1a1a1a] dark:bg-[#1a1a1a] hover:bg-[#2a2a2a] dark:hover:bg-[#2a2a2a] text-white rounded-xl disabled:opacity-50 disabled:cursor-not-allowed text-xs transition-all luxury-shadow"
                  >
                    Description
                  </button>
                  <button
                    onClick={() => generateContent('tags')}
                    disabled={!platform || !niche || !personality || !audience || audience.length === 0 || isGenerating}
                    className="px-3 py-2 bg-[#1a1a1a] dark:bg-[#1a1a1a] hover:bg-[#2a2a2a] dark:hover:bg-[#2a2a2a] text-white rounded-xl disabled:opacity-50 disabled:cursor-not-allowed text-xs transition-all luxury-shadow"
                  >
                    Tags
                  </button>
                </div>

                <div className="grid grid-cols-3 gap-2">
                  <button
                    onClick={() => generateContent('thumbnails')}
                    disabled={!platform || !niche || !personality || !audience || audience.length === 0 || isGenerating}
                    className="px-3 py-2 bg-[#1a1a1a] dark:bg-[#1a1a1a] hover:bg-[#2a2a2a] dark:hover:bg-[#2a2a2a] text-white rounded-xl disabled:opacity-50 disabled:cursor-not-allowed text-xs transition-all luxury-shadow"
                  >
                    Thumbnails
                  </button>
                  <button
                    onClick={() => generateContent('cta')}
                    disabled={!platform || !niche || !personality || !audience || audience.length === 0 || isGenerating}
                    className="px-3 py-2 bg-[#1a1a1a] dark:bg-[#1a1a1a] hover:bg-[#2a2a2a] dark:hover:bg-[#2a2a2a] text-white rounded-xl disabled:opacity-50 disabled:cursor-not-allowed text-xs transition-all luxury-shadow"
                  >
                    CTAs
                  </button>
                  <button
                    onClick={() => generateContent('tools')}
                    disabled={!platform || !niche || !personality || !audience || audience.length === 0 || isGenerating}
                    className="px-3 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-xl disabled:opacity-50 disabled:cursor-not-allowed text-xs transition-all luxury-shadow"
                  >
                    Tools
                  </button>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <>
            {messages.map((msg, i) => {
              if (msg.role === 'assistant' && msg.type) {
                return (
                  <GeneratedContent
                    key={i}
                    type={msg.type}
                    content={msg.content}
                    isStreaming={false}
                    selectedHook={msg.type === 'hooks' ? selectedHook : undefined}
                    onSelectHook={msg.type === 'hooks' ? setSelectedHook : undefined}
                    messageId={i}
                    onEdit={(id, newContent) => {
                      setMessages(prev => prev.map((m, idx) => 
                        idx === id ? { ...m, content: newContent } : m
                      ));
                    }}
                    onUseForNext={(content, contentType) => {
                      if (contentType === 'hooks') {
                        setSelectedHook(content);
                        // Auto-generate script with selected hook
                        generateContent('script');
                      }
                    }}
                  />
                );
              }
              return <ChatMessage key={i} role={msg.role} content={msg.content} type={msg.type} />;
            })}
            {currentGeneration && (
              <GeneratedContent
                type={currentGeneration.type as any}
                content={currentGeneration.content}
                isStreaming={true}
                selectedHook={currentGeneration.type === 'hooks' ? selectedHook : undefined}
                onSelectHook={currentGeneration.type === 'hooks' ? setSelectedHook : undefined}
                onUseForNext={(content, contentType) => {
                  if (contentType === 'hooks') {
                    setSelectedHook(content);
                    // Auto-generate script with selected hook
                    setTimeout(() => generateContent('script'), 500);
                  }
                }}
              />
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Chat Input for Continued Conversation */}
      {!isFirstMessage && messages.length > 0 && (
        <div className="bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800 px-6 py-4">
          <div className="max-w-3xl mx-auto">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                if (chatInput.trim() && !isChatting && !isGenerating) {
                  handleContinueChat(chatInput.trim());
                  setChatInput('');
                }
              }}
              className="flex gap-2"
            >
                <input
                type="text"
                suppressHydrationWarning
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                placeholder="Ask questions, request revisions, or get more ideas..."
                className="flex-1 p-3 luxury-border rounded-lg bg-white dark:bg-[#1a1a1a] text-[var(--foreground)] focus:ring-2 focus:ring-[var(--accent)] focus:border-[var(--accent)] transition luxury-shadow"
                disabled={isChatting || isGenerating}
              />
              <button
                type="submit"
                disabled={!chatInput.trim() || isChatting || isGenerating}
                className="px-6 py-3 luxury-accent hover:opacity-90 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center gap-2 luxury-shadow"
              >
                <Send className="w-4 h-4" />
                {isChatting ? 'Chatting...' : 'Chat'}
              </button>
            </form>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-2 text-center">
              Continue the conversation to refine, revise, or get more ideas
            </p>
          </div>
        </div>
      )}

      {/* Input area */}
      {!isFirstMessage && (
        <div className="bg-white dark:bg-[#0f0f0f] border-t luxury-border px-6 py-4 luxury-shadow-lg">
          <div className="max-w-4xl mx-auto">
            {!reference && (
              <div className="mb-3 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg p-2">
                <p className="text-xs text-amber-800 dark:text-amber-200">
                  <strong>Tip:</strong> Add a detailed reference for better results! Click the info icon above.
                </p>
              </div>
            )}
            <div className="grid grid-cols-2 md:grid-cols-5 gap-2 mb-2">
              <button
                onClick={() => generateContent('hooks')}
                disabled={isGenerating}
                className="px-3 py-2 luxury-accent hover:opacity-90 text-white rounded-xl disabled:opacity-50 disabled:cursor-not-allowed text-xs transition-all luxury-shadow"
              >
                Hooks
              </button>
              <button
                onClick={() => generateContent('script')}
                disabled={isGenerating}
                className="px-3 py-2 bg-[#1a1a1a] dark:bg-[#1a1a1a] hover:bg-[#2a2a2a] dark:hover:bg-[#2a2a2a] text-white rounded-xl disabled:opacity-50 disabled:cursor-not-allowed text-xs transition-all luxury-shadow"
              >
                Script
              </button>
              <button
                onClick={() => generateContent('shotlist')}
                disabled={isGenerating}
                className="px-3 py-2 bg-[#1a1a1a] dark:bg-[#1a1a1a] hover:bg-[#2a2a2a] dark:hover:bg-[#2a2a2a] text-white rounded-xl disabled:opacity-50 disabled:cursor-not-allowed text-xs transition-all luxury-shadow"
              >
                Shots
              </button>
              <button
                onClick={() => generateContent('music')}
                disabled={isGenerating}
                className="px-3 py-2 bg-[#1a1a1a] dark:bg-[#1a1a1a] hover:bg-[#2a2a2a] dark:hover:bg-[#2a2a2a] text-white rounded-xl disabled:opacity-50 disabled:cursor-not-allowed text-xs transition-all luxury-shadow"
              >
                Music
              </button>
              <button
                onClick={() => generateContent('beatmap')}
                disabled={isGenerating}
                className="px-3 py-2 bg-[#1a1a1a] dark:bg-[#1a1a1a] hover:bg-[#2a2a2a] dark:hover:bg-[#2a2a2a] text-white rounded-xl disabled:opacity-50 disabled:cursor-not-allowed text-xs transition-all luxury-shadow"
              >
                Beat Map
              </button>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
              <button
                onClick={() => generateContent('titles')}
                disabled={isGenerating}
                className="px-3 py-2 bg-[#1a1a1a] dark:bg-[#1a1a1a] hover:bg-[#2a2a2a] dark:hover:bg-[#2a2a2a] text-white rounded-xl disabled:opacity-50 disabled:cursor-not-allowed text-xs transition-all luxury-shadow"
              >
                Titles
              </button>
              <button
                onClick={() => generateContent('description')}
                disabled={isGenerating}
                className="px-3 py-2 bg-[#1a1a1a] dark:bg-[#1a1a1a] hover:bg-[#2a2a2a] dark:hover:bg-[#2a2a2a] text-white rounded-xl disabled:opacity-50 disabled:cursor-not-allowed text-xs transition-all luxury-shadow"
              >
                Description
              </button>
              <button
                onClick={() => generateContent('tags')}
                disabled={isGenerating}
                className="px-3 py-2 bg-[#1a1a1a] dark:bg-[#1a1a1a] hover:bg-[#2a2a2a] dark:hover:bg-[#2a2a2a] text-white rounded-xl disabled:opacity-50 disabled:cursor-not-allowed text-xs transition-all luxury-shadow"
              >
                Tags
              </button>
              <button
                onClick={() => generateContent('thumbnails')}
                disabled={isGenerating}
                className="px-3 py-2 bg-[#1a1a1a] dark:bg-[#1a1a1a] hover:bg-[#2a2a2a] dark:hover:bg-[#2a2a2a] text-white rounded-xl disabled:opacity-50 disabled:cursor-not-allowed text-xs transition-all luxury-shadow"
              >
                Thumbnails
              </button>
                  <button
                    onClick={() => generateContent('cta')}
                    disabled={isGenerating}
                    className="px-3 py-2 bg-[#1a1a1a] dark:bg-[#1a1a1a] hover:bg-[#2a2a2a] dark:hover:bg-[#2a2a2a] text-white rounded-xl disabled:opacity-50 disabled:cursor-not-allowed text-xs transition-all luxury-shadow"
                  >
                    CTAs
                  </button>
                  <button
                    onClick={() => generateContent('tools')}
                    disabled={isGenerating}
                    className="px-3 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-xl disabled:opacity-50 disabled:cursor-not-allowed text-xs transition-all luxury-shadow"
                  >
                    Tools
                  </button>
                </div>
          </div>
        </div>
      )}
    </div>
  );
}

