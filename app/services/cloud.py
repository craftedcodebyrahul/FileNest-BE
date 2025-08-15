 
from fastapi import UploadFile
import requests
import os

from app.dependencies import get_current_user

from ..config import get_settings 
import uuid
import mimetypes
  
settings = get_settings()
SUPABASE_URL = settings.SUPABASE_URL
SUPABASE_KEY = settings.SUPABASE_KEY
SUPABASE_BUCKET = settings.SUPABASE_BUCKET



 

def upload_to_supabase(file: UploadFile, content: bytes, user_path: str, token: str):
   
    user = get_current_user(token)
    user_id = user.user_id
 
   
    clean_path = user_path.strip("/").replace("..", "")  
    full_path = f"{user_id}/{clean_path}/{file.filename}"

    
    content_type, _ = mimetypes.guess_type(file.filename)
    content_type = content_type or "application/octet-stream"

    url = f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/{full_path}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": content_type,
        "x-upsert": "false"
    }

    response = requests.put(url, data=content, headers=headers)

    if response.status_code in (200, 201):
        public_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{full_path}"
        return {
            "message": "Upload successful",
            "url": public_url,
            "filename": file.filename,
            "path": clean_path,
            "content_type": content_type
        }
    else:
        raise Exception(f"Upload failed: {response.status_code} - {response.text}")
    
 

def list_user_files(user_path: str, token: str):
    user = get_current_user(token)
    user_id = user.user_id

    clean_path = user_path.strip("/").replace("..", "")
    full_path = f"{user_id}/{clean_path}"

    url = f"{SUPABASE_URL}/storage/v1/object/list/{SUPABASE_BUCKET}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    payload = {
        "prefix": full_path,
        "limit": 100,
        "offset": 0,
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Failed to list files: {response.text}")

    files = response.json()
    
 
    if not files or not isinstance(files, list):
        return []

    filesList = []
    directories=[]
    for file in files:
        if(not file["id"]):
            directories.append(file["name"])
            continue
    
        filesList.append({
            "name": file["name"],
            "fullPath": f"{full_path}/{file['name']}",
            "url": f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{full_path}/{file['name']}",
            "size": file.get("metadata", {}).get("size"),
            "mimetype": file.get("metadata", {}).get("mimetype"),
            "updatedAt": file.get("updated_at")
        })

    return {"files": filesList, "directories": directories}

def create_directory_supabase(user_path: str,dir_name: str, token: str):
    user = get_current_user(token)
    user_id = user.user_id
    clean_path = user_path.strip("/").replace("..", "")
    full_path = f"{user_id}/{clean_path}/{dir_name}/.empty"

    url = f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/{full_path}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/octet-stream"
    }
    response = requests.put(url, data=b'', headers=headers)

    if response.status_code in (200, 201):
        return {"message": "Directory created successfully", "path": full_path}
    else:
        raise Exception(f"Failed to create directory: {response.text}")
