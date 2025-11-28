'use client';

import { useState, useEffect } from 'react';
import { Zap, Calendar, Target, AlertCircle, Clock, CheckCircle2, Loader2, X } from 'lucide-react';

interface Workflow {
  id: string;
  name: string;
  description: string;
  time: string;
  icon: string;
}

export default function OneClickWorkflows({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedWorkflow, setSelectedWorkflow] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);
  const [niche, setNiche] = useState('lifestyle');
  const [platform, setPlatform] = useState('tiktok');

  // Fetch workflows on mount
  useEffect(() => {
    if (isOpen) {
      fetchWorkflows();
    }
  }, [isOpen]);

  const fetchWorkflows = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/workflows/list');
      const data = await response.json();
      setWorkflows(data.workflows);
    } catch (error) {
      console.error('Failed to fetch workflows:', error);
    }
  };

  const executeWorkflow = async (workflowType: string) => {
    setIsLoading(true);
    setSelectedWorkflow(workflowType);
    setResult(null);

    try {
      const response = await fetch('http://localhost:8000/api/workflows/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          workflow_type: workflowType,
          user_id: 'demo_user',
          niche,
          platform,
          additional_params: {}
        })
      });

      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('Workflow execution failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getWorkflowIcon = (iconEmoji: string) => {
    switch (iconEmoji) {
      case '⚡': return <Zap className="w-6 h-6" />;
      case '📅': return <Calendar className="w-6 h-6" />;
      case '🎯': return <Target className="w-6 h-6" />;
      case '🚨': return <AlertCircle className="w-6 h-6" />;
      default: return <Zap className="w-6 h-6" />;
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-[#1a1a1a] rounded-lg shadow-xl max-w-6xl w-full p-6 text-white max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <Zap size={28} />
            One-Click Workflows
          </h2>
          <button onClick={onClose} className="text-white/70 hover:text-white transition-colors">
            <X size={24} />
          </button>
        </div>

        {/* Settings */}
        <div className="bg-[#2a2a2a] rounded-lg border border-gray-700 p-6 mb-6">
          <h2 className="font-bold text-lg mb-4 text-white">Quick Settings</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-white/90 mb-2">
                Niche
              </label>
              <select
                value={niche}
                onChange={(e) => setNiche(e.target.value)}
                className="w-full px-4 py-2 bg-[#1a1a1a] border border-gray-700 rounded-lg text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              >
                <option value="lifestyle">Lifestyle</option>
                <option value="beauty">Beauty</option>
                <option value="fashion">Fashion</option>
                <option value="business">Business</option>
                <option value="finance">Finance</option>
                <option value="education">Education</option>
                <option value="gaming">Gaming</option>
                <option value="entertainment">Entertainment</option>
                <option value="travel">Travel</option>
                <option value="food">Food</option>
                <option value="tech">Tech</option>
                <option value="fitness">Fitness</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-white/90 mb-2">
                Platform
              </label>
              <select
                value={platform}
                onChange={(e) => setPlatform(e.target.value)}
                className="w-full px-4 py-2 bg-[#1a1a1a] border border-gray-700 rounded-lg text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              >
                <option value="tiktok">TikTok</option>
                <option value="instagram">Instagram Reels</option>
                <option value="youtube">YouTube Shorts</option>
              </select>
            </div>
          </div>
        </div>

        {/* Workflows Grid */}
        <div className="grid md:grid-cols-2 gap-6 mb-6">
          {workflows.map((workflow) => (
            <div
              key={workflow.id}
              className="bg-[#2a2a2a] rounded-lg border-2 border-gray-700 p-6 hover:border-purple-500/50 transition-all"
            >
              <div className="flex items-start gap-4">
                <div className="p-3 bg-purple-500/20 rounded-lg text-purple-400 border border-purple-500/50">
                  {getWorkflowIcon(workflow.icon)}
                </div>
                
                <div className="flex-1">
                  <h3 className="font-bold text-lg text-white mb-1">
                    {workflow.name}
                  </h3>
                  <p className="text-sm text-white/70 mb-3">
                    {workflow.description}
                  </p>
                  
                  <div className="flex items-center gap-2 mb-4">
                    <Clock className="w-4 h-4 text-white/50" />
                    <span className="text-xs font-medium text-white/60">
                      {workflow.time}
                    </span>
                  </div>

                    <button
                      onClick={() => executeWorkflow(workflow.id)}
                      disabled={isLoading && selectedWorkflow === workflow.id}
                      className="w-full px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                    >
                      {isLoading && selectedWorkflow === workflow.id ? (
                        <>
                          <Loader2 className="w-4 h-4 animate-spin" />
                          Generating...
                        </>
                      ) : (
                        <>
                          <Zap className="w-4 h-4" />
                          Execute Workflow
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>

        {/* Results */}
        {result && (
          <div className="bg-[#2a2a2a] rounded-lg border border-gray-700 p-6">
            <div className="flex items-center gap-2 mb-4">
              <CheckCircle2 className="w-6 h-6 text-green-400" />
              <h2 className="font-bold text-lg text-white">Workflow Complete!</h2>
              <span className="ml-auto text-sm text-white/60">
                Saved you {result.time_saved}
              </span>
            </div>

            <div className="space-y-4">
              {Object.entries(result.content).map(([key, value]) => (
                <div key={key} className="border-l-4 border-purple-500 pl-4">
                  <h3 className="font-medium text-white/90 mb-2 capitalize">
                    {key.replace(/_/g, ' ')}
                  </h3>
                  <div className="bg-[#1a1a1a] p-4 rounded-lg border border-gray-700">
                    <pre className="whitespace-pre-wrap text-sm text-white/80">
                      {typeof value === 'string' ? value : JSON.stringify(value, null, 2)}
                    </pre>
                  </div>
                </div>
              ))}
            </div>

            {/* Next Steps */}
            <div className="mt-6 p-4 bg-purple-500/10 rounded-lg border border-purple-500/30">
              <h3 className="font-medium text-purple-300 mb-2">Next Steps:</h3>
              <ul className="space-y-1">
                {result.next_steps.map((step: string, i: number) => (
                  <li key={i} className="flex items-center gap-2 text-sm text-purple-200">
                    <span className="text-purple-400">•</span>
                    {step}
                  </li>
                ))}
              </ul>
            </div>

            <button
              onClick={() => setResult(null)}
              className="mt-4 w-full px-4 py-2 border border-gray-600 text-white/90 rounded-lg hover:bg-[#2a2a2a] transition-colors"
            >
              Start New Workflow
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

