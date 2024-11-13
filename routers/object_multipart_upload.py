import base64
import hashlib
import os
import zlib
from uuid import uuid4

from fastapi import APIRouter, Request, Depends, Header, HTTPException
from fastapi.responses import  JSONResponse

from configuration import memcache_client, upload_folder
from routers.models.object_models import InitiateMultipartUploadResponse, CompleteMultipartUploadRequest
from utilities import get_bucket_name

multipart_router = APIRouter(prefix="/{key:path}", tags=["Multipart Upload"])

@multipart_router.post("/?uploads", summary="Initiate a large file upload")
async def initiate_multipart_upload(key: str, bucket_name: str = Depends(get_bucket_name)):
    upload_id = str(uuid4())
    multipart_upload_info = {"key": key, "bucket": bucket_name, "parts": []}
    memcache_client.set(upload_id, multipart_upload_info)

    response_model = InitiateMultipartUploadResponse(
        Bucket=bucket_name,
        Key=key,
        UploadId=upload_id
    )

    return response_model


@multipart_router.put("/?partNumber={part_number}&uploadId={upload_id}",
                   summary="Add content to large file upload initiated using multipart upload")
async def upload_part(
        key: str,
        part_number: int,
        upload_id: str,
        request: Request,
        bucket_name: str = Depends(get_bucket_name),
        content_type: str = Header(None),
        content_length: int = Header(None),
        content_md5: str = Header(None),
        content_crc32: str = Header(None)
):
    multipart_upload_info = memcache_client.get(upload_id)
    if not multipart_upload_info:
        raise HTTPException(status_code=404, detail="Upload ID not found")

    body = await request.body()

    # Validate Content-MD5
    if content_md5:
        md5 = hashlib.md5(body).digest()
        if base64.b64encode(md5).decode() != content_md5:
            raise HTTPException(status_code=400, detail="Content-MD5 mismatch")

    # Calculate and validate CRC32
    crc32 = zlib.crc32(body) & 0xffffffff
    if content_crc32 and format(crc32, '08x') != content_crc32:
        raise HTTPException(status_code=400, detail="Content-CRC32 mismatch")

    multipart_upload_info["parts"].append((part_number, body, crc32))
    memcache_client.set(upload_id, multipart_upload_info)

    return {"message": "Part uploaded successfully"}


@multipart_router.post("/?uploadId={upload_id}", summary="Complete the multipart upload using multipart upload")
async def complete_multipart_upload(key: str, upload_id: str, complete_request: CompleteMultipartUploadRequest,
                                    bucket_name: str = Depends(get_bucket_name)):
    multipart_upload_info = memcache_client.get(upload_id)
    if not multipart_upload_info:
        raise HTTPException(status_code=404, detail="Upload ID not found")

    parts = sorted(multipart_upload_info["parts"], key=lambda x: x[0])

    bucket_path = os.path.join(upload_folder, bucket_name)
    os.makedirs(bucket_path, exist_ok=True)

    file_path = os.path.join(bucket_path, key)
    try:
        with open(file_path, "wb") as f:
            for part_number, part_data, crc32 in parts:
                f.write(part_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to write file: {str(e)}")

    # Generate ETag
    headers = {"ETag": hashlib.md5(open(file_path, "rb").read()).hexdigest()}
    return JSONResponse(content={"message": "Multipart upload completed successfully"}, headers=headers)