'use client';

import { useState } from 'react';
import { X, Upload, Link as LinkIcon, FileText, Download, Loader2 } from 'lucide-react';
import { transcribeFile, transcribeUrl, generateCaptions, TranscriptionResponse } from '@/lib/api';

interface TranscriptionProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function Transcription({ isOpen, onClose }: TranscriptionProps) {
  const [activeTab, setActiveTab] = useState<'file' | 'url'>('file');
  const [file, setFile] = useState<File | null>(null);
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<TranscriptionResponse | null>(null);
  const [urlResult, setUrlResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [captionFormat, setCaptionFormat] = useState<'srt' | 'vtt'>('srt');
  const [captions, setCaptions] = useState<string>('');

  const handleFileUpload = async () => {
    if (!file) {
      setError('Please select a file');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await transcribeFile(file);
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to transcribe file');
    } finally {
      setLoading(false);
    }
  };

  const handleUrlTranscribe = async () => {
    if (!url.trim()) {
      setError('Please enter a URL');
      return;
    }

    setLoading(true);
    setError(null);
    setUrlResult(null);

    try {
      const response = await transcribeUrl(url.trim());
      setUrlResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to transcribe URL');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateCaptions = async (text: string) => {
    setLoading(true);
    setError(null);
    setCaptions('');

    try {
      const response = await generateCaptions(text, captionFormat);
      setCaptions(response.content);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate captions');
    } finally {
      setLoading(false);
    }
  };

  const downloadCaptions = () => {
    if (!captions) return;
    const blob = new Blob([captions], { type: 'text/plain' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `captions.${captionFormat}`;
    link.click();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-[#1a1a1a] rounded-lg shadow-xl max-w-4xl w-full p-6 text-white max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <FileText size={28} />
            Transcription
          </h2>
          <button onClick={onClose} className="text-white/70 hover:text-white transition-colors">
            <X size={24} />
          </button>
        </div>

        {error && (
          <div className="mb-4 p-4 bg-red-500/20 border border-red-500/50 rounded-lg text-red-300">
            {error}
          </div>
        )}

        {/* Tabs */}
        <div className="flex gap-2 mb-6 border-b border-white/10">
          <button
            onClick={() => setActiveTab('file')}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === 'file'
                ? 'border-b-2 border-purple-500 text-purple-400'
                : 'text-white/60 hover:text-white'
            }`}
          >
            <Upload size={18} className="inline mr-2" />
            Upload File
          </button>
          <button
            onClick={() => setActiveTab('url')}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === 'url'
                ? 'border-b-2 border-purple-500 text-purple-400'
                : 'text-white/60 hover:text-white'
            }`}
          >
            <LinkIcon size={18} className="inline mr-2" />
            From URL
          </button>
        </div>

        {/* File Upload Tab */}
        {activeTab === 'file' && (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Upload Audio/Video File</label>
              <div className="border-2 border-dashed border-white/20 rounded-lg p-8 text-center">
                <input
                  type="file"
                  accept="audio/*,video/*"
                  onChange={(e) => setFile(e.target.files?.[0] || null)}
                  className="hidden"
                  id="file-upload"
                />
                <label
                  htmlFor="file-upload"
                  className="cursor-pointer flex flex-col items-center gap-2"
                >
                  <Upload size={32} className="text-white/60" />
                  <span className="text-white/80">
                    {file ? file.name : 'Click to upload or drag and drop'}
                  </span>
                  <span className="text-sm text-white/60">
                    Supports: MP3, MP4, WAV, M4A, etc.
                  </span>
                </label>
              </div>
            </div>
            <button
              onClick={handleFileUpload}
              disabled={loading || !file}
              className="w-full px-4 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:opacity-90 transition-all disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 size={20} className="animate-spin" />
                  Transcribing...
                </>
              ) : (
                <>
                  <FileText size={20} />
                  Transcribe File
                </>
              )}
            </button>

            {result && (
              <div className="mt-6 p-6 bg-[#0f0f0f] rounded-lg border border-white/10">
                <div className="grid grid-cols-3 gap-4 mb-4">
                  <div className="bg-[#1a1a1a] p-3 rounded-lg">
                    <div className="text-sm text-white/60">Language</div>
                    <div className="text-lg font-semibold">{result.language}</div>
                  </div>
                  <div className="bg-[#1a1a1a] p-3 rounded-lg">
                    <div className="text-sm text-white/60">Word Count</div>
                    <div className="text-lg font-semibold">{result.word_count}</div>
                  </div>
                  <div className="bg-[#1a1a1a] p-3 rounded-lg">
                    <div className="text-sm text-white/60">Duration</div>
                    <div className="text-lg font-semibold">{result.duration.toFixed(1)}s</div>
                  </div>
                </div>
                <div>
                  <h4 className="font-semibold mb-2">Transcript</h4>
                  <div className="bg-[#1a1a1a] p-4 rounded-lg text-white/80 max-h-60 overflow-y-auto">
                    {result.text}
                  </div>
                </div>
                <div className="mt-4 flex gap-2">
                  <select
                    value={captionFormat}
                    onChange={(e) => setCaptionFormat(e.target.value as 'srt' | 'vtt')}
                    className="px-3 py-2 bg-[#0f0f0f] border border-white/10 rounded-lg text-white"
                  >
                    <option value="srt">SRT</option>
                    <option value="vtt">VTT</option>
                  </select>
                  <button
                    onClick={() => handleGenerateCaptions(result.text)}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:opacity-90 transition-all flex items-center gap-2"
                  >
                    Generate Captions
                  </button>
                  {captions && (
                    <button
                      onClick={downloadCaptions}
                      className="px-4 py-2 bg-green-600 text-white rounded-lg hover:opacity-90 transition-all flex items-center gap-2"
                    >
                      <Download size={16} />
                      Download
                    </button>
                  )}
                </div>
                {captions && (
                  <div className="mt-4 bg-[#1a1a1a] p-4 rounded-lg max-h-40 overflow-y-auto">
                    <pre className="text-xs text-white/80 whitespace-pre-wrap">{captions}</pre>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* URL Tab */}
        {activeTab === 'url' && (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Video URL</label>
              <input
                type="text"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://youtube.com/watch?v=... or https://tiktok.com/@user/video/..."
                className="w-full p-3 bg-[#0f0f0f] border border-white/10 rounded-lg text-white placeholder-white/40"
              />
            </div>
            <button
              onClick={handleUrlTranscribe}
              disabled={loading || !url.trim()}
              className="w-full px-4 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:opacity-90 transition-all disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 size={20} className="animate-spin" />
                  Transcribing...
                </>
              ) : (
                <>
                  <LinkIcon size={20} />
                  Transcribe from URL
                </>
              )}
            </button>

            {urlResult && (
              <div className="mt-6 p-6 bg-[#0f0f0f] rounded-lg border border-white/10">
                <h4 className="font-semibold mb-2">{urlResult.title}</h4>
                <div className="mb-4 text-sm text-white/60">
                  Duration: {urlResult.duration}s • Language: {urlResult.language}
                </div>
                <div>
                  <h4 className="font-semibold mb-2">Transcript</h4>
                  <div className="bg-[#1a1a1a] p-4 rounded-lg text-white/80 max-h-60 overflow-y-auto">
                    {urlResult.transcription}
                  </div>
                </div>
                <div className="mt-4 flex gap-2">
                  <select
                    value={captionFormat}
                    onChange={(e) => setCaptionFormat(e.target.value as 'srt' | 'vtt')}
                    className="px-3 py-2 bg-[#0f0f0f] border border-white/10 rounded-lg text-white"
                  >
                    <option value="srt">SRT</option>
                    <option value="vtt">VTT</option>
                  </select>
                  <button
                    onClick={() => handleGenerateCaptions(urlResult.transcription)}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:opacity-90 transition-all flex items-center gap-2"
                  >
                    Generate Captions
                  </button>
                  {captions && (
                    <button
                      onClick={downloadCaptions}
                      className="px-4 py-2 bg-green-600 text-white rounded-lg hover:opacity-90 transition-all flex items-center gap-2"
                    >
                      <Download size={16} />
                      Download
                    </button>
                  )}
                </div>
                {captions && (
                  <div className="mt-4 bg-[#1a1a1a] p-4 rounded-lg max-h-40 overflow-y-auto">
                    <pre className="text-xs text-white/80 whitespace-pre-wrap">{captions}</pre>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

