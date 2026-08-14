"""Mixins de modelos base para compartilhar com classes de modelo."""

import uuid
from typing import Any

from django.conf import settings
from django.db import models
from django.utils import timezone


class UUIDMixin(models.Model):
    """Mixin para adicionar um campo UUID como chave primária."""

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class TimestampMixin(models.Model):
    """Mixin para adicionar campos de timestamp de criação e atualização."""

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AuditMixin(models.Model):
    """Mixin para adicionar campos de auditoria de criação e atualização."""

    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_criado",
    )
    atualizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_atualizado",
    )
    deletado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_deletado",
    )

    class Meta:
        abstract = True


class CustomManager(models.Manager):
    """Gerenciador personalizado que filtra objetos não deletados."""

    def get_queryset(self) -> models.QuerySet:
        """Retorna queryset contendo apenas registros não deletados."""
        return super().get_queryset().filter(deletado_em=None)


class SoftDeleteMixin(models.Model):
    """Mixin para adicionar funcionalidade de soft delete."""

    deletado_em = models.DateTimeField(
        "Deletado em", default=None, null=True, blank=True
    )

    objects = CustomManager()
    dm_objects = models.Manager()

    class Meta:
        abstract = True

    def delete(
        self, using: Any | None = None, keep_parents: bool = False
    ) -> tuple[int, dict[str, int]]:
        """Marca o registro como deletado sem removê-lo fisicamente."""
        _ = using, keep_parents
        self.deletado_em = timezone.now()
        self.save(update_fields=["deletado_em"])
        return 1, {self._meta.label: 1}

    def hard_delete(
        self, using: str | None = None, keep_parents: bool = False
    ) -> tuple[int, dict[str, int]]:
        """Remove o registro fisicamente do banco de dados."""
        return super().delete(using=using, keep_parents=keep_parents)

    def restore(self) -> None:
        """Restaura um registro marcado como deletado."""
        self.deletado_em = None
        self.save(update_fields=["deletado_em"])


class BaseModel(UUIDMixin, TimestampMixin, AuditMixin, SoftDeleteMixin):
    """Modelo base com UUID, timestamp, auditoria e soft delete."""

    class Meta:
        abstract = True
