import pytest
from django.db import connection, models
from rest_framework.test import APIRequestFactory

from apps.core.models.mixins import BaseModel


@pytest.fixture
def api_factory():
    """Fixture que fornece uma instância do APIRequestFactory do DRF."""
    return APIRequestFactory()


class ModelBase(BaseModel):
    """Modelo de teste para BaseModel."""

    nome = models.CharField(max_length=100)

    class Meta:
        app_label = "core"


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
