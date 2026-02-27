# System Architecture

## Overview
This document explains the technical architecture of the Film Asset Management & Active Learning System.

## System Components

### 1. Backend Architecture (Python/FastAPI)

#### Keyframe Extractor (`services/keyframe_extractor.py`)
**Purpose**: Intelligently extract representative frames from video shots

**Algorithm**:
1. Load video using OpenCV
2. Calculate frame-to-frame variance using pixel difference
3. Compute average variance across entire shot
4. Decision logic:
   - If variance < threshold: STATIC shot → Extract 1 median keyframe
   - If variance ≥ threshold: DYNAMIC shot → Extract 3 keyframes (start, middle, end)

**Why this approach?**
- Static shots (locked camera): One frame is sufficient
- Dynamic shots (camera movement/action): Multiple frames capture spatial coverage
- Prevents redundant processing while ensuring complete scene representation

#### Embedding Engine (`services/embedding_engine.py`)
**Purpose**: Generate vector representations for scene and character matching

**Components**:
1. **Scene Embeddings** (CLIP ViT-B/32):
   - Converts entire image to 512-dimensional vector
   - Captures spatial layout, lighting, location characteristics
   - Model: `sentence-transformers/clip-ViT-B-32`
   - Future upgrade path: DINOv2 for better scene understanding

2. **Character Embeddings** (MTCNN + CLIP):
   - Detects faces using MTCNN
   - Extracts bounding boxes for each face
   - Generates embeddings for each detected face
   - Future upgrade path: InsightFace (ArcFace) for better face recognition

**Design Pattern**:
- Dual-embedding architecture separates "where" (scene) from "who" (character)
- Enables hierarchical clustering: macro (location) → micro (people)

#### Clustering Engine (`services/clustering_engine.py`)
**Purpose**: Real-time hierarchical clustering using vector similarity

**Technology**: ChromaDB with HNSW (Hierarchical Navigable Small World) indexing

**Algorithm**:
1. **Scene-Level Clustering** (Macro):
   - Query new scene_vector against existing clusters
   - If cosine similarity ≥ 0.85: Assign to existing cluster
   - If similarity < 0.5: Route to noise bucket
   - Otherwise: Create new cluster

2. **Character-Level Clustering** (Micro):
   - Within each scene cluster, sub-cluster by detected faces
   - Enables grouping like "Kitchen with Character A" vs "Kitchen with Character B"

3. **Noise Bucket**:
   - Catches ambiguous shots that don't clearly belong anywhere
   - Human can later drag these to correct clusters
   - Logged as training data for model improvement

**Thresholds**:
- `scene_threshold = 0.85`: High confidence for scene matching
- `character_threshold = 0.75`: Moderate confidence for face matching
- `noise_threshold = 0.5`: Below this = uncertain

#### Storage Service (`services/storage_service.py`)
**Purpose**: Persist data to Supabase for long-term storage and analytics

**Operations**:
- Save shot metadata (paths, clusters, scores)
- Log human feedback events
- Enable querying for training data export

### 2. Frontend Architecture (React/TypeScript)

#### Component Hierarchy

```
App (DndContext)
├── Sidebar
│   ├── Upload button
│   ├── View mode toggle (Scene/Character)
│   └── Refresh button
├── MainGallery
│   └── ClusterFolder (Droppable)
│       └── Shot thumbnails
├── NoiseBucket
│   └── DraggableShot (Draggable)
└── DragOverlay
```

#### Drag-and-Drop Flow

1. User drags shot from NoiseBucket
2. `handleDragStart`: Store dragged shot in state
3. User drops onto cluster folder
4. `handleDragEnd`:
   - Call API `/api/move_to_cluster`
   - Log feedback `/api/log_feedback`
   - Refresh data

#### State Management
- Local component state for UI interactions
- API calls via axios for backend communication
- No global state management needed (simple application)

### 3. Data Flow

```
Video Upload
    ↓
Keyframe Extraction (OpenCV)
    ↓
Embedding Generation (CLIP + MTCNN)
    ↓
Clustering (ChromaDB)
    ↓
Display in UI
    ↓
Human Correction (Drag-and-Drop)
    ↓
Log Feedback (JSONL + Supabase)
    ↓
Future: Metric Learning Training
```

### 4. Database Schema

#### `shots` table
```sql
- id: UUID (primary key)
- shot_id: Text (identifier)
- keyframe_path: Text (file path)
- frame_index: Integer
- cluster_type: Text (scene/character/noise)
- cluster_id: Text
- similarity_score: Float
- timestamp: Timestamptz
```

#### `training_feedback` table
```sql
- id: UUID (primary key)
- anchor_id: Text (shot being moved)
- positive_id: Text (target cluster)
- label: Integer (1 = positive association)
- timestamp: Timestamptz
```

## Active Learning Pipeline

### Current Implementation
1. System makes initial clustering decisions
2. Uncertain shots go to noise bucket
3. Human corrects by dragging to correct cluster
4. Feedback logged as (anchor, positive) pairs

### Future Training Loop
1. Collect feedback data from `training_feedback` table
2. For each feedback event, create triplet:
   - Anchor: Moved shot embedding
   - Positive: Centroid of target cluster
   - Negative: Sample from other clusters
3. Train neural network adapter using Triplet Loss
4. Fine-tune last layers of embedding models
5. Deploy improved model

## Scalability Considerations

### Current Limitations
- In-memory ChromaDB (resets on restart)
- Local file storage for keyframes
- Single-threaded processing

### Production Upgrades
1. Persistent ChromaDB with remote backend
2. Cloud storage (S3/Supabase Storage) for keyframes
3. Task queue (Celery) for async video processing
4. GPU acceleration for embedding generation
5. Model versioning and A/B testing

## Security

### Data Protection
- RLS policies on Supabase tables
- Public access for demo (should restrict in production)
- No authentication (add in production)

### File Handling
- Videos stored locally in `uploads/`
- Keyframes stored in `keyframes/`
- Should validate file types and size limits

## Performance Optimizations

### Backend
- ChromaDB HNSW indexing for fast similarity search
- Batch embedding generation (future)
- Video processing in background tasks (future)

### Frontend
- Lazy loading of images
- Virtual scrolling for large clusters (future)
- Debounced search/filter (future)

## Monitoring & Observability

### Current
- Console logging in backend
- Error boundaries in frontend (TODO)

### Production Requirements
- Structured logging (JSON)
- Performance metrics (embedding time, clustering time)
- Error tracking (Sentry)
- User analytics (feedback patterns)

## Testing Strategy

### Unit Tests
- Keyframe extraction logic
- Embedding generation
- Clustering algorithm

### Integration Tests
- API endpoints
- Database operations
- File uploads

### E2E Tests
- Complete video upload flow
- Drag-and-drop functionality
- Feedback logging

## Deployment

### Development
1. Backend: `cd backend && ./start.sh`
2. Frontend: `npm run dev`

### Production
1. Backend: Docker container with FastAPI + Uvicorn
2. Frontend: Static build served via CDN
3. Database: Supabase hosted
4. Storage: Supabase Storage or S3
5. Vector DB: ChromaDB cloud or Pinecone

## Future Enhancements

1. **Better Models**
   - DINOv2 for scene embeddings
   - InsightFace for face recognition

2. **Advanced Clustering**
   - Temporal clustering (group by time)
   - Multi-modal clustering (audio + visual)

3. **Export Features**
   - XML/EDL for NLE software
   - Batch operations

4. **Search & Discovery**
   - Text search with CLIP
   - Visual similarity search
   - Filter by metadata

5. **Collaboration**
   - Multi-user support
   - Comments and annotations
   - Approval workflows
