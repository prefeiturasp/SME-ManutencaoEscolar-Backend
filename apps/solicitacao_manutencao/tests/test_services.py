"""Testes dos serviços de solicitações de manutenção."""

from typing import Any

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.core.services.anexo_service import AnexoService
from apps.escola.models import Unidadeeducacional
from apps.solicitacao_manutencao.models import (
    FotoLocalReparo,
    SolicitacaoManutencao,
)
from apps.solicitacao_manutencao.repository import (
    ArquivoServicoManutencaoRepository,
    ServicoManutencaoRepository,
    SolicitacaoManutencaoRepository,
)
from apps.solicitacao_manutencao.services.solicitacao_service import (
    SolicitacaoManutencaoService,
)
from apps.solicitacao_manutencao.services.ue_services import (
    SolicitacaoManutencaoUeService,
)
from apps.usuarios.models import Usuario

pytestmark = pytest.mark.django_db


def test_lista_solicitacoes_visiveis_para_usuario(
    unidade_educacional_emef: Unidadeeducacional,
    usuario_ativo: Usuario,
    usuario_inativo: Usuario,
) -> None:
    """Lista somente as solicitações visíveis para o usuário da UE."""
    solicitacao_visivel = SolicitacaoManutencao.objects.create(
        codigo="0000001",
        tipo_atendimento="comum",
        unidade_educacional=unidade_educacional_emef,
        criado_por=usuario_ativo,
    )
    SolicitacaoManutencao.objects.create(
        codigo="0000002",
        tipo_atendimento="comum",
        unidade_educacional=unidade_educacional_emef,
        criado_por=usuario_inativo,
    )

    resultado = SolicitacaoManutencaoService().listar_por_usuario(
        usuario_ativo
    )

    assert list(resultado) == [
        {
            "uuid": solicitacao_visivel.uuid,
            "codigo": "0000001",
            "tipo_atendimento": "comum",
            "situacao": "nao_enviado_dre",
            "data_envio": None,
            "fase": "solicitacao",
        }
    ]


def test_inicializar_com_dependencias_informadas() -> None:
    """Utiliza as dependências informadas na inicialização do serviço."""
    repository = SolicitacaoManutencaoRepository()
    servico_repository = ServicoManutencaoRepository()
    arquivo_repository = ArquivoServicoManutencaoRepository()
    anexo_service = AnexoService()

    service = SolicitacaoManutencaoUeService(
        repository=repository,
        servico_repository=servico_repository,
        arquivo_repository=arquivo_repository,
        anexo_service=anexo_service,
    )

    assert service.repository is repository
    assert service.servico_repository is servico_repository
    assert service.arquivo_repository is arquivo_repository
    assert service.anexo_service is anexo_service


def test_criar_servico_com_arquivo(
    unidade_educacional_emef: Unidadeeducacional,
    usuario_ativo: Usuario,
) -> None:
    """Cria e associa um arquivo validado ao serviço de manutenção."""
    arquivo = SimpleUploadedFile(
        "reparo.jpg",
        b"conteudo da foto",
        content_type="image/jpeg",
    )
    dados: dict[str, Any] = {
        "tipo_atendimento": "comum",
        "unidade_educacional": unidade_educacional_emef,
        "servicos": [
            {
                "servico_especifico": "Reparo hidráulico",
                "local_reparo": "Cozinha",
                "descricao": "Vazamento na pia",
                "arquivos": [{"arquivo": arquivo}],
            }
        ],
    }

    resultado = SolicitacaoManutencaoUeService().criar(dados, usuario_ativo)

    arquivo_criado = resultado["servicos"][0]["arquivos"][0]
    assert arquivo_criado["nome_original"] == "reparo.jpg"
    assert arquivo_criado["tipo"] == "imagem"
    assert arquivo_criado["criado_por"] == usuario_ativo
    assert FotoLocalReparo.objects.filter(id=arquivo_criado["id"]).exists()


def test_criar_solicitacoes_com_codigos_crescentes_de_sete_digitos(
    unidade_educacional_emef: Unidadeeducacional,
    usuario_ativo: Usuario,
) -> None:
    """Gera códigos sequenciais com sete dígitos."""
    service = SolicitacaoManutencaoUeService()

    def criar_solicitacao() -> dict[str, Any]:
        """Cria uma solicitação com os dados mínimos necessários."""
        return service.criar(
            {
                "tipo_atendimento": "comum",
                "unidade_educacional": unidade_educacional_emef,
                "servicos": [
                    {
                        "servico_especifico": "Reparo hidráulico",
                        "local_reparo": "Cozinha",
                        "descricao": "Vazamento na pia",
                        "arquivos": [],
                    }
                ],
            },
            usuario_ativo,
        )

    primeira_solicitacao = criar_solicitacao()
    segunda_solicitacao = criar_solicitacao()

    assert primeira_solicitacao["codigo"] == "0000001"
    assert segunda_solicitacao["codigo"] == "0000002"
