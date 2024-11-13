import hashlib
import os
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from fastapi.responses import JSONResponse,StreamingResponse

from configuration import upload_folder
from utilities import get_bucket_name

object_router = APIRouter(prefix="/{key:path}", tags=["Objects"])

multipart_uploads: Dict[str, Dict] = {}  # TODO: This need to replaced with memcache or redis


@object_router.put("/")
async def put_object(key: str, file: UploadFile = File(...), bucket_name: str = Depends(get_bucket_name)):
    bucket_path = os.path.join(upload_folder, bucket_name)
    os.makedirs(bucket_path, exist_ok=True)

    file_path = os.path.join(bucket_path, key)

    with open(file_path, "wb") as f:
        while contents := await file.read(1024):  # Read the file in chunks
            f.write(contents)

    # Generate ETag, good for multipart upload
    file.file.seek(0)
    body = await file.read()
    headers = {"ETag": hashlib.md5(body).hexdigest()}

    return JSONResponse(content={"message": "Object added successfully"}, headers=headers)


@object_router.delete("/")
async def delete_object(key: str, bucket_name: str = Depends(get_bucket_name)):
    file_path = os.path.join(upload_folder, bucket_name, key)
    if os.path.exists(file_path):
        os.remove(file_path)
        return {"message": "Object deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Object not found")

@object_router.get("/")
async def get_object(key: str, bucket_name: str = Depends(get_bucket_name)):
    file_path = os.path.join(upload_folder, bucket_name, key)
    if os.path.exists(file_path):
        def iterable():
            with open(file_path, "rb") as f:
                while chunk := f.read(1024):  # Read the file in chunks
                    yield chunk
        return StreamingResponse(iterable(), media_type="application/octet-stream")
    else:
        raise HTTPException(status_code=404, detail="Object not found")
