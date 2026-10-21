"""Fixtures para solicitações de manutenção."""

from typing import Any

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.escola.models import TipoEscola, Unidadeeducacional
from apps.escola.models.diretoria_regional import DiretoriaRegional
from apps.servico.models import Servico


@pytest.fixture
def tipo_escola() -> TipoEscola:
    """Cria um tipo de escola."""
    return TipoEscola.objects.create(codigo_eol=1, sigla="EMEF")


@pytest.fixture
def unidade_educacional(
    diretoria_regional_centro: DiretoriaRegional,
    tipo_escola: TipoEscola,
) -> Unidadeeducacional:
    """Cria uma unidade educacional."""
    return Unidadeeducacional.objects.create(
        codigo_eol="123456",
        nome="EMEF Exemplo",
        diretoria_regional=diretoria_regional_centro,
        tipo_escola=tipo_escola,
    )


@pytest.fixture
def servico() -> Servico:
    """Cria um serviço disponível para solicitações."""
    return Servico.objects.create(nome="Elétrica")


@pytest.fixture
def solicitacao_payload(
    unidade_educacional: Unidadeeducacional,
    servico: Servico,
) -> dict[str, Any]:
    """Retorna um payload válido para criar uma solicitação."""
    return {
        "codigo": "SOL-001",
        "tipo_atendimento": "urgente",
        "informacoes_adicionais": "Reparo prioritário.",
        "unidade_educacional": str(unidade_educacional.uuid),
        "fase": "solicitacao",
        "servicos": [
            {
                "servico": str(servico.uuid),
                "servico_especifico": "Troca de disjuntor",
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
