'use client';

import { useState, useEffect } from 'react';
import { X, FileText, Send, Sparkles, Loader2, Save, Trash2 } from 'lucide-react';

interface IdeaNotesProps {
  isOpen: boolean;
  onClose: () => void;
  onDevelopIdea?: (idea: string) => void;
}

export default function IdeaNotes({ isOpen, onClose, onDevelopIdea }: IdeaNotesProps) {
  const [notes, setNotes] = useState('');
  const [savedNotes, setSavedNotes] = useState<string[]>([]);
  const [isDeveloping, setIsDeveloping] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Load saved notes from localStorage on mount
  useEffect(() => {
    if (isOpen) {
      const saved = localStorage.getItem('ideaNotes');
      if (saved) {
        try {
          const parsed = JSON.parse(saved);
          setSavedNotes(Array.isArray(parsed) ? parsed : []);
        } catch (e) {
          console.error('Error loading saved notes:', e);
          setSavedNotes([]);
        }
      } else {
        setSavedNotes([]);
      }
    }
  }, [isOpen]);

  // Save notes to localStorage
  const saveNotes = () => {
    const trimmedNotes = notes.trim();
    if (trimmedNotes) {
      const updated = [...savedNotes, trimmedNotes];
      setSavedNotes(updated);
      try {
        localStorage.setItem('ideaNotes', JSON.stringify(updated));
        setNotes('');
        setSaveSuccess(true);
        setTimeout(() => setSaveSuccess(false), 2000);
      } catch (e) {
        console.error('Error saving notes:', e);
        alert('Failed to save note. Please try again.');
      }
    }
  };

  // Delete a saved note
  const deleteNote = (index: number) => {
    const updated = savedNotes.filter((_, i) => i !== index);
    setSavedNotes(updated);
    localStorage.setItem('ideaNotes', JSON.stringify(updated));
  };

  // Load a saved note into the editor
  const loadNote = (note: string) => {
    setNotes(note);
  };

  // Develop idea with AI
  const handleDevelopIdea = async () => {
    const trimmedNotes = notes.trim();
    if (!trimmedNotes) {
      alert('Please write an idea first!');
      return;
    }

    setIsDeveloping(true);
    
    try {
      // If onDevelopIdea callback is provided, use it
      if (onDevelopIdea) {
        await new Promise(resolve => setTimeout(resolve, 300)); // Small delay for UX
        onDevelopIdea(trimmedNotes);
        onClose();
      } else {
        alert('Idea development feature will be integrated with the chat system.');
      }
    } catch (error) {
      console.error('Error developing idea:', error);
      alert('Failed to develop idea. Please try again.');
    } finally {
      setIsDeveloping(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white dark:bg-gray-900 rounded-lg shadow-lg w-full max-w-4xl max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex justify-between items-center p-4 border-b border-gray-200 dark:border-gray-800">
          <div className="flex items-center gap-2">
            <FileText className="w-5 h-5 text-[var(--accent)]" />
            <h2 className="text-xl font-bold text-gray-800 dark:text-gray-200">Idea Notes</h2>
            <span className="text-sm text-gray-500 dark:text-gray-400 ml-2">
              Write down your brainstorming ideas and we'll help you develop them
            </span>
          </div>
          <button 
            onClick={onClose} 
            className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
          >
            <X size={24} />
          </button>
        </div>

        <div className="flex-1 flex overflow-hidden">
          {/* Main Editor */}
          <div className="flex-1 flex flex-col p-6">
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Your Idea / Brainstorming Notes
              </label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Write down your ideas, thoughts, concepts, or any content ideas you want to develop. Be as detailed or as brief as you like - we'll help expand and refine them!"
                className="w-full h-64 p-4 border border-gray-300 dark:border-gray-700 rounded-lg resize-none focus:ring-2 focus:ring-[var(--accent)] focus:border-transparent dark:bg-gray-800 dark:text-white"
              />
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                {notes.length} characters
              </p>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3">
              <button
                onClick={handleDevelopIdea}
                disabled={!notes.trim() || isDeveloping}
                className="flex items-center gap-2 px-6 py-3 bg-[var(--accent)] text-white rounded-lg hover:opacity-90 transition-all disabled:opacity-50 disabled:cursor-not-allowed luxury-shadow"
              >
                {isDeveloping ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Developing...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    <span>Develop with AI</span>
                  </>
                )}
              </button>

              <button
                onClick={saveNotes}
                disabled={!notes.trim()}
                className="flex items-center gap-2 px-6 py-3 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed relative"
              >
                <Save className="w-4 h-4" />
                <span>{saveSuccess ? 'Saved!' : 'Save Note'}</span>
                {saveSuccess && (
                  <span className="absolute -top-2 -right-2 w-2 h-2 bg-green-500 rounded-full animate-ping"></span>
                )}
              </button>
            </div>
          </div>

          {/* Saved Notes Sidebar */}
          <div className="w-80 border-l border-gray-200 dark:border-gray-800 flex flex-col">
            <div className="p-4 border-b border-gray-200 dark:border-gray-800">
              <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                Saved Notes ({savedNotes.length})
              </h3>
            </div>
            <div className="flex-1 overflow-y-auto p-4">
              {savedNotes.length > 0 ? (
                <div className="space-y-3">
                  {savedNotes.map((note, index) => (
                    <div
                      key={index}
                      className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
                    >
                      <p className="text-sm text-gray-700 dark:text-gray-300 line-clamp-3 mb-2">
                        {note}
                      </p>
                      <div className="flex gap-2">
                        <button
                          onClick={() => loadNote(note)}
                          className="flex-1 text-xs px-3 py-1.5 bg-[var(--accent)] text-white rounded hover:opacity-90 transition"
                        >
                          Load
                        </button>
                        <button
                          onClick={() => {
                            if (confirm('Delete this note?')) {
                              deleteNote(index);
                            }
                          }}
                          className="px-3 py-1.5 text-xs bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 rounded hover:bg-red-200 dark:hover:bg-red-900/50 transition"
                        >
                          <Trash2 className="w-3 h-3" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center h-full text-center p-6">
                  <FileText className="w-12 h-12 text-gray-300 dark:text-gray-600 mb-3" />
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    No saved notes yet
                  </p>
                  <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
                    Save your ideas to access them later
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

