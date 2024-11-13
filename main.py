import os

from fastapi import FastAPI

from configuration import upload_folder
from routers.bucket_router import bucket_router
from routers.object_multipart_upload import multipart_router
from routers.object_router import object_router


app = FastAPI()
os.makedirs(upload_folder, exist_ok=True)

app.include_router(bucket_router)
app.include_router(object_router)
app.include_router(multipart_router)
