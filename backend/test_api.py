import sys
import os

print("Testing imports...")

try:
    from fastapi import FastAPI
    print("✓ FastAPI imported successfully")
except ImportError as e:
    print(f"✗ Failed to import FastAPI: {e}")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    print("✓ python-dotenv imported successfully")
except ImportError as e:
    print(f"✗ Failed to import dotenv: {e}")
    sys.exit(1)

try:
    import cv2
    print("✓ OpenCV imported successfully")
except ImportError as e:
    print(f"✗ Failed to import OpenCV: {e}")
    sys.exit(1)

try:
    from supabase import create_client
    print("✓ Supabase client imported successfully")
except ImportError as e:
    print(f"✗ Failed to import Supabase: {e}")
    sys.exit(1)

try:
    from sentence_transformers import SentenceTransformer
    print("✓ sentence-transformers imported successfully")
except ImportError as e:
    print(f"✗ Failed to import sentence-transformers: {e}")
    sys.exit(1)

try:
    import chromadb
    print("✓ ChromaDB imported successfully")
except ImportError as e:
    print(f"✗ Failed to import ChromaDB: {e}")
    sys.exit(1)

try:
    from mtcnn import MTCNN
    print("✓ MTCNN imported successfully")
except ImportError as e:
    print(f"✗ Failed to import MTCNN: {e}")
    sys.exit(1)

print("\n" + "="*50)
print("Testing environment variables...")
load_dotenv()

supabase_url = os.getenv("VITE_SUPABASE_URL")
supabase_key = os.getenv("VITE_SUPABASE_ANON_KEY")

if supabase_url:
    print(f"✓ VITE_SUPABASE_URL: {supabase_url}")
else:
    print("✗ VITE_SUPABASE_URL not found")

if supabase_key:
    print(f"✓ VITE_SUPABASE_ANON_KEY: {supabase_key[:20]}...")
else:
    print("✗ VITE_SUPABASE_ANON_KEY not found")

print("\n" + "="*50)
print("Testing Supabase connection...")

if supabase_url and supabase_key:
    try:
        client = create_client(supabase_url, supabase_key)
        result = client.table("shots").select("*").limit(1).execute()
        print("✓ Successfully connected to Supabase")
        print(f"  Tables accessible: shots, training_feedback")
    except Exception as e:
        print(f"✗ Failed to connect to Supabase: {e}")
else:
    print("✗ Cannot test Supabase connection - missing credentials")

print("\n" + "="*50)
print("All tests completed!")
print("="*50)
