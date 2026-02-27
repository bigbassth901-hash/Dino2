# Testing Guide

Complete guide for testing the Film Asset Management system.

## Prerequisites

Before testing, ensure:
1. Backend is running on `http://localhost:8000`
2. Frontend is running on `http://localhost:5173`
3. Database tables are created in Supabase
4. All dependencies are installed

## Quick Test Checklist

- [ ] Backend starts without errors
- [ ] Frontend builds successfully
- [ ] Database connection works
- [ ] Can access frontend in browser
- [ ] Can upload a video file
- [ ] Keyframes are extracted
- [ ] Clusters are created
- [ ] Noise bucket shows unclassified shots
- [ ] Can drag shots to clusters
- [ ] Feedback is logged to database

## Test Videos

For testing, use short video clips with:
- **Static scenes**: Videos with little camera movement (good for single keyframe extraction)
- **Dynamic scenes**: Videos with camera pans or action (tests multiple keyframe extraction)
- **Faces**: Videos with people for character detection testing
- **Different locations**: Multiple scene changes for clustering testing

### Recommended Test Videos

1. **Short clip (5-10 seconds)** - Quick functionality test
2. **Scene variety** - Video with 2-3 different locations
3. **People talking** - Tests face detection
4. **Mixed content** - Combination of indoor/outdoor scenes

You can create test videos using:
```bash
# Create a 10-second test video from your webcam (requires ffmpeg)
ffmpeg -f avfoundation -i "0" -t 10 test_video.mp4

# Or download free stock footage from:
# - Pexels.com
# - Pixabay.com
# - Coverr.co
```

## Unit Tests

### Backend Component Tests

#### 1. Test Environment Setup
```bash
cd backend
source venv/bin/activate
python3 test_api.py
```

Expected output:
```
✓ FastAPI imported successfully
✓ python-dotenv imported successfully
✓ OpenCV imported successfully
✓ Supabase client imported successfully
✓ sentence-transformers imported successfully
✓ ChromaDB imported successfully
✓ MTCNN imported successfully
✓ VITE_SUPABASE_URL: https://...
✓ VITE_SUPABASE_ANON_KEY: eyJ...
✓ Successfully connected to Supabase
```

#### 2. Test Keyframe Extraction
```python
# Create file: backend/test_keyframe.py
from services.keyframe_extractor import KeyframeExtractor
import os

extractor = KeyframeExtractor()

# Test with a sample video
if os.path.exists("test_video.mp4"):
    keyframes = extractor.extract_keyframes("test_video.mp4")
    print(f"✓ Extracted {len(keyframes)} keyframes")
    for kf in keyframes:
        print(f"  - {kf['path']} (frame {kf['frame_index']})")
else:
    print("✗ test_video.mp4 not found")
```

#### 3. Test Embedding Generation
```python
# Create file: backend/test_embeddings.py
from services.embedding_engine import EmbeddingEngine
from PIL import Image
import numpy as np

engine = EmbeddingEngine()

# Create a test image
test_img = Image.new('RGB', (640, 480), color='red')
test_img.save("test_image.jpg")

# Test scene embedding
scene_vector = engine.generate_scene_embedding("test_image.jpg")
print(f"✓ Scene embedding: {len(scene_vector)} dimensions")

# Test character embedding
char_vectors = engine.generate_character_embeddings("test_image.jpg")
print(f"✓ Character embeddings: {len(char_vectors)} faces detected")
```

#### 4. Test Clustering
```python
# Create file: backend/test_clustering.py
import asyncio
from services.clustering_engine import ClusteringEngine

async def test_clustering():
    engine = ClusteringEngine()

    # Create dummy vectors
    scene_vector = [0.1] * 512
    char_vectors = [[0.2] * 512]

    result = engine.assign_to_cluster(
        scene_vector=scene_vector,
        character_vectors=char_vectors,
        keyframe_path="test_image.jpg"
    )

    print(f"✓ Cluster assignment: {result['cluster_id']}")
    print(f"  Type: {result['cluster_type']}")
    print(f"  Score: {result['similarity_score']}")

asyncio.run(test_clustering())
```

### Frontend Tests

#### 1. Build Test
```bash
npm run build
```

Expected: Build completes without errors

#### 2. Type Check
```bash
npm run typecheck
```

Expected: No TypeScript errors

#### 3. Lint Check
```bash
npm run lint
```

Expected: No linting errors

## Integration Tests

### Test 1: Complete Upload Flow

1. Start backend and frontend
2. Open `http://localhost:5173` in browser
3. Open DevTools (F12) to monitor console and network
4. Click "Upload Video" button
5. Select a test video file
6. Wait for processing to complete

**Expected Results:**
- Upload progress indicator shows
- Backend processes video (check terminal logs)
- Keyframes appear in clusters
- Some shots may appear in Noise Bucket
- No console errors

### Test 2: Clustering Accuracy

1. Upload a video with 2-3 distinct scenes
2. Review the created clusters
3. Check if similar scenes are grouped together

**Expected Results:**
- Similar scenes (same location/lighting) should cluster together
- Different scenes should be in separate clusters
- Cluster similarity scores should be high (>0.85) for matches

### Test 3: Active Learning Flow

1. Look at the Noise Bucket (right sidebar)
2. Drag a shot from Noise Bucket to a cluster folder
3. Check browser console for API call
4. Verify feedback is logged

**Expected Results:**
- Drag-and-drop works smoothly
- API call succeeds (check Network tab)
- Shot moves from Noise Bucket to cluster
- Database receives feedback entry

### Test 4: View Mode Toggle

1. Click "Scene Clusters" view (default)
2. Note the clusters shown
3. Click "Character Clusters" view
4. Compare the results

**Expected Results:**
- View toggles smoothly
- Different clustering in character mode
- Videos with faces show character-based grouping

### Test 5: Database Persistence

1. Upload and process a video
2. Note the clusters created
3. Restart the backend server
4. Refresh the frontend

**Expected Results:**
- Clusters are preserved in ChromaDB
- Data is saved to Supabase
- UI shows previous clusters

## Load Testing

### Test with Multiple Videos

```bash
# Upload multiple videos via API
for video in video1.mp4 video2.mp4 video3.mp4; do
  curl -X POST http://localhost:8000/api/upload \
    -F "file=@$video"
done
```

**Monitor:**
- Server response time
- Memory usage
- Database performance

## Performance Benchmarks

Typical performance on modern hardware:

| Task | Duration | Notes |
|------|----------|-------|
| Video upload (10s clip) | 1-2s | Network dependent |
| Keyframe extraction | 2-5s | Video length dependent |
| Scene embedding | 3-10s | First run downloads models |
| Face detection | 5-15s | Depends on face count |
| Clustering | <1s | Fast with ChromaDB |
| Total processing | 10-30s | For 10-second video |

## Troubleshooting Test Failures

### Backend won't start
- Check Python version: `python3 --version`
- Verify dependencies: `pip list`
- Check logs for import errors

### Keyframes not extracted
- Verify video file is valid
- Check `backend/keyframes/` directory exists
- Look for OpenCV errors in logs

### No faces detected
- Faces must be clear and frontal
- MTCNN may fail on profile shots
- Try videos with larger, clearer faces

### Clustering produces too many groups
- Normal for diverse content
- Adjust similarity thresholds in code
- Try videos with more repetitive content

### Database errors
- Check Supabase connection
- Verify tables exist
- Check RLS policies

## Continuous Testing

Set up automated tests:

```bash
# Add to package.json scripts:
"scripts": {
  "test": "npm run typecheck && npm run build",
  "test:backend": "cd backend && python3 test_api.py"
}
```

Run tests before commits:
```bash
npm run test
npm run test:backend
```

## Test Data Management

Clean up test data:
```bash
# Remove uploaded videos
rm backend/uploads/*

# Remove keyframes
rm backend/keyframes/*

# Remove training data
rm backend/training_data/training_pairs.jsonl

# Reset ChromaDB (will lose all clusters)
rm -rf backend/chroma_db/
```

## Next Steps for Testing

1. Add pytest for Python unit tests
2. Add Jest for React component tests
3. Set up CI/CD pipeline
4. Add E2E tests with Playwright
5. Implement load testing with Locust
