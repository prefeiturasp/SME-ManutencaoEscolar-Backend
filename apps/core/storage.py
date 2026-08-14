"""Funções utilitárias para configuração do storage privado no MinIO."""

from django_minio_backend.models import MinioBackend

from config.settings import MINIO_BUCKET_NAME


def get_private_storage() -> MinioBackend:
    """Cria o backend de armazenamento privado do MinIO.

    O backend utiliza o bucket definido em ``MINIO_BUCKET_NAME`` e o
    storage configurado como ``default``

    Returns:
        MinioBackend: Instância do backend do MinIO configurada para o
            armazenamento privado.
    """
    return MinioBackend(
        bucket_name=MINIO_BUCKET_NAME,
        storage_name="default",
    )
