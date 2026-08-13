"""_summary_.

Returns:
    _type_: _description_
"""

from django_minio_backend.models import MinioBackend

from config.settings import MINIO_BUCKET_NAME


def get_private_storage() -> MinioBackend:
    """_summary_.

    Returns:
        _type_: _description_
    """
    return MinioBackend(
        bucket_name=MINIO_BUCKET_NAME,
        storage_name="default",
    )
