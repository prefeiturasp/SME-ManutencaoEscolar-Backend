import uuid

import pytest
from django.conf import settings
from django.db import connection, models
from django.utils import timezone
from rest_framework.test import APIRequestFactory

from apps.core.models.mixins import CustomManager


@pytest.fixture
def api_factory():
    """Fixture que fornece uma instância do APIRequestFactory do DRF."""
    return APIRequestFactory()


class ModelBase(models.Model):
    """Modelo de teste para BaseModel."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="core_modelbase_criado",
    )
    atualizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="core_modelbase_atualizado",
    )
    deletado_em = models.DateTimeField(
        "Deletado em", default=None, null=True, blank=True
    )
    nome = models.CharField(max_length=100)

    objects = CustomManager()
    dm_objects = models.Manager()

    class Meta:
        app_label = "core"

    def delete(self, user=None):
        self.deletado_em = timezone.now()
        self.save(update_fields=["deletado_em"])

    def hard_delete(self, using=None, keep_parents=False):
        return super().delete(using=using, keep_parents=keep_parents)

    def restore(self):
        self.deletado_em = None
        self.save(update_fields=["deletado_em"])


@pytest.fixture(scope="session", autouse=True)
def django_test_db_setup(django_db_setup, django_db_blocker):
    """Cria as tabelas de teste necessárias."""
    with (
        django_db_blocker.unblock(),
        connection.schema_editor() as schema_editor,
    ):
        schema_editor.create_model(ModelBase)

    yield

    with (
        django_db_blocker.unblock(),
        connection.schema_editor() as schema_editor,
    ):
        schema_editor.delete_model(ModelBase)
