from supabase import create_client, Client
import os
from typing import Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../../.env'))

class StorageService:
    def __init__(self):
        supabase_url = os.getenv("VITE_SUPABASE_URL")
        supabase_key = os.getenv("VITE_SUPABASE_ANON_KEY")

        if not supabase_url or not supabase_key:
            print("Warning: Supabase credentials not found. Using local storage only.")
            self.supabase = None
        else:
            self.supabase: Client = create_client(supabase_url, supabase_key)
            print(f"✓ Connected to Supabase: {supabase_url}")

    async def save_shot(self, shot_data: Dict) -> Dict:
        if not self.supabase:
            return {"success": False, "message": "Supabase not configured"}

        try:
            result = self.supabase.table("shots").insert(shot_data).execute()
            return {"success": True, "data": result.data}
        except Exception as e:
            print(f"Error saving shot to Supabase: {e}")
            return {"success": False, "error": str(e)}

    async def save_feedback(self, feedback_data: Dict) -> Dict:
        if not self.supabase:
            return {"success": False, "message": "Supabase not configured"}

        try:
            result = self.supabase.table("training_feedback").insert(feedback_data).execute()
            return {"success": True, "data": result.data}
        except Exception as e:
            print(f"Error saving feedback to Supabase: {e}")
            return {"success": False, "error": str(e)}

    async def get_all_shots(self) -> List[Dict]:
        if not self.supabase:
            return []

        try:
            result = self.supabase.table("shots").select("*").execute()
            return result.data
        except Exception as e:
            print(f"Error fetching shots from Supabase: {e}")
            return []

    async def get_feedback_history(self) -> List[Dict]:
        if not self.supabase:
            return []

        try:
            result = self.supabase.table("training_feedback").select("*").execute()
            return result.data
        except Exception as e:
            print(f"Error fetching feedback from Supabase: {e}")
            return []
