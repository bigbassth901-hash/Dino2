# Film Asset Management & Active Learning System

An enterprise-grade AI-powered film asset management system that intelligently organizes video shots using advanced computer vision and hierarchical clustering with human-in-the-loop active learning.

## Architecture Overview

### Backend (Python FastAPI)
- Dynamic keyframe extraction using OpenCV
- Dual-embedding engine (Scene + Character detection)
- Real-time hierarchical clustering with ChromaDB
- Active learning pipeline with human feedback
- Supabase integration for data persistence

### Frontend (React + Vite)
- Cinematic dark UI with professional NLE aesthetic
- Drag-and-drop interface for human-in-the-loop learning
- Real-time cluster visualization
- Scene and character view modes

## Key Features

### 1. Dynamic Keyframe Extraction
- Analyzes video motion using frame-to-frame variance
- Static shots: Extracts 1 median keyframe
- Dynamic shots: Extracts 3 keyframes (start, peak, end)

### 2. Dual-Embedding Engine
- Scene embeddings: CLIP-based spatial/location analysis
- Character embeddings: Face detection and embedding with MTCNN

### 3. Hierarchical Clustering
- Macro-level: Scene-based clustering
- Micro-level: Character-based sub-clustering
- Automatic noise bucket for low-confidence shots
- ChromaDB with HNSW indexing for fast similarity search

### 4. Active Learning
- Drag-and-drop shots from noise bucket to clusters
- Automatic logging of training pairs to JSONL
- Prepares data for future metric learning (Triplet Loss)

## Installation & Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm or yarn

### Quick Start

**Option 1: Use the automated start script (Recommended)**

1. Navigate to backend directory and run:
```bash
cd backend
chmod +x start_server.sh
./start_server.sh
```

This will automatically:
- Create a virtual environment
- Install all Python dependencies
- Run system tests
- Start the FastAPI server on `http://localhost:8000`

**Option 2: Manual setup**

1. Backend setup:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 test_api.py  # Run tests
python3 main.py      # Start server
```

2. Frontend setup (in a new terminal):
```bash
npm install
npm run dev
```

The frontend will start on `http://localhost:5173`

### Environment Variables

Make sure you have a `.env` file in the project root with:
```
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

## Usage

1. Upload a video file using the sidebar
2. The system will automatically:
   - Extract keyframes based on motion analysis
   - Generate scene and character embeddings
   - Cluster shots hierarchically
   - Identify noise/unclassified shots

3. Review clusters in the main gallery
4. Drag shots from the Noise Bucket to appropriate clusters
5. The system logs your feedback for future model fine-tuning

## Technology Stack

### Backend
- FastAPI: Modern Python web framework
- OpenCV: Video processing and keyframe extraction
- CLIP (via sentence-transformers): Scene embeddings
- MTCNN: Face detection
- ChromaDB: Vector database with HNSW indexing
- Supabase: Data persistence

### Frontend
- React 18: UI framework
- Vite: Build tool
- TypeScript: Type safety
- TailwindCSS: Styling
- @dnd-kit: Drag-and-drop functionality
- Axios: API communication
- Lucide React: Icons

## API Endpoints

- `POST /api/upload` - Upload and process video
- `GET /api/clusters?view_type=scene|character` - Get all clusters
- `GET /api/noise_bucket` - Get unclassified shots
- `POST /api/move_to_cluster` - Move shot to cluster
- `POST /api/log_feedback` - Log human feedback

## Database Schema

### Shots Table
- Stores all processed video shots
- Tracks clustering assignments
- Records similarity scores

### Training Feedback Table
- Logs human corrections
- Stores anchor-positive pairs
- Prepares data for metric learning

## Future Enhancements

1. Replace CLIP with DINOv2 for better scene understanding
2. Replace MTCNN with InsightFace for improved face recognition
3. Implement Triplet Loss training on collected feedback
4. Add batch video processing
5. Export clusters to editing software (XML/EDL)
6. Add search and filter functionality
7. Implement user authentication and multi-project support

## Training Data

All human feedback is saved to:
- Local: `backend/training_data/training_pairs.jsonl`
- Database: `training_feedback` table in Supabase

This data can be used to fine-tune the embedding models using contrastive learning techniques.

## License

MIT License
