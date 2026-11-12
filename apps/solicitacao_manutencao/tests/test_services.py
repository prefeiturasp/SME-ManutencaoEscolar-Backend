"""Testes dos serviços de solicitações de manutenção."""

from typing import Any
from uuid import uuid4

import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.core.services.anexo_service import AnexoService
from apps.escola.models import HistoricoResponsavel, Unidadeeducacional
from apps.solicitacao_manutencao.constants import SituacaoSolicitacao
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
    usuario_ue: Usuario,
    usuario_inativo: Usuario,
    historico_responsavel: HistoricoResponsavel,
) -> None:
    """Lista as solicitações da unidade vinculada ao usuário da UE."""
    usuario_ue.username = historico_responsavel.responsavel.registro_funcional
    usuario_ue.save(update_fields=["username"])
    solicitacao_visivel = SolicitacaoManutencao.objects.create(
        codigo="0000001",
        tipo_atendimento="comum",
        unidade_educacional=unidade_educacional_emef,
        criado_por=usuario_ue,
    )
    SolicitacaoManutencao.objects.create(
        codigo="0000002",
        tipo_atendimento="comum",
        unidade_educacional=unidade_educacional_emef,
        criado_por=usuario_inativo,
    )

    resultado = SolicitacaoManutencaoService().listar_por_usuario(usuario_ue)

    assert list(resultado) == [
        {
            "uuid": SolicitacaoManutencao.objects.get(codigo="0000002").uuid,
            "codigo": "0000002",
            "tipo_atendimento": "comum",
            "solicitante": "ue",
            "situacao": "nao_enviado_dre",
            "data_envio": None,
            "fase": "solicitacao",
        },
        {
            "uuid": solicitacao_visivel.uuid,
            "codigo": "0000001",
            "tipo_atendimento": "comum",
            "solicitante": "ue",
            "situacao": "nao_enviado_dre",
            "data_envio": None,
            "fase": "solicitacao",
        },
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


def test_sincronizar_arquivos_preserva_arquivos_existentes_e_adiciona_novos(
    unidade_educacional_emef: Unidadeeducacional,
    usuario_ativo: Usuario,
) -> None:
    """Mantém os anexos existentes e inclui os novos na lista final."""
    solicitacao = SolicitacaoManutencao.objects.create(
        codigo="0000001",
        tipo_atendimento="comum",
        unidade_educacional=unidade_educacional_emef,
        criado_por=usuario_ativo,
    )
    servico = ServicoManutencaoRepository().criar(
        {
            "servico_especifico": "Reparo hidráulico",
            "local_reparo": "Cozinha",
            "descricao": "Vazamento na pia",
        },
        solicitacao.id,
        usuario_ativo,
    )
    arquivo_existente = ArquivoServicoManutencaoRepository().criar(
        {
            "nome_original": "existente.jpg",
            "arquivo": SimpleUploadedFile(
                "existente.jpg",
                b"arquivo existente",
                content_type="image/jpeg",
            ),
            "tipo": "imagem",
            "tipo_mime": "image/jpeg",
            "tamanho_bytes": 17,
        },
        servico["id"],
        usuario_ativo,
    )

    novo_arquivo = SimpleUploadedFile(
        "novo.jpg",
        b"arquivo novo",
        content_type="image/jpeg",
    )

    resultado = SolicitacaoManutencaoUeService()._sincronizar_arquivos(
        servico_id=servico["id"],
        dados=[
            {"uuid": arquivo_existente["uuid"]},
            {"arquivo": novo_arquivo},
        ],
        usuario=usuario_ativo,
    )

    assert [str(item["uuid"]) for item in resultado] == [
        str(arquivo_existente["uuid"]),
        str(resultado[-1]["uuid"]),
    ]
    assert len(resultado) == 2
    assert resultado[0]["nome_original"] == "existente.jpg"
    assert resultado[1]["nome_original"] == "novo.jpg"


def test_atualiza_solicitacao_sem_alterar_servicos(
    unidade_educacional_emef: Unidadeeducacional,
    usuario_ativo: Usuario,
) -> None:
    """Atualiza somente os campos principais da solicitação."""
    solicitacao = SolicitacaoManutencao.objects.create(
        codigo="0000013",
        tipo_atendimento="comum",
        unidade_educacional=unidade_educacional_emef,
        criado_por=usuario_ativo,
    )

    resultado = SolicitacaoManutencaoUeService().atualizar(
        {"id": solicitacao.id, "situacao": solicitacao.situacao},
        {"informacoes_adicionais": "Atualizada"},
        usuario_ativo,
    )

    assert resultado["informacoes_adicionais"] == "Atualizada"
    assert "servicos" not in resultado


def test_atualiza_e_envia_solicitacao_para_analise(
    unidade_educacional_emef: Unidadeeducacional,
    usuario_ativo: Usuario,
) -> None:
    """Registra situação e data ao enviar solicitação editada."""
    solicitacao = SolicitacaoManutencao.objects.create(
        codigo="0000018",
        tipo_atendimento="comum",
        unidade_educacional=unidade_educacional_emef,
        criado_por=usuario_ativo,
    )

    resultado = SolicitacaoManutencaoUeService().atualizar(
        {"id": solicitacao.id, "situacao": solicitacao.situacao},
        {"informacoes_adicionais": "Enviada"},
        usuario_ativo,
        enviar=True,
    )

    assert resultado["situacao"] == SituacaoSolicitacao.AGUARDANDO_ANALISE_DRE
    assert resultado["data_envio"] is not None


def test_nao_atualiza_solicitacao_em_situacao_nao_editavel(
    unidade_educacional_emef: Unidadeeducacional,
    usuario_ativo: Usuario,
) -> None:
    """Impede edição quando a solicitação aguarda análise da DRE."""
    solicitacao = SolicitacaoManutencao.objects.create(
        codigo="0000017",
        tipo_atendimento="comum",
        unidade_educacional=unidade_educacional_emef,
        situacao=SituacaoSolicitacao.AGUARDANDO_ANALISE_DRE,
        criado_por=usuario_ativo,
    )

    with pytest.raises(ValidationError, match="só pode ser editada"):
        SolicitacaoManutencaoUeService().atualizar(
            {"id": solicitacao.id, "situacao": solicitacao.situacao},
            {"informacoes_adicionais": "Não deve ser salva"},
            usuario_ativo,
        )

    solicitacao.refresh_from_db()
    assert solicitacao.informacoes_adicionais == ""
    assert solicitacao.situacao == SituacaoSolicitacao.AGUARDANDO_ANALISE_DRE


def test_sincroniza_servicos_removendo_existentes_e_criando_novos(
    unidade_educacional_emef: Unidadeeducacional,
    usuario_ativo: Usuario,
) -> None:
    """Remove serviços omitidos e cadastra os serviços novos enviados."""
    solicitacao = SolicitacaoManutencao.objects.create(
        codigo="0000014",
        tipo_atendimento="comum",
        unidade_educacional=unidade_educacional_emef,
        criado_por=usuario_ativo,
    )
    existente = ServicoManutencaoRepository().criar(
        {
            "servico_especifico": "Serviço antigo",
            "local_reparo": "Cozinha",
            "descricao": "Descrição antiga",
        },
        solicitacao.id,
        usuario_ativo,
    )

    resultado = SolicitacaoManutencaoUeService()._sincronizar_servicos(
        solicitacao.id,
        [
            {
                "servico_especifico": "Serviço novo",
                "local_reparo": "Sala",
                "descricao": "Descrição nova",
                "arquivos": [],
            }
        ],
        usuario_ativo,
    )

    assert len(resultado) == 1
    assert resultado[0]["servico_especifico"] == "Serviço novo"
    assert not ServicoManutencaoRepository.model.objects.filter(
        pk=existente["id"]
    ).exists()


def test_rejeita_servico_que_nao_pertence_a_solicitacao(
    unidade_educacional_emef: Unidadeeducacional,
    usuario_ativo: Usuario,
) -> None:
    """Rejeita UUID de serviço desconhecido na atualização."""
    solicitacao = SolicitacaoManutencao.objects.create(
        codigo="0000015",
        tipo_atendimento="comum",
        unidade_educacional=unidade_educacional_emef,
    )

    with pytest.raises(ValidationError, match="Serviço não encontrado"):
        SolicitacaoManutencaoUeService()._sincronizar_servicos(
            solicitacao.id,
            [{"uuid": str(uuid4()), "arquivos": []}],
            usuario_ativo,
        )


def test_rejeita_arquivo_que_nao_pertence_ao_servico(
    unidade_educacional_emef: Unidadeeducacional,
    usuario_ativo: Usuario,
) -> None:
    """Rejeita UUID de anexo desconhecido na atualização."""
    solicitacao = SolicitacaoManutencao.objects.create(
        codigo="0000016",
        tipo_atendimento="comum",
        unidade_educacional=unidade_educacional_emef,
    )
    servico = ServicoManutencaoRepository().criar(
        {
            "servico_especifico": "Serviço",
            "local_reparo": "Sala",
            "descricao": "Descrição",
        },
        solicitacao.id,
        usuario_ativo,
    )

    with pytest.raises(ValidationError, match="Arquivo não encontrado"):
        SolicitacaoManutencaoUeService()._sincronizar_arquivos(
            servico["id"], [{"uuid": str(uuid4())}], usuario_ativo
        )


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
