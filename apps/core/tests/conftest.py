import pytest
from django.db import connection, models
from rest_framework.test import APIRequestFactory

from apps.core.models.mixins import BaseModel
from apps.usuarios.constants import PerfilAcesso
from apps.usuarios.models.cargo_eol import CargoEOL
from apps.usuarios.models.usuario import Usuario


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


@pytest.fixture
def cargo_perfil_diretor():
    """_summary_."""
    return CargoEOL.objects.create(
        codigo="9999",
        nome="Diretor",
        perfil=PerfilAcesso.UE,
    )


@pytest.fixture
def usuario_ativo(cargo_perfil_diretor):
    """_summary_."""
    return Usuario.objects.create(
        username="9876543219",
        nome="João da Silva",
        registro_funcional=None,
        cpf="9876543219",
        cargo=cargo_perfil_diretor,
        is_active=True,
    )


@pytest.fixture
def usuario_inativo(cargo_perfil_diretor):
    """_summary_."""
    return Usuario.objects.create(
        username="9876543211",
        nome="Pedro da Silva",
        registro_funcional=None,
        cpf="9876543211",
        cargo=cargo_perfil_diretor,
        is_active=False,
    )
