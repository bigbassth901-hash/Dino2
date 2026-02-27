# Quick Start Guide

Get the Film Asset Management system running in 5 minutes!

## Prerequisites Check

Before starting, ensure you have:
- ✓ Python 3.10 or higher
- ✓ Node.js 18 or higher
- ✓ 5GB free disk space
- ✓ Internet connection (for downloading ML models)

Quick check:
```bash
python3 --version  # Should show 3.10+
node --version     # Should show 18+
npm --version      # Should be installed
```

## Step 1: Frontend Setup (30 seconds)

Open a terminal and run:

```bash
# Install dependencies
npm install

# Build to check for errors
npm run build
```

Expected output:
```
✓ built in 7.88s
```

## Step 2: Backend Setup (2-3 minutes)

Open a **new terminal** and run:

```bash
cd backend
chmod +x start_server.sh
./start_server.sh
```

This will:
1. Create Python virtual environment
2. Install all dependencies (this takes the longest)
3. Run system tests
4. Start the server

Expected final output:
```
========================================
Starting FastAPI server on port 8000...
========================================

INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Step 3: Start Frontend (30 seconds)

Return to your first terminal and run:

```bash
npm run dev
```

Expected output:
```
  VITE v5.4.8  ready in 1234 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

## Step 4: Open in Browser

1. Open your browser
2. Go to: `http://localhost:5173`
3. You should see the Film Asset Manager interface

## Step 5: Test Upload (1 minute)

1. Click "Upload Video" button
2. Select a short video file (5-10 seconds recommended for first test)
3. Wait for processing (10-30 seconds)
4. See results:
   - Keyframes extracted
   - Clusters created
   - Some shots may appear in "Noise Bucket"

## Troubleshooting

### Backend won't start

**Error:** "python: command not found"
```bash
# Use python3 instead
python3 --version
```

**Error:** "No module named 'fastapi'"
```bash
# Make sure you're in the virtual environment
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend won't start

**Error:** "Port 5173 already in use"
```bash
# Kill the process
lsof -ti:5173 | xargs kill -9
# Then try again
npm run dev
```

### Can't upload video

**Issue:** Upload button doesn't work
- Check that backend is running on port 8000
- Open browser DevTools (F12) and check Console for errors
- Make sure video file is in a supported format (MP4, MOV, AVI)

## What's Happening Behind the Scenes?

When you upload a video, the system:

1. **Extracts Keyframes** (2-5s)
   - Analyzes video motion
   - Static shots: 1 keyframe
   - Dynamic shots: 3 keyframes

2. **Generates Embeddings** (3-10s)
   - Scene embeddings with CLIP
   - Face detection with MTCNN
   - Creates 512-dimensional vectors

3. **Clusters Shots** (<1s)
   - Groups similar scenes together
   - Uses ChromaDB vector search
   - Uncertain shots go to Noise Bucket

4. **Saves to Database**
   - Stores in Supabase
   - Ready for active learning

## Next Steps

Now that it's working, try:

1. **Upload more videos** - See how clustering improves
2. **Drag and drop** - Move shots from Noise Bucket to clusters
3. **Toggle views** - Switch between Scene and Character views
4. **Check the data** - Open Supabase dashboard to see stored data

## Understanding the UI

```
┌─────────────────────────────────────────────────────┐
│  Sidebar         Main Gallery          Noise Bucket │
│  ┌────────┐     ┌──────────────┐      ┌──────────┐ │
│  │Upload  │     │ Cluster 1    │      │ Shot 1   │ │
│  │        │     │  📁 5 shots  │      │ Shot 2   │ │
│  │Scene   │     ├──────────────┤      │ Shot 3   │ │
│  │Char    │     │ Cluster 2    │      └──────────┘ │
│  │        │     │  📁 3 shots  │      Drag shots   │
│  │Refresh │     └──────────────┘      to clusters  │
│  └────────┘                                         │
└─────────────────────────────────────────────────────┘
```

## File Locations

While running, files are stored in:
```
backend/
├── uploads/         # Original uploaded videos
├── keyframes/       # Extracted keyframe images
├── training_data/   # Human feedback logs
└── chroma_db/       # Vector database
```

## Stopping the System

When done:

1. Frontend: Press `Ctrl+C` in the frontend terminal
2. Backend: Press `Ctrl+C` in the backend terminal

Data is saved in Supabase and ChromaDB, so you can restart later.

## System Requirements

**Minimum:**
- CPU: 2 cores
- RAM: 4GB
- Disk: 5GB free

**Recommended:**
- CPU: 4+ cores
- RAM: 8GB+
- Disk: 10GB+ free
- GPU: Optional but speeds up processing

## Performance Tips

**First video upload is slow** because:
- ML models are downloaded (~500MB)
- Models are loaded into memory
- Subsequent uploads are much faster

**Speed up processing:**
- Use shorter videos for testing
- Use videos with clear faces
- Ensure good internet connection (first run)
- Add more RAM if available

## Complete Feature List

Current features:
- ✓ Video upload and processing
- ✓ Dynamic keyframe extraction
- ✓ Scene clustering
- ✓ Character detection
- ✓ Active learning (drag-and-drop)
- ✓ Feedback logging
- ✓ Database persistence
- ✓ Real-time updates

## Getting Help

If you're stuck:
1. Check `TROUBLESHOOTING.md` for common issues
2. Review `API_EXAMPLES.md` for API usage
3. Read `TESTING.md` for validation steps
4. See `DEPLOYMENT.md` for production setup

## Success Checklist

You're all set if:
- ✓ Frontend loads at http://localhost:5173
- ✓ Backend responds at http://localhost:8000
- ✓ You can upload a video
- ✓ Keyframes are extracted
- ✓ Clusters are created
- ✓ You can drag shots to clusters

Congratulations! Your AI-powered film asset management system is running!
