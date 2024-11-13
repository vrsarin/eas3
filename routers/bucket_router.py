import os
from datetime import datetime
from typing import Optional

from fastapi import APIRouter
from fastapi import HTTPException, Request, Depends, Query
from starlette.responses import JSONResponse

from configuration import upload_folder
from routers.models.bucket_models import CreateBucketConfiguration, ListBucketsResponse
from utilities import get_bucket_name

bucket_router = APIRouter(tags=["Bucket"])

@bucket_router.put("/",responses={
    200: {"description": "Bucket created successfully"},
    400: {"description": "Bad Request"},
    500: {"description": "Internal Server Error"}
})
async def create_bucket(config: CreateBucketConfiguration, request: Request,bucket_name: str = Depends(get_bucket_name)):
    bucket_path = os.path.join(upload_folder, bucket_name)
    try:
        os.makedirs(bucket_path, exist_ok=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create bucket folder: {str(e)}")

    return JSONResponse(status_code=200, content=f'Location": "{request.url.scheme}://{bucket_name}.{request.url.hostname}:{request.url.port}/"')


@bucket_router.delete("/", status_code=204, responses={
    204: {"description": "No Content"},
    400: {"description": "Bad Request"},
    409: {"description": "Bucket not found"},
    500: {"description": "Internal Server Error"}
})
async def delete_bucket(bucket_name: str = Depends(get_bucket_name)):
    bucket_path = os.path.join(upload_folder, bucket_name)
    try:
        if os.path.exists(bucket_path):
            os.rmdir(bucket_path)
        else:
            raise HTTPException(status_code=404, detail="Bucket not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete bucket folder: {str(e)}")

    return JSONResponse(status_code=204,content="No Content")


@bucket_router.get("/", response_model=ListBucketsResponse, responses={
    200: {"description": "Buckets listed successfully"},
    500: {"description": "Internal Server Error"}
})
async def list_buckets(
        bucket_region: Optional[str] = Query(None, alias="bucket-region"),
        continuation_token: Optional[str] = Query(None, alias="continuation-token"),
        max_buckets: Optional[int] = Query(None, alias="max-buckets"),
        prefix: Optional[str] = Query(None)
):
    try:
        bucket_names = os.listdir(upload_folder)
        buckets = [
            {"Name": name, "CreationDate": datetime.fromtimestamp(os.path.getctime(os.path.join(upload_folder, name))),
             "BucketRegion": bucket_region or "us-east-1"}
            for name in bucket_names if os.path.isdir(os.path.join(upload_folder, name))
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list buckets: {str(e)}")

    owner = {"DisplayName": "owner-name", "ID": "owner-id"} # This will be user that will create the bucket

    return {
        "Buckets": buckets,
        "Owner": owner,
        "ContinuationToken": continuation_token,
        "Prefix": prefix
    }
