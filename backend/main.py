from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import json
from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

from services.keyframe_extractor import KeyframeExtractor
from services.embedding_engine import EmbeddingEngine
from services.clustering_engine import ClusteringEngine
from services.storage_service import StorageService

app = FastAPI(title="Film Asset Management API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

keyframe_extractor = KeyframeExtractor()
embedding_engine = EmbeddingEngine()
clustering_engine = ClusteringEngine()
storage_service = StorageService()

os.makedirs("uploads", exist_ok=True)
os.makedirs("keyframes", exist_ok=True)
os.makedirs("training_data", exist_ok=True)

app.mount("/keyframes", StaticFiles(directory="keyframes"), name="keyframes")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

class FeedbackRequest(BaseModel):
    anchor_id: str
    positive_id: str
    label: int

class MoveToClusterRequest(BaseModel):
    shot_id: str
    target_cluster_id: str

@app.get("/")
async def root():
    return {"message": "Film Asset Management API is running"}

@app.post("/api/upload")
async def upload_video(file: UploadFile = File(...)):
    try:
        file_path = f"uploads/{file.filename}"

        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        keyframes = keyframe_extractor.extract_keyframes(file_path)

        if not keyframes:
            raise HTTPException(status_code=400, detail="No keyframes extracted")

        shot_data = []
        for idx, keyframe_data in enumerate(keyframes):
            keyframe_path = keyframe_data["path"]

            scene_vector = embedding_engine.generate_scene_embedding(keyframe_path)
            character_vectors = embedding_engine.generate_character_embeddings(keyframe_path)

            cluster_result = clustering_engine.assign_to_cluster(
                scene_vector=scene_vector,
                character_vectors=character_vectors,
                keyframe_path=keyframe_path
            )

            shot_info = {
                "shot_id": f"{file.filename}_{idx}",
                "keyframe_path": keyframe_path,
                "frame_index": keyframe_data["frame_index"],
                "cluster_type": cluster_result["cluster_type"],
                "cluster_id": cluster_result["cluster_id"],
                "similarity_score": cluster_result["similarity_score"],
                "timestamp": datetime.now().isoformat()
            }

            await storage_service.save_shot(shot_info)
            shot_data.append(shot_info)

        clusters = await clustering_engine.get_all_clusters()

        return JSONResponse({
            "success": True,
            "filename": file.filename,
            "shots_processed": len(shot_data),
            "shots": shot_data,
            "clusters": clusters
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/clusters")
async def get_clusters(view_type: str = "scene"):
    try:
        clusters = await clustering_engine.get_all_clusters(view_type=view_type)
        return JSONResponse({"success": True, "clusters": clusters})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/log_feedback")
async def log_feedback(feedback: FeedbackRequest):
    try:
        feedback_entry = {
            "anchor_id": feedback.anchor_id,
            "positive_id": feedback.positive_id,
            "label": feedback.label,
            "timestamp": datetime.now().isoformat()
        }

        with open("training_data/training_pairs.jsonl", "a") as f:
            f.write(json.dumps(feedback_entry) + "\n")

        await storage_service.save_feedback(feedback_entry)

        return JSONResponse({
            "success": True,
            "message": "Feedback logged successfully"
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/move_to_cluster")
async def move_to_cluster(request: MoveToClusterRequest):
    try:
        result = await clustering_engine.move_shot_to_cluster(
            request.shot_id,
            request.target_cluster_id
        )

        feedback_entry = {
            "anchor_id": request.shot_id,
            "positive_id": request.target_cluster_id,
            "label": 1,
            "timestamp": datetime.now().isoformat()
        }

        with open("training_data/training_pairs.jsonl", "a") as f:
            f.write(json.dumps(feedback_entry) + "\n")

        await storage_service.save_feedback(feedback_entry)

        return JSONResponse({
            "success": True,
            "message": "Shot moved successfully",
            "result": result
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/noise_bucket")
async def get_noise_bucket():
    try:
        noise_shots = await clustering_engine.get_noise_bucket()
        return JSONResponse({"success": True, "noise_shots": noise_shots})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
