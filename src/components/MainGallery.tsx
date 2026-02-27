import { useState } from 'react';
import { useDroppable } from '@dnd-kit/core';
import { ChevronDown, ChevronRight, Folder } from 'lucide-react';
import { Cluster } from '../types';

interface MainGalleryProps {
  clusters: Cluster[];
  loading: boolean;
}

export default function MainGallery({ clusters, loading }: MainGalleryProps) {
  const [expandedClusters, setExpandedClusters] = useState<Set<string>>(new Set());

  const toggleCluster = (clusterId: string) => {
    setExpandedClusters((prev) => {
      const next = new Set(prev);
      if (next.has(clusterId)) {
        next.delete(clusterId);
      } else {
        next.add(clusterId);
      }
      return next;
    });
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-zinc-400">Loading clusters...</div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto p-8">
      <div className="max-w-7xl mx-auto">
        <h2 className="text-3xl font-bold mb-8">Scene Clusters</h2>

        {clusters.length === 0 ? (
          <div className="text-center py-16">
            <Folder size={64} className="mx-auto text-zinc-700 mb-4" />
            <p className="text-zinc-400">No clusters yet</p>
            <p className="text-sm text-zinc-600 mt-2">Upload a video to get started</p>
          </div>
        ) : (
          <div className="space-y-4">
            {clusters.map((cluster) => (
              <ClusterFolder
                key={cluster.cluster_id}
                cluster={cluster}
                expanded={expandedClusters.has(cluster.cluster_id)}
                onToggle={() => toggleCluster(cluster.cluster_id)}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

interface ClusterFolderProps {
  cluster: Cluster;
  expanded: boolean;
  onToggle: () => void;
}

function ClusterFolder({ cluster, expanded, onToggle }: ClusterFolderProps) {
  const { setNodeRef, isOver } = useDroppable({
    id: cluster.cluster_id,
  });

  return (
    <div
      ref={setNodeRef}
      className={`bg-zinc-900 rounded-lg border transition-colors ${
        isOver ? 'border-blue-500 bg-zinc-800' : 'border-zinc-800'
      }`}
    >
      <button
        onClick={onToggle}
        className="w-full flex items-center gap-3 p-4 hover:bg-zinc-800/50 transition-colors"
      >
        {expanded ? <ChevronDown size={20} /> : <ChevronRight size={20} />}
        <Folder size={20} className="text-blue-400" />
        <span className="font-semibold">{cluster.cluster_id}</span>
        <span className="text-sm text-zinc-500 ml-auto">{cluster.shots.length} shots</span>
      </button>

      {expanded && (
        <div className="p-4 border-t border-zinc-800">
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
            {cluster.shots.map((shot) => (
              <div key={shot.id} className="group relative">
                <div className="aspect-video rounded-lg overflow-hidden bg-zinc-800">
                  <img
                    src={`http://localhost:8000/${shot.keyframe_path}`}
                    alt={shot.id}
                    className="w-full h-full object-cover"
                  />
                </div>
                <div className="mt-2 text-xs text-zinc-500 truncate">{shot.id}</div>
                {shot.similarity && (
                  <div className="mt-1 text-xs text-blue-400">
                    Similarity: {(shot.similarity * 100).toFixed(1)}%
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
