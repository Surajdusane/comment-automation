from dotenv import load_dotenv
load_dotenv()
import os
from supabase import create_client
import json

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

# data = supabase.table("session_id").select("*").eq("id", "1").execute()
# json = json.dumps(data.data)
# print(json)