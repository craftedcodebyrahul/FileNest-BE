 
import json
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

def delete_file_supabase(file_path: str, token: str):
    user = get_current_user(token)
    user_id = user.user_id

    # Sanitize path
    clean_path = file_path.strip("/").replace("..", "")
    full_path_to_delete = f"{user_id}/{clean_path}"

    delete_url = f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

    # Correct body
    payload = {
        "prefixes": [full_path_to_delete]
    }

    response = requests.delete(
        delete_url,
        json=payload,
        headers=headers
    )

    if response.status_code == 200:
        return {"message": "File deleted successfully"}
    else:
        raise Exception(f"Failed to delete file: {response.status_code} - {response.text}")
    
def rename_file_supabase(old_file_path: str, new_file_name: str, token: str):
    user = get_current_user(token)
    user_id = user.user_id

    # Sanitize paths to prevent traversal attacks
    clean_old_path = old_file_path.strip("/").replace("..", "")

    # Ensure the path is always under this user
    old_full_path = f"{user_id}/{clean_old_path}".strip("/")

    # Extract the directory part from the old path
    directory_path = os.path.dirname(old_full_path)

    # Construct the full new path with the new filename
    new_full_path = f"{directory_path}/{new_file_name}".strip("/")

    # ✅ Correct endpoint (no bucket in URL)
    url = f"{SUPABASE_URL}/storage/v1/object/move"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

    # ✅ Correct payload
    payload = {
        "bucketId": SUPABASE_BUCKET,
        "sourceKey": old_full_path,
        "destinationKey": new_full_path
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        return {
            "message": "File renamed successfully",
            "old_path": old_full_path,
            "new_path": new_full_path
        }
    else:
        raise Exception(f"Failed to rename file: {response.status_code} - {response.text}")
 
def rename_directory_supabase(old_dir_path: str, new_dir_name: str, token: str):
    user = get_current_user(token)
    user_id = user.user_id

    # Sanitize paths
    clean_old_dir = old_dir_path.strip("/").replace("..", "")

    # Add base path with user_id
    old_full_path = f"{user_id}/{clean_old_dir}".strip("/")

    # Extract parent path (under user_id) and build new path
    parent_path = os.path.dirname(old_full_path)
    new_dir_path = f"{parent_path}/{new_dir_name}".strip("/")

    # 1. List all objects inside the old directory
    list_url = f"{SUPABASE_URL}/storage/v1/object/list/{SUPABASE_BUCKET}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "prefix": old_full_path + "/",  # must end with slash for directory
        "limit": 100,  # todo: implement pagination for large dirs
        "offset": 0
    }

    list_response = requests.post(list_url, json=payload, headers=headers)
    if list_response.status_code != 200:
        raise Exception(f"Failed to list files for renaming: {list_response.text}")

    files_to_move = list_response.json()
    if not files_to_move:
        return {"message": "Directory is empty, nothing to rename."}

    # 2. Move each file to the new directory
    move_url = f"{SUPABASE_URL}/storage/v1/object/move"
    moved_files = []

    for file in files_to_move:
        # Skip directories (supabase sometimes returns placeholders)
        if 'id' not in file or file['id'] is None:
            continue

        old_file_path = f"{old_full_path}/{file['name']}".strip("/")
        new_file_path = f"{new_dir_path}/{file['name']}".strip("/")

        move_payload = {
           "bucketId": SUPABASE_BUCKET,
           "sourceKey": old_file_path,
           "destinationKey": new_file_path
        }

        move_response = requests.post(move_url, json=move_payload, headers=headers)

        if move_response.status_code == 200:
            moved_files.append({
                "old_path": old_file_path,
                "new_path": new_file_path
            })
        else:
            print(f"Failed to move {old_file_path}: {move_response.text}")

    if moved_files:
        return {
            "message": f"Successfully renamed directory '{clean_old_dir}' → '{new_dir_name}'",
            "moved_files": moved_files
        }
    else:
        raise Exception("Failed to move any files. Check logs for details.")
    
def get_signed_url_supabase(path: str, token: str):
   user = get_current_user(token)
   user_id = user.user_id
   
   # Sanitize the directory path
   clean_path = path.strip("/").replace("..", "")
   full_path_prefix = f"{user_id}/{clean_path}"  # always end with slash

   expires_in = 60 * 5  # 5 minutes

   url = f"{SUPABASE_URL}/storage/v1/object/sign/{SUPABASE_BUCKET}/{full_path_prefix}"
   headers = {
       "apikey": SUPABASE_KEY,
       "Authorization": f"Bearer {SUPABASE_KEY}"  # use service key here, not user JWT
   }
   payload = {"expiresIn": expires_in}

   response = requests.post(url, headers=headers, json=payload)

   if response.status_code == 200:
       return f"{SUPABASE_URL}/storage/v1/{response.json().get('signedURL')}"
   else:
       raise Exception(f"Failed to get signed URL: {response.text}")

def _auth_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
    }
def _safe_join_prefix(prefix: str) -> str:
    # Ensure a single trailing slash on non-empty prefixes
    prefix = prefix.strip("/")
    return f"{prefix}/" if prefix else ""
def delete_directory_supabase(dir_path: str, token: str):
    """
    Recursively deletes all objects under `user_id/dir_path/`.
    Walks subfolders and sends fully-qualified keys to /remove.
    """
    user = get_current_user(token)
    user_id = user.user_id

    clean_path = dir_path.strip("/").replace("..", "")
    base_prefix = _safe_join_prefix(f"{user_id}/{clean_path}")  # e.g. "123/abc/" or "123/"

    list_url = f"{SUPABASE_URL}/storage/v1/object/list/{SUPABASE_BUCKET}"
    remove_url = f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}"
    headers = _auth_headers()

    # BFS over folders
    to_visit = [base_prefix]         # queue of prefixes to list
    all_files = []                   # fully-qualified keys to delete
    limit = 1000

    while to_visit:
        current_prefix = to_visit.pop(0)  # FIFO

        offset = 0
        while True:
            payload = {
                "prefix": current_prefix,  # list within this prefix
                "limit": limit,
                "offset": offset,
                # optional: keep things deterministic
                "sortBy": {"column": "name", "order": "asc"},
            }

            resp = requests.post(list_url, json=payload, headers=headers)
            if resp.status_code != 200:
                raise Exception(f"Failed to list '{current_prefix}': {resp.status_code} - {resp.text}")

            batch = resp.json() or []

            # Supabase returns both files and folder entries.
            # Folders generally have `id: null`; files have a UUID `id` and metadata.
            for item in batch:
                name = item.get("name") or ""
                if not name:
                    continue

                full_key = f"{current_prefix}{name}"  # <-- CRUCIAL: prepend the current prefix

                is_folder = item.get("id") is None  # folders have no id
                if is_folder:
                    # Dive deeper: list this subfolder by appending '/'
                    to_visit.append(_safe_join_prefix(full_key))
                else:
                    # It's a file (including placeholder files like '.empty')
                    all_files.append(full_key)

            if len(batch) < limit:
                break
            offset += limit

    if not all_files:
        return {"message": f"Directory empty or not found: {base_prefix}"}

    # Delete in batches to be safe
    batch_size = 1000
    deleted = 0
    for i in range(0, len(all_files), batch_size):
        chunk = all_files[i:i + batch_size]
        resp = requests.delete(remove_url, json={"prefixes": chunk}, headers=headers)
        if resp.status_code != 200:
            raise Exception(f"Failed to delete batch {i//batch_size + 1}: {resp.status_code} - {resp.text}")
        deleted += len(chunk)

    return {"message": f"Deleted {deleted} objects under {base_prefix}"}