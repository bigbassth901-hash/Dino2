import axios from 'axios';
import { Cluster, NoiseShot, UploadResponse } from '../types';

const API_BASE_URL = 'http://localhost:8000';

export const uploadVideo = async (file: File): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await axios.post(`${API_BASE_URL}/api/upload`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

export const fetchClusters = async (viewType: 'scene' | 'character' = 'scene'): Promise<Record<string, Cluster>> => {
  const response = await axios.get(`${API_BASE_URL}/api/clusters`, {
    params: { view_type: viewType },
  });

  return response.data.clusters;
};

export const fetchNoiseBucket = async (): Promise<NoiseShot[]> => {
  const response = await axios.get(`${API_BASE_URL}/api/noise_bucket`);
  return response.data.noise_shots;
};

export const moveShotToCluster = async (shotId: string, targetClusterId: string): Promise<void> => {
  await axios.post(`${API_BASE_URL}/api/move_to_cluster`, {
    shot_id: shotId,
    target_cluster_id: targetClusterId,
  });
};

export const logFeedback = async (anchorId: string, positiveId: string, label: number): Promise<void> => {
  await axios.post(`${API_BASE_URL}/api/log_feedback`, {
    anchor_id: anchorId,
    positive_id: positiveId,
    label,
  });
};
