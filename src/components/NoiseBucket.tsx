import { useDraggable } from '@dnd-kit/core';
import { AlertTriangle } from 'lucide-react';
import { NoiseShot } from '../types';

interface NoiseBucketProps {
  shots: NoiseShot[];
  loading: boolean;
}

export default function NoiseBucket({ shots, loading }: NoiseBucketProps) {
  return (
    <div className="w-96 bg-zinc-900 border-l border-zinc-800 flex flex-col overflow-hidden">
      <div className="p-6 border-b border-zinc-800">
        <div className="flex items-center gap-3">
          <AlertTriangle size={24} className="text-amber-500" />
          <div>
            <h2 className="text-xl font-bold">Noise Bucket</h2>
            <p className="text-sm text-zinc-400">Unclassified shots</p>
          </div>
        </div>
        <div className="mt-3 text-2xl font-bold text-amber-500">{shots.length}</div>
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        {loading ? (
          <div className="text-center text-zinc-400 py-8">Loading...</div>
        ) : shots.length === 0 ? (
          <div className="text-center text-zinc-500 py-8">
            <p>No noise shots</p>
            <p className="text-xs mt-2">All shots are classified</p>
          </div>
        ) : (
          <div className="space-y-3">
            {shots.map((shot) => (
              <DraggableShot key={shot.shot_id} shot={shot} />
            ))}
          </div>
        )}
      </div>

      <div className="p-4 border-t border-zinc-800 bg-zinc-900/50">
        <p className="text-xs text-zinc-500">
          Drag shots to clusters to train the AI
        </p>
      </div>
    </div>
  );
}

interface DraggableShotProps {
  shot: NoiseShot;
}

function DraggableShot({ shot }: DraggableShotProps) {
  const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({
    id: shot.shot_id,
  });

  const style = transform
    ? {
        transform: `translate3d(${transform.x}px, ${transform.y}px, 0)`,
      }
    : undefined;

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...listeners}
      {...attributes}
      className={`group cursor-grab active:cursor-grabbing ${
        isDragging ? 'opacity-50' : ''
      }`}
    >
      <div className="bg-zinc-800 rounded-lg overflow-hidden transition-all hover:ring-2 hover:ring-amber-500">
        <div className="aspect-video">
          <img
            src={`http://localhost:8000/${shot.keyframe_path}`}
            alt={shot.shot_id}
            className="w-full h-full object-cover"
          />
        </div>
        <div className="p-2">
          <p className="text-xs text-zinc-400 truncate">{shot.shot_id}</p>
        </div>
      </div>
    </div>
  );
}
