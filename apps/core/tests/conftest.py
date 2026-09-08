from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection, models
from rest_framework.test import APIRequestFactory

from apps.core.constants import MAPA_EXTENSOES_TIPO_ARQUIVO
from apps.core.models.mixins import BaseModel
from apps.core.services.anexo_service import AnexoService
from apps.usuarios.constants import PerfilAcesso
from apps.usuarios.models.usuario import Usuario

URL_ARQUIVO = "https://minio.local/documento.pdf"
TYPE_PDF = "application/pdf"
DOCUMENTO_PDF = "documento.pdf"


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
def usuario_ativo(cargo_perfil_diretor):
    """Fixture de usuario ativo."""
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
    """Fixture de usuario inativo."""
    return Usuario.objects.create(
        username="9876543211",
        nome="Pedro da Silva",
        registro_funcional=None,
        cpf="9876543211",
        cargo=cargo_perfil_diretor,
        is_active=False,
    )


@pytest.fixture
def usuario_ativo_dict(usuario_ativo):
    """Fixture de usuario inativo retornando em diconario."""
    return {
        "id": usuario_ativo.id,
        "uuid": usuario_ativo.uuid,
        "nome": usuario_ativo.nome,
        "email": usuario_ativo.email,
        "registro_funcional": usuario_ativo.registro_funcional,
        "cpf": usuario_ativo.cpf,
        "username": usuario_ativo.username,
        "perfil_acesso": {
            "cargo": usuario_ativo.cargo.nome,
            "perfil": {
                "codigo": usuario_ativo.perfil,
                "descricao": PerfilAcesso(usuario_ativo.perfil).label,
            },
        },
    }


@pytest.fixture(scope="module")
def bloquear_uploads_minio(monkeypatch):
    """Impede qualquer tentativa de escrita no bucket durante testes."""
    from apps.core.models.anexo import Anexo

    monkeypatch.setattr(
        Anexo.arquivo.field.storage,
        "_save",
        lambda *args, **kwargs: "testes/arquivo-mockado",
    )


@pytest.fixture
def anexo() -> SimpleNamespace:
    """Fixture que representa um anexo persistido."""
    arquivo = Mock()
    arquivo.name = f"arquivos/{DOCUMENTO_PDF}"
    arquivo.url = URL_ARQUIVO
    arquivo.open.return_value = "stream"
    anexo = SimpleNamespace(
        uuid="12345678-1234-5678-1234-567812345678",
        nome_original=DOCUMENTO_PDF,
        tipo="documento",
        tipo_mime=TYPE_PDF,
        tamanho_bytes=123,
        url=URL_ARQUIVO,
        arquivo=arquivo,
    )
    anexo.delete = Mock()
    return anexo


@pytest.fixture
def mock_repository_anexo() -> Mock:
    """Mock do repository de anexo."""
    repository = Mock()
    repository.criar.return_value = {
        "uuid": "12345678-1234-5678-1234-567812345678",
        "nome": DOCUMENTO_PDF,
        "tipo": MAPA_EXTENSOES_TIPO_ARQUIVO["pdf"],
        "tipo_mime": TYPE_PDF,
        "tamanho": 8,
        "url": URL_ARQUIVO,
    }
    return repository


@pytest.fixture
def arquivo(
    nome: str = DOCUMENTO_PDF, conteudo: bytes = b"conteudo"
) -> SimpleUploadedFile:
    """Cria um arquivo PDF para uso nos testes."""
    return SimpleUploadedFile(
        name=nome,
        content=conteudo,
        content_type=TYPE_PDF,
    )


@pytest.fixture
def anexo_service(mock_repository_anexo):
    """Cria o serviço de anexos usando o repository mockado."""
    return AnexoService(repository=mock_repository_anexo)
