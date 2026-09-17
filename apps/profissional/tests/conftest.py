"""Fixtures dos testes do domínio Profissional."""

from collections.abc import Iterator
from unittest.mock import patch

import pytest
from django.core.files.storage import InMemoryStorage
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.cargo.models import Cargo
from apps.profissional.models import DocumentoFuncaoProfissional


@pytest.fixture(autouse=True)
def storage_de_documentos_em_memoria() -> Iterator[None]:
    """Evita acesso ao MinIO nos testes de documentos profissionais."""
    campo_arquivo = DocumentoFuncaoProfissional._meta.get_field("arquivo")
    with patch.object(campo_arquivo, "storage", InMemoryStorage()):
        yield


@pytest.fixture
def cargo_profissional(db: None) -> Cargo:
    """Cria um cargo disponível para vincular ao profissional."""
    return Cargo.objects.create(nome="Eletricista", exige_documento=True)


@pytest.fixture
def profissional_payload(cargo_profissional: Cargo) -> dict[str, object]:
    """Retorna um payload válido de profissional."""
    return {
        "nome": "José da Silva",
        "cpf": "12345678901",
        "rg": "123456789",
        "status": True,
        "funcoes": [
            {
                "uuid_cargo": str(cargo_profissional.uuid),
                "documentos": [
                    {
                        "arquivo": SimpleUploadedFile(
                            "certificado-nr10.pdf",
                            b"conteudo",
                            content_type="application/pdf",
                        )
                    }
                ],
            }
        ],
    }
