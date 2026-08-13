"""Modelos relacionados ao armazenamento de arquivos anexados."""

from django.db import models

from apps.core.constants import TipoArquivo
from apps.core.models.mixins import BaseModel
from apps.core.storage import get_private_storage


class Anexo(BaseModel):
    """Representa um arquivo anexado e armazenado no MinIO.

    Armazena o nome original do arquivo, seus metadados e o tipo de arquivo,
    além de disponibilizar propriedades para acesso ao nome do objeto e à
    URL do arquivo armazenado.
    """

    nome_original = models.CharField(
        max_length=255,
    )

    arquivo = models.FileField(
        upload_to="arquivos/%Y/%m/%d/",
        storage=get_private_storage,
    )

    tipo = models.CharField(
        max_length=20,
        choices=TipoArquivo.choices,
    )

    tipo_mime = models.CharField(
        max_length=150,
        blank=True,
    )

    tamanho_bytes = models.PositiveBigIntegerField(
        default=0,
    )

    class Meta:
        ordering = ["-criado_em"]

    def __str__(self) -> str:
        """Retorna o nome original do arquivo.

        Returns:
            str: Nome original do arquivo anexado.
        """
        return self.nome_original

    @property
    def nome_bucket(self) -> str:
        """Retorna o nome do objeto armazenado no bucket do MinIO.

        Returns:
            str: Caminho e nome do objeto no armazenamento.
        """
        if self.arquivo.name is None:
            raise ValueError("O nome do arquivo não está definido.")
        return self.arquivo.name

    @property
    def url(self) -> str:
        """Retorna a URL de acesso ao arquivo armazenado.

        Returns:
            str: URL do arquivo no armazenamento configurado.
        """
        return self.arquivo.url
