 
from fastapi import APIRouter, Body, Depends, Form, Query, UploadFile, File,status,HTTPException
import shutil
import os

from ..services.cloud import create_directory_supabase,  delete_directory_supabase, delete_file_supabase, get_signed_url_supabase, list_user_files, rename_directory_supabase, rename_file_supabase, upload_to_supabase
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

@router.delete("/delete_file")
async def delete_file(
    file_path: str = Body(..., embed=True),
    token: str = Depends(oauth2_scheme)
):
    try:
        result = delete_file_supabase(file_path, token)
        return {"status": "success", "result": result}
    except HTTPException:
        # Re-raise HTTP exceptions to maintain proper status codes
        raise
    except Exception as e:
        # Raise proper HTTP exception instead of returning error in response body
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete file: {str(e)}"
        )
    
@router.delete("/delete_dir")
async def delete_directory(
    dir_path: str = Body(..., embed=True),
    token: str = Depends(oauth2_scheme)
):
    try:
        result = delete_directory_supabase(dir_path, token)
        return {"status": "success", "result": result}
    except HTTPException:
        # Re-raise HTTP exceptions to maintain proper status codes
        raise
    except Exception as e:
        # Raise proper HTTP exception instead of returning error in response body
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete directory: {str(e)}"
        )

@router.get("/get_signed_url")
async def get_signed_url(
    file_path: str = Query(..., description="Path to the file"),
    token: str = Depends(oauth2_scheme)
):
    try:
        signed_url = get_signed_url_supabase(file_path, token)
        return {"status": "success", "result": signed_url}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
@router.post("/rename_dir")
async def rename_directory(
    old_dir_path: str = Form(...),
    new_dir_name: str = Form(...),
    token: str = Depends(oauth2_scheme)
):
    try:
        result = rename_directory_supabase(old_dir_path, new_dir_name, token)
        return {"status": "success", "result": result}
    except Exception as e:
         raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to rename directory: {str(e)}"
        )

@router.post("/rename_file")
async def rename_file(
    old_file_path: str = Form(...),
    new_file_name: str = Form(...),
    token: str = Depends(oauth2_scheme)
):
    try:
        result = rename_file_supabase(old_file_path, new_file_name, token)
        return {"status": "success", "result": result}
    except Exception as e:
         raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to rename file: {str(e)}"
        )