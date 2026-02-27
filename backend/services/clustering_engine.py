import chromadb
from chromadb.config import Settings
import numpy as np
from typing import List, Dict, Optional
import uuid
from datetime import datetime

class ClusteringEngine:
    def __init__(self, scene_threshold: float = 0.85, character_threshold: float = 0.75, noise_threshold: float = 0.5):
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory="./chroma_db"
        ))

        try:
            self.scene_collection = self.client.get_collection("scene_clusters")
        except:
            self.scene_collection = self.client.create_collection(
                name="scene_clusters",
                metadata={"hnsw:space": "cosine"}
            )

        try:
            self.character_collection = self.client.get_collection("character_clusters")
        except:
            self.character_collection = self.client.create_collection(
                name="character_clusters",
                metadata={"hnsw:space": "cosine"}
            )

        self.scene_threshold = scene_threshold
        self.character_threshold = character_threshold
        self.noise_threshold = noise_threshold

        self.clusters = {}
        self.noise_bucket = []

    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        vec1_np = np.array(vec1)
        vec2_np = np.array(vec2)

        dot_product = np.dot(vec1_np, vec2_np)
        norm1 = np.linalg.norm(vec1_np)
        norm2 = np.linalg.norm(vec2_np)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def assign_to_cluster(
        self,
        scene_vector: List[float],
        character_vectors: List[List[float]],
        keyframe_path: str
    ) -> Dict:
        shot_id = str(uuid.uuid4())

        try:
            scene_results = self.scene_collection.query(
                query_embeddings=[scene_vector],
                n_results=1
            )

            if scene_results['ids'] and len(scene_results['ids'][0]) > 0:
                best_distance = scene_results['distances'][0][0]
                similarity = 1 - best_distance

                if similarity >= self.scene_threshold:
                    cluster_id = scene_results['ids'][0][0]

                    self.scene_collection.add(
                        embeddings=[scene_vector],
                        ids=[shot_id],
                        metadatas=[{
                            "keyframe_path": keyframe_path,
                            "cluster_id": cluster_id,
                            "similarity": float(similarity),
                            "timestamp": datetime.now().isoformat()
                        }]
                    )

                    if character_vectors:
                        self._assign_character_cluster(
                            shot_id,
                            character_vectors,
                            cluster_id,
                            keyframe_path
                        )

                    return {
                        "cluster_type": "scene",
                        "cluster_id": cluster_id,
                        "similarity_score": float(similarity),
                        "shot_id": shot_id
                    }

                elif similarity < self.noise_threshold:
                    self.noise_bucket.append({
                        "shot_id": shot_id,
                        "keyframe_path": keyframe_path,
                        "scene_vector": scene_vector,
                        "character_vectors": character_vectors,
                        "timestamp": datetime.now().isoformat()
                    })

                    return {
                        "cluster_type": "noise",
                        "cluster_id": "noise_bucket",
                        "similarity_score": float(similarity),
                        "shot_id": shot_id
                    }

            new_cluster_id = f"scene_{str(uuid.uuid4())[:8]}"

            self.scene_collection.add(
                embeddings=[scene_vector],
                ids=[shot_id],
                metadatas=[{
                    "keyframe_path": keyframe_path,
                    "cluster_id": new_cluster_id,
                    "similarity": 1.0,
                    "timestamp": datetime.now().isoformat()
                }]
            )

            if character_vectors:
                self._assign_character_cluster(
                    shot_id,
                    character_vectors,
                    new_cluster_id,
                    keyframe_path
                )

            return {
                "cluster_type": "scene",
                "cluster_id": new_cluster_id,
                "similarity_score": 1.0,
                "shot_id": shot_id
            }

        except Exception as e:
            print(f"Error in clustering: {e}")

            self.noise_bucket.append({
                "shot_id": shot_id,
                "keyframe_path": keyframe_path,
                "scene_vector": scene_vector,
                "character_vectors": character_vectors,
                "timestamp": datetime.now().isoformat()
            })

            return {
                "cluster_type": "noise",
                "cluster_id": "noise_bucket",
                "similarity_score": 0.0,
                "shot_id": shot_id
            }

    def _assign_character_cluster(
        self,
        shot_id: str,
        character_vectors: List[List[float]],
        scene_cluster_id: str,
        keyframe_path: str
    ):
        for char_idx, char_vector in enumerate(character_vectors):
            char_id = f"{shot_id}_char_{char_idx}"

            self.character_collection.add(
                embeddings=[char_vector],
                ids=[char_id],
                metadatas=[{
                    "shot_id": shot_id,
                    "scene_cluster_id": scene_cluster_id,
                    "keyframe_path": keyframe_path,
                    "character_index": char_idx,
                    "timestamp": datetime.now().isoformat()
                }]
            )

    async def get_all_clusters(self, view_type: str = "scene") -> Dict:
        if view_type == "scene":
            all_data = self.scene_collection.get()
        else:
            all_data = self.character_collection.get()

        clusters = {}

        for idx, metadata in enumerate(all_data['metadatas']):
            cluster_id = metadata.get('cluster_id') or metadata.get('scene_cluster_id')

            if cluster_id not in clusters:
                clusters[cluster_id] = {
                    "cluster_id": cluster_id,
                    "shots": []
                }

            clusters[cluster_id]["shots"].append({
                "id": all_data['ids'][idx],
                "keyframe_path": metadata.get('keyframe_path'),
                "similarity": metadata.get('similarity'),
                "timestamp": metadata.get('timestamp')
            })

        return clusters

    async def get_noise_bucket(self) -> List[Dict]:
        return self.noise_bucket

    async def move_shot_to_cluster(self, shot_id: str, target_cluster_id: str) -> Dict:
        noise_item = None
        for idx, item in enumerate(self.noise_bucket):
            if item['shot_id'] == shot_id:
                noise_item = self.noise_bucket.pop(idx)
                break

        if not noise_item:
            raise ValueError(f"Shot {shot_id} not found in noise bucket")

        self.scene_collection.add(
            embeddings=[noise_item['scene_vector']],
            ids=[shot_id],
            metadatas=[{
                "keyframe_path": noise_item['keyframe_path'],
                "cluster_id": target_cluster_id,
                "similarity": 1.0,
                "timestamp": datetime.now().isoformat(),
                "moved_from_noise": True
            }]
        )

        if noise_item['character_vectors']:
            self._assign_character_cluster(
                shot_id,
                noise_item['character_vectors'],
                target_cluster_id,
                noise_item['keyframe_path']
            )

        return {
            "success": True,
            "shot_id": shot_id,
            "target_cluster_id": target_cluster_id
        }
