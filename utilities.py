from fastapi import HTTPException, Request

from constants import HTTP_HOST_HEADER


def get_bucket_name(request: Request) -> str:
    host = request.headers.get(HTTP_HOST_HEADER)
    if not host:
        raise HTTPException(status_code=400, detail="Host header not found")

    parts = host.split(".")
    if len(parts) <= 2:
        raise HTTPException(status_code=400, detail="Bucket name not found in subdomain")

    return parts[0]