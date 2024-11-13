from typing import Optional, List

from pydantic import BaseModel


class InitiateMultipartUploadResponse(BaseModel):
    Bucket: str
    Key: str
    UploadId: str

class Part(BaseModel):
    PartNumber: int
    ETag: str
    ChecksumCRC32: Optional[str] = None
    ChecksumCRC32C: Optional[str] = None
    ChecksumSHA1: Optional[str] = None
    ChecksumSHA256: Optional[str] = None

class CompleteMultipartUploadRequest(BaseModel):
    Parts: List[Part]