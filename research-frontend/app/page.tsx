'use client';

import { useState, FormEvent, ChangeEvent } from 'react';
import ReactMarkdown from 'react-markdown';

export default function Home() {
  const [query, setQuery] = useState('');
  const [provider, setProvider] = useState('gemini');
  const [files, setFiles] = useState<File[]>([]);
  const [report, setReport] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');

  // Handle adding new files without replacing existing ones
  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files);
      setFiles((prev) => [...prev, ...selectedFiles]);
    }
  };

  // Remove a specific file by index
  const removeFile = (indexToRemove: number) => {
    setFiles((prev) => prev.filter((_, index) => index !== indexToRemove));
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError('');
    setReport('');

    try {
      const formData = new FormData();
      formData.append('query', query);
      formData.append('provider', provider);
      
      // Append all selected files to FormData under key "files"
      files.forEach((file) => {
        formData.append('files', file);
      });

      const res = await fetch('https://multi-agent-research-api-hzrj.onrender.com/research', {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) throw new Error(`API Request failed with status ${res.status}`);

      const data = await res.json();
      setReport(data.report || JSON.stringify(data, null, 2));
    } catch (err: any) {
      setError(err.message || 'An error occurred during research.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 p-6 md:p-12 font-sans">
      <div className="max-w-4xl mx-auto space-y-8">
        <header className="border-b border-slate-800 pb-4">
          <h1 className="text-3xl font-bold tracking-tight text-indigo-400">
            Multi-Agent Research Tool
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Synthesize multi-provider research powered by Claude, Gemini, and OpenAI.
          </p>
        </header>

        <form onSubmit={handleSubmit} className="space-y-6 bg-slate-900 p-6 rounded-xl border border-slate-800 shadow-xl">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">Research Query</label>
            <textarea
              rows={3}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-slate-200 focus:ring-2 focus:ring-indigo-500 outline-none"
              placeholder="e.g. Compare the attached documents..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              required
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">AI Provider</label>
              <select
                value={provider}
                onChange={(e) => setProvider(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-slate-200 focus:ring-2 focus:ring-indigo-500 outline-none"
              >
                <option value="gemini">Google Gemini</option>
                <option value="claude">Anthropic Claude</option>
                <option value="openai">OpenAI GPT-4o</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Attach Documents (PDFs)</label>
              <label className="inline-flex items-center px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg cursor-pointer text-sm font-semibold transition">
                <span>+ Add PDF</span>
                <input
                  type="file"
                  accept=".pdf"
                  multiple
                  onChange={handleFileChange}
                  className="hidden"
                />
              </label>
            </div>
          </div>

          {/* List attached PDFs with individual delete buttons */}
          {files.length > 0 && (
            <div className="space-y-2 border-t border-slate-800 pt-4">
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Attached Documents ({files.length})</p>
              <div className="flex flex-wrap gap-2">
                {files.map((file, idx) => (
                  <div key={idx} className="flex items-center space-x-2 bg-slate-950 border border-slate-800 px-3 py-1.5 rounded-lg text-xs text-slate-300">
                    <span className="truncate max-w-[200px]">{file.name}</span>
                    <button
                      type="button"
                      onClick={() => removeFile(idx)}
                      className="text-red-400 hover:text-red-300 font-bold ml-1"
                    >
                      ✕
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-medium py-3 rounded-lg transition duration-200 disabled:opacity-50 cursor-pointer"
          >
            {loading ? 'Synthesizing Research...' : 'Run Research Pipeline'}
          </button>
        </form>

        {error && (
          <div className="p-4 bg-red-950/50 border border-red-800 rounded-lg text-red-300 text-sm">
            {error}
          </div>
        )}

        {report && (
          <section className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
            <h2 className="text-xl font-semibold text-indigo-300">Generated Research Report</h2>
            <div className="prose prose-invert max-w-none text-slate-300 text-sm leading-relaxed">
              <ReactMarkdown>{report}</ReactMarkdown>
            </div>
          </section>
        )}
      </div>
    </main>
  );
}