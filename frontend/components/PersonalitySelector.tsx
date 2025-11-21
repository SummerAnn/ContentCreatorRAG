'use client';

interface PersonalitySelectorProps {
  personality: string;
  onChange: (value: string) => void;
}

const personalities = [
  { 
    id: 'friendly', 
    label: 'Friendly / Girl Next Door', 
    description: 'Conversational, warm, "hi girly", "hey everyone" vibes',
    examples: ['Hi girly!', 'Hey everyone!', 'So I was thinking...']
  },
  { 
    id: 'educational', 
    label: 'Educational / Smart', 
    description: 'Informative, expert, "let me explain", fact-driven',
    examples: ['Have you heard...', 'Did you know...', 'Let me explain...']
  },
  { 
    id: 'motivational', 
    label: 'Motivational', 
    description: 'Inspiring, uplifting, empowering messages',
    examples: ['You can do this!', 'Here\'s how to...', 'Believe in yourself']
  },
  { 
    id: 'funny', 
    label: 'Funny / Light-hearted', 
    description: 'Humorous, playful, entertaining, comedic',
    examples: ['Wait until you see...', 'This is wild!', 'You won\'t believe...']
  },
  { 
    id: 'rage_bait', 
    label: 'Rage Bait / Controversial', 
    description: 'Provocative, controversial, attention-grabbing',
    examples: ['This will make you angry...', 'Hot take:', 'Unpopular opinion:']
  },
  { 
    id: 'storytelling', 
    label: 'Storytelling', 
    description: 'Narrative-driven, personal stories, "so I was..."',
    examples: ['So I was...', 'Let me tell you about...', 'This happened to me...']
  },
  { 
    id: 'authentic', 
    label: 'Authentic / Raw', 
    description: 'Real, unfiltered, honest, vulnerable',
    examples: ['I need to be honest...', 'Real talk:', 'No BS, here\'s...']
  },
  { 
    id: 'luxury', 
    label: 'Luxury / Aspirational', 
    description: 'High-end, premium, aspirational, sophisticated',
    examples: ['This luxury...', 'Elevated style...', 'Sophisticated approach...']
  },
  { 
    id: 'minimalist', 
    label: 'Minimalist / Clean', 
    description: 'Simple, clean, focused, refined',
    examples: ['Let\'s keep it simple...', 'Clean and focused...', 'Essentials only...']
  },
  { 
    id: 'energetic', 
    label: 'Energetic / Hyper', 
    description: 'High energy, fast-paced, exciting, enthusiastic',
    examples: ['OMG you guys!', 'This is INSANE!', 'You NEED to see this!']
  },
  { 
    id: 'calm', 
    label: 'Calm / Relaxed', 
    description: 'Peaceful, zen, soothing, meditative',
    examples: ['Let\'s take a moment...', 'Peacefully...', 'Gently speaking...']
  },
  { 
    id: 'quirky', 
    label: 'Quirky / Unique', 
    description: 'Unique, eccentric, unconventional, offbeat',
    examples: ['Here\'s something weird...', 'Random but...', 'You probably don\'t know...']
  },
  { 
    id: 'professional', 
    label: 'Professional / Corporate', 
    description: 'Business-like, formal, polished, corporate',
    examples: ['In today\'s analysis...', 'Let\'s examine...', 'From a business perspective...']
  },
  { 
    id: 'relatable', 
    label: 'Relatable / Down-to-Earth', 
    description: 'Everyday person, relatable struggles, normal life',
    examples: ['We\'ve all been there...', 'Anyone else...', 'Can we talk about...']
  },
];

export default function PersonalitySelector({ personality, onChange }: PersonalitySelectorProps) {
  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
        Creator Personality *
      </label>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {personalities.map((p) => (
          <button
            key={p.id}
            onClick={() => onChange(p.id)}
            className={`
              p-4 border-2 rounded-xl text-left transition-all luxury-shadow
              ${personality === p.id
                ? 'border-[var(--accent)] bg-[var(--accent)]/10 dark:bg-[var(--accent)]/20'
                : 'luxury-border hover:border-[var(--accent)]/50 bg-white dark:bg-[#1a1a1a]'
              }
            `}
          >
            <div className="font-semibold text-sm text-gray-800 dark:text-gray-200 mb-1">
              {p.label}
            </div>
            <div className="text-xs text-gray-600 dark:text-gray-400 mb-2">
              {p.description}
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-500 italic">
              Examples: {p.examples.join(', ')}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}

