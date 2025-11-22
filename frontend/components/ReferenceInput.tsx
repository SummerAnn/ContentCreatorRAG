'use client';

import { Upload, Link, FileText, Info, X, Loader2, Check } from 'lucide-react';
import { useState, useRef, useEffect } from 'react';

interface ReferenceInputProps {
  value: string;
  onChange: (value: string) => void;
}

export default function ReferenceInput({ value, onChange }: ReferenceInputProps) {
  const [showTip, setShowTip] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<{ name: string; description: string; preview?: string } | null>(null);
  const [linkContent, setLinkContent] = useState<{ url: string; content: string } | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isExtracting, setIsExtracting] = useState(false);
  const [linkInput, setLinkInput] = useState('');
  const [showLinkInput, setShowLinkInput] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  
  // Remove data-has-listeners attribute after mount (added by browser extensions)
  useEffect(() => {
    const removeExtensionAttributes = () => {
      // Remove from this specific input
      if (inputRef.current && inputRef.current.hasAttribute('data-has-listeners')) {
        inputRef.current.removeAttribute('data-has-listeners');
      }
      // Also check link input
      const linkInput = document.querySelector('input[type="url"]');
      if (linkInput && linkInput.hasAttribute('data-has-listeners')) {
        linkInput.removeAttribute('data-has-listeners');
      }
    };
    
    // Run multiple times to catch attributes added at different times
    const intervals: NodeJS.Timeout[] = [];
    [0, 50, 100, 200, 500, 1000, 2000].forEach(delay => {
      intervals.push(setTimeout(removeExtensionAttributes, delay));
    });
    
    // Also use MutationObserver to catch attributes added dynamically
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (mutation.type === 'attributes' && mutation.attributeName === 'data-has-listeners') {
          const target = mutation.target as HTMLElement;
          if (target.hasAttribute('data-has-listeners')) {
            target.removeAttribute('data-has-listeners');
          }
        }
      });
    });
    
    // Observe the input for attribute changes
    if (inputRef.current) {
      observer.observe(inputRef.current, {
        attributes: true,
        attributeFilter: ['data-has-listeners'],
        attributeOldValue: false
      });
    }
    
    // Also set up interval to check periodically
    const intervalId = setInterval(removeExtensionAttributes, 1000);
    
    return () => {
      intervals.forEach(id => clearTimeout(id));
      clearInterval(intervalId);
      observer.disconnect();
    };
  }, []);

  const examples = [
    "A cozy study session with soft lighting and ambient music",
    "Budget travel tips for exploring Europe on $50/day",
    "Quick morning routine for busy professionals - 5 minutes",
    "Homemade pasta recipe with step-by-step instructions",
    "Product review: comparing three budget laptops under $500"
  ];

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      alert('Please upload an image file (JPG, PNG, etc.)');
      return;
    }

    setIsUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/upload/upload-file`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to upload file');
      }

      const data = await response.json();
      
      // Create preview URL
      const previewUrl = URL.createObjectURL(file);
      
      setUploadedFile({
        name: file.name,
        description: data.description || data.suggestion || 'Image uploaded',
        preview: previewUrl
      });

      // Update reference text with file description
      const fileRef = `[Image: ${file.name}] ${data.description || 'Uploaded for visual reference. Describe the style, vibe, colors, and mood.'}`;
      onChange(value ? `${value}\n\n${fileRef}` : fileRef);
      
    } catch (error) {
      console.error('Upload error:', error);
      alert('Failed to upload file. Please try again.');
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleLinkExtract = async () => {
    if (!linkInput.trim()) {
      alert('Please enter a URL');
      return;
    }

    setIsExtracting(true);
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/upload/extract-link`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: linkInput.trim() }),
      });

      if (!response.ok) {
        throw new Error('Failed to extract link content');
      }

      const data = await response.json();
      
      setLinkContent({
        url: linkInput.trim(),
        content: data.extracted_content
      });

      // Update reference text with extracted content
      const linkRef = `[Link: ${data.url}]\n${data.extracted_content}`;
      onChange(value ? `${value}\n\n${linkRef}` : linkRef);
      
      setLinkInput('');
      setShowLinkInput(false);
      
    } catch (error) {
      console.error('Link extraction error:', error);
      alert('Failed to extract link content. Please check the URL and try again.');
    } finally {
      setIsExtracting(false);
    }
  };

  const removeFile = () => {
    if (uploadedFile?.preview) {
      URL.revokeObjectURL(uploadedFile.preview);
    }
    setUploadedFile(null);
    // Remove file reference from value
    const lines = value.split('\n');
    const filtered = lines.filter(line => !line.includes('[Image:'));
    onChange(filtered.join('\n').trim());
  };

  const removeLink = () => {
    setLinkContent(null);
    // Remove link reference from value
    const lines = value.split('\n');
    const filtered = lines.filter(line => !line.includes('[Link:'));
    onChange(filtered.join('\n').trim());
  };

  return (
    <div className="space-y-2" suppressHydrationWarning>
      <div className="flex items-center justify-between">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          Reference (optional but recommended)
        </label>
        <button
          onClick={() => setShowTip(!showTip)}
          className="p-1 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition"
          title="Why is this important?"
        >
          <Info className="w-4 h-4" />
        </button>
      </div>

      {showTip && (
        <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg p-3 mb-2">
          <p className="text-xs text-amber-800 dark:text-amber-200 font-medium mb-1">
            <strong>Tip:</strong> More descriptive = Better results!
          </p>
          <p className="text-xs text-amber-700 dark:text-amber-300">
            Instead of "travel video", try: "Budget travel tips for exploring Europe on $50/day, focusing on hidden gems and local experiences"
          </p>
          <div className="mt-2 text-xs text-amber-600 dark:text-amber-400">
            <p className="font-medium mb-1">Good examples:</p>
            <ul className="list-disc list-inside space-y-0.5">
              {examples.slice(0, 3).map((ex, i) => (
                <li key={i} className="text-xs">{ex}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      <div className="flex gap-2" suppressHydrationWarning>
        <div className="flex-1 relative" suppressHydrationWarning>
          <FileText className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 dark:text-gray-500 w-5 h-5" />
          <input
            ref={inputRef}
            type="text"
            suppressHydrationWarning
            data-hydration-suppress
            className="w-full pl-10 pr-4 py-3 luxury-border bg-white dark:bg-[#1a1a1a] text-[var(--foreground)] rounded-xl focus:ring-2 focus:ring-[var(--accent)] focus:border-[var(--accent)] transition luxury-shadow"
            placeholder="Describe your content idea in detail... (e.g., 'A cozy study session with soft lighting, ambient music, and productivity tips')"
            value={value}
            onChange={(e) => {
              onChange(e.target.value);
              // Remove extension attributes on change too
              if (e.target.hasAttribute('data-has-listeners')) {
                e.target.removeAttribute('data-has-listeners');
              }
            }}
            onFocus={(e) => {
              // Remove extension attributes when focused
              if (e.target.hasAttribute('data-has-listeners')) {
                e.target.removeAttribute('data-has-listeners');
              }
            }}
            onBlur={(e) => {
              // Remove extension attributes when blurred
              if (e.target.hasAttribute('data-has-listeners')) {
                e.target.removeAttribute('data-has-listeners');
              }
            }}
          />
        </div>
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleFileUpload}
          className="hidden"
          id="file-upload"
        />
        <label
          htmlFor="file-upload"
          className={`px-4 py-3 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition cursor-pointer flex items-center gap-2 ${isUploading ? 'opacity-50 cursor-not-allowed' : ''}`}
          title="Upload reference image (vibe/style you want)"
        >
          {isUploading ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <Upload className="w-5 h-5" />
          )}
        </label>
        <button
          onClick={() => setShowLinkInput(!showLinkInput)}
          className="px-4 py-3 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition flex items-center gap-2"
          title="Add inspiration link"
        >
          <Link className="w-5 h-5" />
        </button>
      </div>

      {/* Link Input */}
      {showLinkInput && (
        <div className="mt-2 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="flex gap-2">
            <input
              type="url"
              suppressHydrationWarning
              value={linkInput}
              onChange={(e) => setLinkInput(e.target.value)}
              placeholder="Paste link to inspiration page..."
              className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-lg text-sm"
              onFocus={(e) => {
                // Remove extension attributes when focused
                e.target.removeAttribute('data-has-listeners');
              }}
              onKeyPress={(e) => {
                if (e.key === 'Enter' && !isExtracting) {
                  handleLinkExtract();
                }
              }}
            />
            <button
              onClick={handleLinkExtract}
              disabled={isExtracting || !linkInput.trim()}
              className="px-4 py-2 luxury-accent hover:opacity-90 text-white rounded-xl disabled:opacity-50 disabled:cursor-not-allowed text-sm transition-all flex items-center gap-2 luxury-shadow"
            >
              {isExtracting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Extracting...
                </>
              ) : (
                <>
                  <Link className="w-4 h-4" />
                  Extract
                </>
              )}
            </button>
            <button
              onClick={() => {
                setShowLinkInput(false);
                setLinkInput('');
              }}
              className="px-3 py-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Uploaded File Preview */}
      {uploadedFile && (
        <div className="mt-2 p-3 bg-blue-50 dark:bg-blue-950/20 border border-blue-200 dark:border-blue-800 rounded-lg">
          <div className="flex items-start gap-3">
            {uploadedFile.preview && (
              <img
                src={uploadedFile.preview}
                alt={uploadedFile.name}
                className="w-16 h-16 object-cover rounded-lg"
              />
            )}
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between mb-1">
                <p className="text-sm font-medium text-blue-900 dark:text-blue-200 truncate">
                  {uploadedFile.name}
                </p>
                <button
                  onClick={removeFile}
                  className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
              <p className="text-xs text-blue-700 dark:text-blue-300">
                {uploadedFile.description}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Extracted Link Content */}
      {linkContent && (
        <div className="mt-2 p-3 bg-green-50 dark:bg-green-950/20 border border-green-200 dark:border-green-800 rounded-lg">
          <div className="flex items-start justify-between mb-2">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <Link className="w-4 h-4 text-green-600 dark:text-green-400 flex-shrink-0" />
                <a
                  href={linkContent.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm font-medium text-green-900 dark:text-green-200 hover:underline truncate"
                >
                  {linkContent.url}
                </a>
              </div>
              <p className="text-xs text-green-700 dark:text-green-300 mt-2 whitespace-pre-wrap">
                {linkContent.content}
              </p>
            </div>
            <button
              onClick={removeLink}
              className="text-green-600 hover:text-green-800 dark:text-green-400 dark:hover:text-green-200 ml-2 flex-shrink-0"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
      <p className="text-xs text-gray-500 dark:text-gray-400">
        <strong>Pro tip:</strong> Include details like mood, setting, key points, or target audience for better AI results
      </p>
    </div>
  );
}
