"""Mixins de modelos base para compartilhar com classes de modelo."""

import uuid
from typing import Any

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.constants import TipoArquivo
from apps.core.storage import get_private_storage


class CustomManager(models.Manager):
    """Gerenciador personalizado que filtra objetos não deletados."""

    def get_queryset(self) -> models.QuerySet:
        """Retorna queryset contendo apenas registros não deletados."""
        return super().get_queryset().filter(deletado_em=None)


class UUIDMixin(models.Model):
    """Mixin para adicionar um campo UUID como chave primária."""

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class CriacaoMixin(models.Model):
    """Adiciona informações relacionadas à criação do registro."""

    criado_em = models.DateTimeField(auto_now_add=True)
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_criado",
    )

    class Meta:
        abstract = True


class AtualizacaoMixin(models.Model):
    """Adiciona informações relacionadas à atualização do registro."""

    atualizado_em = models.DateTimeField(auto_now=True)
    atualizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_atualizado",
    )

    class Meta:
        abstract = True


class SoftDeleteMixin(models.Model):
    """Mixin para adicionar funcionalidade de soft delete."""

    deletado_em = models.DateTimeField(
        "Deletado em", default=None, null=True, blank=True
    )
    deletado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_deletado",
    )

    objects = CustomManager()
    dm_objects = models.Manager()

    class Meta:
        abstract = True

    def soft_delete(
        self,
        usuario: Any | None = None,
    ) -> tuple[int, dict[str, int]]:
        """Marca o registro como deletado sem removê-lo fisicamente."""
        self.deletado_em = timezone.now()
        self.deletado_por = usuario
        self.save(update_fields=["deletado_em", "deletado_por"])
        return 1, {self._meta.label: 1}

    def delete(
        self, using: str | None = None, keep_parents: bool = False
    ) -> tuple[int, dict[str, int]]:
        """Remove o registro fisicamente do banco de dados."""
        return super().delete(using=using, keep_parents=keep_parents)

    def restore(self) -> None:
        """Restaura um registro marcado como deletado."""
        self.deletado_em = None
        self.save(update_fields=["deletado_em"])


class AuditMixin(
    CriacaoMixin,
    AtualizacaoMixin,
    SoftDeleteMixin,
):
    """Adiciona informações de criação, atualização e exclusão."""

    class Meta:
        abstract = True


class BaseModel(UUIDMixin, AuditMixin):
    """Modelo base com UUID, timestamp, auditoria e soft delete."""

    class Meta:
        abstract = True


class AnexoMixin(BaseModel):
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
        abstract = True

    @property
    def nome_bucket(self) -> str:
        """Retorna o nome do objeto armazenado no bucket do MinIO.

        Returns:
            str: Caminho e nome do objeto no armazenamento.
        """
        if not self.arquivo.name:
            raise ValueError("O nome do arquivo não está definido.")
        return self.arquivo.name

    @property
    def url(self) -> str:
        """Retorna a URL de acesso ao arquivo armazenado.

        Returns:
            str: URL do arquivo no armazenamento configurado.
        """
        return self.arquivo.url
