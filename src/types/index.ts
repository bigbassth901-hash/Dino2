export interface Shot {
  id: string;
  keyframe_path: string;
  similarity?: number;
  timestamp: string;
}

export interface Cluster {
  cluster_id: string;
  shots: Shot[];
}

export interface NoiseShot {
  shot_id: string;
  keyframe_path: string;
  scene_vector: number[];
  character_vectors: number[][];
  timestamp: string;
}

export interface UploadResponse {
  success: boolean;
  filename: string;
  shots_processed: number;
  shots: any[];
  clusters: Record<string, Cluster>;
}
