from fastapi import APIRouter, Depends, Form, Query, UploadFile, File
import shutil
import os

from ..services.cloud import create_directory_supabase, list_user_files, upload_to_supabase
from ..dependencies import oauth2_scheme
 

router = APIRouter()

@router.post("/upload")
async def upload_file( file: UploadFile = File(...),
    path: str = Form(...), 
    token: str = Depends(oauth2_scheme)):
    try:
        content = await file.read()
        result = upload_to_supabase(file, content,path,token)
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/files")
async def get_user_files(
    path: str = Query(..., description="Path inside your storage directory"),
    token: str = Depends(oauth2_scheme)
):
    try:
        files = list_user_files(path, token)
        return {"status": "success", "result": files}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
@router.post("/create_directory")
async def create_directory(
    path: str = Form(...),
    dir_name: str = Form(...),
    token: str = Depends(oauth2_scheme)
):
    try:
        result = create_directory_supabase(path,dir_name, token)
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}