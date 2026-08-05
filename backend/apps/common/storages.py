"""Optional object storage backend (S3 / MinIO)."""

from __future__ import annotations

from storages.backends.s3boto3 import S3Boto3Storage


class MediaStorage(S3Boto3Storage):
    """Production media storage.

    Bucket, credentials and endpoint are read from Django settings
    (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME,
    AWS_S3_ENDPOINT_URL). ACLs are managed by the bucket policy — not per
    object — to avoid deprecated S3 ACL behavior.
    """

    default_acl = None
    file_overwrite = False
    querystring_auth = True
    querystring_expire = 3600
