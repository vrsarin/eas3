import os

from pymemcache.client import base

from constants import ENV_BASE_UPLOAD_FOLDER, ENV_MEMCACHED_HOST, ENV_MEMCACHED_PORT

upload_folder = os.getenv(ENV_BASE_UPLOAD_FOLDER, "./data")

memcache_client = base.Client((os.getenv(ENV_MEMCACHED_HOST, 'localhost'), int(os.getenv(ENV_MEMCACHED_PORT, 11211))))