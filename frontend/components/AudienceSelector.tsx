'use client';

interface AudienceSelectorProps {
  audience: string[];
  onChange: (value: string[]) => void;
}

const audiences = [
  { 
    id: 'gen_z', 
    label: 'Gen Z (18-27)', 
    description: 'Trendy, fast-paced, slang-friendly, TikTok-native'
  },
  { 
    id: 'millennials', 
    label: 'Millennials (28-43)', 
    description: 'Nostalgic, value-driven, work-life balance focused'
  },
  { 
    id: 'gen_x', 
    label: 'Gen X (44-59)', 
    description: 'Practical, independent, authentic, no-nonsense'
  },
  { 
    id: 'professionals', 
    label: 'Professionals', 
    description: 'Career-focused, ambitious, productivity-oriented'
  },
  { 
    id: 'students', 
    label: 'Students', 
    description: 'Study-focused, budget-conscious, lifestyle-oriented'
  },
  { 
    id: 'parents', 
    label: 'Parents', 
    description: 'Family-focused, time-constrained, practical advice'
  },
  { 
    id: 'creators', 
    label: 'Content Creators', 
    description: 'Industry-focused, growth-minded, trend-aware'
  },
  { 
    id: 'general', 
    label: 'General Audience', 
    description: 'Broad appeal, accessible to all ages'
  },
];

const genders = [
  { id: 'female', label: 'Female' },
  { id: 'male', label: 'Male' },
  { id: 'all', label: 'All Genders' },
];

export default function AudienceSelector({ audience, onChange }: AudienceSelectorProps) {
  const handleToggle = (id: string) => {
    if (audience.includes(id)) {
      onChange(audience.filter(a => a !== id));
    } else {
      onChange([...audience, id]);
    }
  };

  return (
    <div className="space-y-4">
      <div className="space-y-3">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          Target Audience * (Select multiple)
        </label>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {audiences.map((a) => (
            <button
              key={a.id}
              onClick={() => handleToggle(a.id)}
              className={`
                p-3 border-2 rounded-lg text-left transition-all
                ${audience.includes(a.id)
                  ? 'border-[#d4a574] bg-[#d4a574]/10 dark:bg-[#d4a574]/20'
                  : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600 bg-white dark:bg-gray-800'
                }
              `}
            >
              <div className="font-semibold text-xs text-gray-800 dark:text-gray-200 mb-1">
                {a.label}
              </div>
              <div className="text-xs text-gray-600 dark:text-gray-400">
                {a.description}
              </div>
              {audience.includes(a.id) && (
                <div className="mt-2 text-xs text-[#d4a574] font-medium">✓ Selected</div>
              )}
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-3">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          Gender Target (Select one or multiple)
        </label>
        <div className="flex gap-3">
          {genders.map((g) => (
            <button
              key={g.id}
              onClick={() => {
                if (g.id === 'all') {
                  // If "All" is clicked, clear other gender selections
                  const newAudience = audience.filter(a => !['female', 'male'].includes(a));
                  onChange(newAudience.includes('all') ? newAudience.filter(a => a !== 'all') : [...newAudience, 'all']);
                } else {
                  // Toggle individual gender
                  const newAudience = audience.filter(a => a !== 'all');
                  if (newAudience.includes(g.id)) {
                    onChange(newAudience.filter(a => a !== g.id));
                  } else {
                    onChange([...newAudience, g.id]);
                  }
                }
              }}
              className={`
                px-4 py-2 border-2 rounded-lg transition-all
                ${audience.includes(g.id)
                  ? 'border-[#d4a574] bg-[#d4a574]/10 dark:bg-[#d4a574]/20 text-gray-800 dark:text-gray-200'
                  : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300'
                }
              `}
            >
              {g.label}
              {audience.includes(g.id) && (
                <span className="ml-2 text-[#d4a574]">✓</span>
              )}
            </button>
          ))}
        </div>
      </div>

      {audience.length > 0 && (
        <div className="text-xs text-gray-600 dark:text-gray-400">
          Selected: {audience.join(', ')}
        </div>
      )}
    </div>
  );
}
