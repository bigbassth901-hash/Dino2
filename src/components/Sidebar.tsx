import { useState, useRef } from 'react';
import { Upload, Layers, Users, RefreshCw } from 'lucide-react';
import { uploadVideo } from '../services/api';

interface SidebarProps {
  viewType: 'scene' | 'character';
  onViewTypeChange: (type: 'scene' | 'character') => void;
  onRefresh: () => void;
  loading: boolean;
}

export default function Sidebar({ viewType, onViewTypeChange, onRefresh, loading }: SidebarProps) {
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      await uploadVideo(file);
      onRefresh();
    } catch (error) {
      console.error('Upload error:', error);
      alert('Failed to upload video');
    } finally {
      setUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  return (
    <div className="w-80 bg-zinc-900 border-r border-zinc-800 flex flex-col">
      <div className="p-6 border-b border-zinc-800">
        <h1 className="text-2xl font-bold tracking-tight">Film Asset Manager</h1>
        <p className="text-sm text-zinc-400 mt-2">AI-Powered Scene Clustering</p>
      </div>

      <div className="p-6 space-y-6 flex-1">
        <div>
          <h2 className="text-sm font-semibold text-zinc-400 mb-3 uppercase tracking-wide">Upload</h2>
          <input
            ref={fileInputRef}
            type="file"
            accept="video/*"
            onChange={handleFileUpload}
            className="hidden"
            id="video-upload"
          />
          <label
            htmlFor="video-upload"
            className={`flex items-center justify-center gap-2 w-full px-4 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors cursor-pointer ${
              uploading ? 'opacity-50 cursor-not-allowed' : ''
            }`}
          >
            <Upload size={20} />
            {uploading ? 'Uploading...' : 'Upload Video'}
          </label>
        </div>

        <div>
          <h2 className="text-sm font-semibold text-zinc-400 mb-3 uppercase tracking-wide">View Mode</h2>
          <div className="space-y-2">
            <button
              onClick={() => onViewTypeChange('scene')}
              className={`flex items-center gap-3 w-full px-4 py-3 rounded-lg transition-colors ${
                viewType === 'scene'
                  ? 'bg-zinc-800 text-white'
                  : 'text-zinc-400 hover:bg-zinc-800/50 hover:text-white'
              }`}
            >
              <Layers size={20} />
              <span>Scene Clusters</span>
            </button>
            <button
              onClick={() => onViewTypeChange('character')}
              className={`flex items-center gap-3 w-full px-4 py-3 rounded-lg transition-colors ${
                viewType === 'character'
                  ? 'bg-zinc-800 text-white'
                  : 'text-zinc-400 hover:bg-zinc-800/50 hover:text-white'
              }`}
            >
              <Users size={20} />
              <span>Character Clusters</span>
            </button>
          </div>
        </div>

        <div className="pt-4 border-t border-zinc-800">
          <button
            onClick={onRefresh}
            disabled={loading}
            className={`flex items-center justify-center gap-2 w-full px-4 py-3 bg-zinc-800 hover:bg-zinc-700 text-white rounded-lg transition-colors ${
              loading ? 'opacity-50 cursor-not-allowed' : ''
            }`}
          >
            <RefreshCw size={20} className={loading ? 'animate-spin' : ''} />
            Refresh
          </button>
        </div>
      </div>

      <div className="p-6 border-t border-zinc-800">
        <p className="text-xs text-zinc-500">
          Active Learning System
          <br />
          Drag from Noise Bucket to cluster
        </p>
      </div>
    </div>
  );
}
