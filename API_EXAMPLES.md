# API Usage Examples

This document provides practical examples of how to use the Film Asset Management API.

## Base URL

```
http://localhost:8000
```

## Endpoints

### 1. Health Check

Check if the API is running.

**Request:**
```bash
curl http://localhost:8000/
```

**Response:**
```json
{
  "message": "Film Asset Management API is running"
}
```

### 2. Upload Video

Upload a video file for processing.

**Request:**
```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@/path/to/your/video.mp4"
```

**Response:**
```json
{
  "success": true,
  "filename": "video.mp4",
  "shots_processed": 5,
  "shots": [
    {
      "shot_id": "video.mp4_0",
      "keyframe_path": "keyframes/video_frame_0.jpg",
      "frame_index": 0,
      "cluster_type": "scene",
      "cluster_id": "scene_abc123",
      "similarity_score": 0.92,
      "timestamp": "2024-01-01T12:00:00"
    }
  ],
  "clusters": {
    "scene_abc123": {
      "cluster_id": "scene_abc123",
      "shots": [...]
    }
  }
}
```

### 3. Get Clusters

Retrieve all clusters (scene-based or character-based).

**Request (Scene View):**
```bash
curl "http://localhost:8000/api/clusters?view_type=scene"
```

**Request (Character View):**
```bash
curl "http://localhost:8000/api/clusters?view_type=character"
```

**Response:**
```json
{
  "success": true,
  "clusters": {
    "scene_abc123": {
      "cluster_id": "scene_abc123",
      "shots": [
        {
          "id": "shot_id_1",
          "keyframe_path": "keyframes/video_frame_0.jpg",
          "similarity": 0.92,
          "timestamp": "2024-01-01T12:00:00"
        }
      ]
    }
  }
}
```

### 4. Get Noise Bucket

Retrieve all unclassified shots that need human review.

**Request:**
```bash
curl http://localhost:8000/api/noise_bucket
```

**Response:**
```json
{
  "success": true,
  "noise_shots": [
    {
      "shot_id": "video.mp4_3",
      "keyframe_path": "keyframes/video_frame_15.jpg",
      "scene_vector": [0.1, 0.2, ...],
      "character_vectors": [[0.3, 0.4, ...]],
      "timestamp": "2024-01-01T12:00:00"
    }
  ]
}
```

### 5. Move Shot to Cluster

Move a shot from the noise bucket to a specific cluster (human feedback).

**Request:**
```bash
curl -X POST http://localhost:8000/api/move_to_cluster \
  -H "Content-Type: application/json" \
  -d '{
    "shot_id": "video.mp4_3",
    "target_cluster_id": "scene_abc123"
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Shot moved successfully",
  "result": {
    "success": true,
    "shot_id": "video.mp4_3",
    "target_cluster_id": "scene_abc123"
  }
}
```

### 6. Log Feedback

Manually log training feedback (alternative to move_to_cluster).

**Request:**
```bash
curl -X POST http://localhost:8000/api/log_feedback \
  -H "Content-Type: application/json" \
  -d '{
    "anchor_id": "video.mp4_3",
    "positive_id": "scene_abc123",
    "label": 1
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Feedback logged successfully"
}
```

## Python Examples

### Upload and Process Video

```python
import requests

url = "http://localhost:8000/api/upload"
files = {"file": open("sample_video.mp4", "rb")}

response = requests.post(url, files=files)
data = response.json()

print(f"Processed {data['shots_processed']} shots")
print(f"Created {len(data['clusters'])} clusters")
```

### Get All Clusters

```python
import requests

response = requests.get("http://localhost:8000/api/clusters?view_type=scene")
data = response.json()

for cluster_id, cluster_data in data['clusters'].items():
    print(f"Cluster: {cluster_id}")
    print(f"  Shots: {len(cluster_data['shots'])}")
```

### Move Shot to Cluster

```python
import requests

url = "http://localhost:8000/api/move_to_cluster"
payload = {
    "shot_id": "video.mp4_3",
    "target_cluster_id": "scene_abc123"
}

response = requests.post(url, json=payload)
data = response.json()

if data['success']:
    print("Shot moved successfully!")
```

## JavaScript/TypeScript Examples

### Upload Video (Frontend)

```typescript
const uploadVideo = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch('http://localhost:8000/api/upload', {
    method: 'POST',
    body: formData,
  });

  const data = await response.json();
  console.log(`Processed ${data.shots_processed} shots`);
  return data;
};
```

### Fetch Clusters

```typescript
const fetchClusters = async (viewType: 'scene' | 'character' = 'scene') => {
  const response = await fetch(
    `http://localhost:8000/api/clusters?view_type=${viewType}`
  );
  const data = await response.json();
  return data.clusters;
};
```

### Move Shot to Cluster with Drag-and-Drop

```typescript
const moveShot = async (shotId: string, targetClusterId: string) => {
  const response = await fetch('http://localhost:8000/api/move_to_cluster', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      shot_id: shotId,
      target_cluster_id: targetClusterId,
    }),
  });

  const data = await response.json();
  return data;
};
```

## Rate Limiting

Currently, there are no rate limits on the API. However, for production use, consider:

- Implementing rate limiting middleware
- Adding authentication/authorization
- Setting upload size limits
- Implementing request queuing for heavy processing

## Error Handling

All endpoints return JSON responses with the following structure:

**Success:**
```json
{
  "success": true,
  "data": {...}
}
```

**Error:**
```json
{
  "detail": "Error message describing what went wrong"
}
```

HTTP Status Codes:
- `200` - Success
- `400` - Bad Request (e.g., invalid file)
- `500` - Internal Server Error

## Testing with Postman

1. Import the API into Postman
2. Create a new request collection
3. Set base URL to `http://localhost:8000`
4. Test each endpoint with sample data

## Next Steps

- Add authentication tokens
- Implement webhook notifications
- Add batch processing endpoints
- Create export endpoints (XML/EDL)
- Add search and filter capabilities
