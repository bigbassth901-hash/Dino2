import { useState, useEffect } from 'react';
import { DndContext, DragEndEvent, DragOverlay, DragStartEvent } from '@dnd-kit/core';
import Sidebar from './components/Sidebar';
import MainGallery from './components/MainGallery';
import NoiseBucket from './components/NoiseBucket';
import { Cluster, NoiseShot } from './types';
import { fetchClusters, fetchNoiseBucket, moveShotToCluster } from './services/api';

function App() {
  const [clusters, setClusters] = useState<Cluster[]>([]);
  const [noiseBucket, setNoiseBucket] = useState<NoiseShot[]>([]);
  const [viewType, setViewType] = useState<'scene' | 'character'>('scene');
  const [activeDrag, setActiveDrag] = useState<NoiseShot | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadData();
  }, [viewType]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [clustersData, noiseData] = await Promise.all([
        fetchClusters(viewType),
        fetchNoiseBucket()
      ]);
      setClusters(Object.values(clustersData));
      setNoiseBucket(noiseData);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDragStart = (event: DragStartEvent) => {
    const draggedShot = noiseBucket.find(shot => shot.shot_id === event.active.id);
    setActiveDrag(draggedShot || null);
  };

  const handleDragEnd = async (event: DragEndEvent) => {
    const { active, over } = event;

    if (over && active.id !== over.id) {
      const shotId = active.id as string;
      const targetClusterId = over.id as string;

      try {
        await moveShotToCluster(shotId, targetClusterId);
        await loadData();
      } catch (error) {
        console.error('Error moving shot:', error);
      }
    }

    setActiveDrag(null);
  };

  return (
    <DndContext onDragStart={handleDragStart} onDragEnd={handleDragEnd}>
      <div className="min-h-screen bg-zinc-950 text-zinc-100 flex">
        <Sidebar
          viewType={viewType}
          onViewTypeChange={setViewType}
          onRefresh={loadData}
          loading={loading}
        />

        <MainGallery clusters={clusters} loading={loading} />

        <NoiseBucket shots={noiseBucket} loading={loading} />

        <DragOverlay>
          {activeDrag ? (
            <div className="w-32 h-32 rounded-lg overflow-hidden shadow-2xl border-2 border-blue-500">
              <img
                src={`http://localhost:8000/${activeDrag.keyframe_path}`}
                alt="Dragging"
                className="w-full h-full object-cover"
              />
            </div>
          ) : null}
        </DragOverlay>
      </div>
    </DndContext>
  );
}

export default App;
