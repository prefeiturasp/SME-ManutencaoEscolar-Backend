"""Fixtures para solicitações de manutenção."""

from collections.abc import Iterator
from typing import Any

import pytest
from django.core.files.storage import InMemoryStorage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import FileField

from apps.escola.models import Unidadeeducacional
from apps.servico.models import Servico
from apps.solicitacao_manutencao.models import FotoLocalReparo


@pytest.fixture(autouse=True)
def storage_de_fotos_em_memoria() -> Iterator[None]:
    """Evita acesso ao MinIO nos testes de solicitações de manutenção."""
    campo_arquivo = FotoLocalReparo._meta.get_field("arquivo")
    assert isinstance(campo_arquivo, FileField)
    storage_original = campo_arquivo.storage
    campo_arquivo.storage = InMemoryStorage()
    try:
        yield
    finally:
        campo_arquivo.storage = storage_original


@pytest.fixture
def servico() -> Servico:
    """Cria um serviço disponível para solicitações."""
    return Servico.objects.create(nome="Elétrica")


@pytest.fixture
def solicitacao_payload(
    unidade_educacional_emef: Unidadeeducacional,
    servico: Servico,
) -> dict[str, Any]:
    """Retorna um payload válido para criar uma solicitação."""
    return {
        "codigo": "SOL-001",
        "tipo_atendimento": "urgente",
        "informacoes_adicionais": "Reparo prioritário.",
        "unidade_educacional": str(unidade_educacional_emef.uuid),
        "fase": "solicitacao",
        "servicos": [
            {
                "servico": str(servico.uuid),
                "local_reparo": "Cozinha",
                "descricao": "Disjuntor desarmando constantemente.",
                "arquivos": [
                    {
                        "arquivo": SimpleUploadedFile(
                            "reparo.jpg",
                            b"conteudo da foto",
                            content_type="image/jpeg",
                        )
                    }
                ],
            }
        ],
    }
