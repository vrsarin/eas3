from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class Location(BaseModel):
    Name: str
    Type: str

class Bucket(BaseModel):
    DataRedundancy: str
    Type: str

class CreateBucketConfiguration(BaseModel):
    LocationConstraint: str
    Location: Location
    Bucket: Bucket


class BucketInfo(BaseModel):
    Name: str
    CreationDate: datetime
    BucketRegion: str

class Owner(BaseModel):
    DisplayName: str
    ID: str

class ListBucketsResponse(BaseModel):
    Buckets: List[BucketInfo]
    Owner: Owner
    ContinuationToken: Optional[str] = None
    Prefix: Optional[str] = None