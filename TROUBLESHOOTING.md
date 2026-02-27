# Troubleshooting Guide

## Common Issues and Solutions

### Backend Issues

#### 1. Python Not Found
**Error:** `python: command not found`

**Solution:**
```bash
# Use python3 instead
python3 --version

# If python3 is not found, install Python:
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv

# macOS
brew install python3
```

#### 2. OpenCV Import Error
**Error:** `ImportError: libGL.so.1: cannot open shared object file`

**Solution:**
```bash
# Ubuntu/Debian
sudo apt-get install libgl1-mesa-glx libglib2.0-0

# For headless servers, use opencv-python-headless
pip uninstall opencv-python
pip install opencv-python-headless
```

#### 3. TensorFlow Installation Issues
**Error:** TensorFlow fails to install or import

**Solution:**
```bash
# For ARM-based Macs (M1/M2)
pip install tensorflow-macos

# For older Python versions, use compatible TensorFlow
pip install tensorflow==2.13.0

# If face detection fails, MTCNN can work without GPU
```

#### 4. ChromaDB Persistence Issues
**Error:** ChromaDB data lost after restart

**Solution:**
- ChromaDB is configured to persist in `./chroma_db` directory
- Make sure the directory has write permissions
- Check if the directory exists: `ls -la backend/chroma_db`

#### 5. Supabase Connection Error
**Error:** `Warning: Supabase credentials not found`

**Solution:**
```bash
# Make sure .env file exists in project root
ls -la .env

# Check .env contents
cat .env

# Verify environment variables
cd backend
python3 -c "from dotenv import load_dotenv; import os; load_dotenv('../.env'); print(os.getenv('VITE_SUPABASE_URL'))"
```

### Frontend Issues

#### 1. Port Already in Use
**Error:** `Port 5173 is already in use`

**Solution:**
```bash
# Kill the process using port 5173
lsof -ti:5173 | xargs kill -9

# Or specify a different port
npm run dev -- --port 3000
```

#### 2. CORS Errors
**Error:** `Access to fetch has been blocked by CORS policy`

**Solution:**
- Make sure backend is running on `http://localhost:8000`
- Check that CORS is enabled in `backend/main.py` (it should be)
- Verify frontend is making requests to the correct URL

#### 3. Images Not Loading
**Error:** Images show broken icon

**Solution:**
- Make sure backend is serving static files (check `main.py` for StaticFiles mount)
- Verify image paths are correct
- Check browser console for 404 errors
- Ensure keyframes directory exists: `ls -la backend/keyframes`

### Database Issues

#### 1. Table Does Not Exist
**Error:** `relation "shots" does not exist`

**Solution:**
- Check if migration has been applied
- Verify tables exist in Supabase dashboard
- Re-run migration if needed

#### 2. RLS Policy Blocking Access
**Error:** `new row violates row-level security policy`

**Solution:**
- Check RLS policies in Supabase dashboard
- Verify policies allow public access (for demo)
- Disable RLS temporarily for testing (not recommended for production)

### Performance Issues

#### 1. Video Processing is Slow
**Problem:** Video upload takes too long

**Solution:**
- First upload will download ML models (CLIP, MTCNN)
- Subsequent uploads will be faster
- Consider using smaller video files for testing
- GPU acceleration will improve performance significantly

#### 2. Face Detection Not Working
**Problem:** No faces detected in video

**Solution:**
- MTCNN requires clear, frontal faces
- Low resolution or blurry faces may not be detected
- Check if faces are large enough in frame
- Consider adjusting MTCNN detection threshold

## Testing the System

### Backend Test
```bash
cd backend
source venv/bin/activate
python3 test_api.py
```

### Frontend Test
```bash
npm run build
```

### Full System Test
1. Start backend: `cd backend && ./start_server.sh`
2. Start frontend (new terminal): `npm run dev`
3. Open browser: `http://localhost:5173`
4. Try uploading a short video file

## Logs and Debugging

### Backend Logs
- FastAPI logs appear in the terminal where you ran `python3 main.py`
- Check for Python errors and stack traces
- Enable debug mode by setting `debug=True` in uvicorn.run()

### Frontend Logs
- Open browser DevTools (F12)
- Check Console tab for JavaScript errors
- Check Network tab for API call failures

### Database Logs
- Check Supabase dashboard for query logs
- Monitor table row counts
- Verify data is being inserted correctly

## Getting Help

If you encounter issues not covered here:
1. Check the error message carefully
2. Search for the error in the project's issue tracker
3. Verify all prerequisites are installed
4. Try running the test scripts
5. Check if backend and frontend are on the same network (for remote deployments)
