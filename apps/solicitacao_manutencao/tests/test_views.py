"""Testes do endpoint de criação de solicitações."""

from datetime import datetime
from typing import Any

import pytest
from django.contrib.auth.models import AnonymousUser
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, ValidationError
from rest_framework.request import Request
from rest_framework.test import APIClient, APIRequestFactory

from apps.escola.models import HistoricoResponsavel
from apps.solicitacao_manutencao.api.views import SolicitacaoManutencaoViewSet
from apps.solicitacao_manutencao.models import (
    ServicoManutencao,
    SolicitacaoManutencao,
)
from apps.solicitacao_manutencao.serializers import (
    ServicoManutencaoDetalhesSerializer,
    SolicitacaoManutencaoCriarEditarSerializer,
    SolicitacaoManutencaoDetalheSerializer,
    SolicitacaoManutencaoListSerializer,
)
from apps.usuarios.constants import PerfilAcesso
from apps.usuarios.models import Usuario

pytestmark = pytest.mark.django_db

URL_SOLICITACAO_UE = "/api/v1/solicitacoes-manutencao/solicitacao-ue/"
URL_EDITAR_SOLICITACAO_UE = (
    "/api/v1/solicitacoes-manutencao/editar-solicitacao-ue/{}/"
)
URL_SOLICITACOES = "/api/v1/solicitacoes-manutencao/"
URL_SOLICITACAO = "/api/v1/solicitacoes-manutencao/{}/"
URL_SITUACOES = "/api/v1/solicitacoes-manutencao/situacoes/"
URL_FASES = "/api/v1/solicitacoes-manutencao/fases/"
URL_TIPOS_ATENDIMENTO = "/api/v1/solicitacoes-manutencao/tipos-atendimento/"


def _postar_solicitacao(
    cliente: APIClient,
    url: str,
    payload: dict[str, Any],
    metodo: str = "post",
) -> Any:
    """Envia uma solicitação com seus arquivos em formato multipart."""
    dados = {
        chave: valor for chave, valor in payload.items() if chave != "servicos"
    }
    for indice_servico, servico in enumerate(payload["servicos"]):
        for chave, valor in servico.items():
            if chave != "arquivos":
                dados[f"servicos[{indice_servico}]{chave}"] = valor
        for indice_arquivo, arquivo in enumerate(servico.get("arquivos", [])):
            for chave, valor in arquivo.items():
                if hasattr(valor, "seek"):
                    valor.seek(0)
                dados[
                    "servicos"
                    f"[{indice_servico}]arquivos[{indice_arquivo}]{chave}"
                ] = valor

    return getattr(cliente, metodo)(url, dados, format="multipart")


def test_seleciona_serializer_conforme_acao() -> None:
    """Usa um serializer resumido somente na listagem."""
    view = SolicitacaoManutencaoViewSet()
    view.action = "list"
    assert view.get_serializer_class() is SolicitacaoManutencaoListSerializer

    view.action = "solicitacao_ue"
    assert (
        view.get_serializer_class()
        is SolicitacaoManutencaoCriarEditarSerializer
    )

    view.action = "editar_solicitacao_ue"
    assert (
        view.get_serializer_class()
        is SolicitacaoManutencaoCriarEditarSerializer
    )

    view.action = "retrieve"
    assert (
        view.get_serializer_class() is SolicitacaoManutencaoDetalheSerializer
    )


def test_get_queryset_retorna_queryset_para_listagem(
    api_cliente_ue: APIClient,
) -> None:
    """Mantém queryset no contrato usado pela listagem e seus filtros."""
    requisicao = APIRequestFactory().get(URL_SOLICITACOES)
    view = SolicitacaoManutencaoViewSet()
    view.request = Request(requisicao)
    view.action = "list"

    assert isinstance(
        view.get_queryset(), type(SolicitacaoManutencao.objects.all())
    )


def test_lista_situacoes_da_solicitacao(api_cliente: APIClient) -> None:
    """Retorna os valores e rótulos das situações da solicitação."""
    resposta = api_cliente.get(URL_SITUACOES)

    assert resposta.status_code == status.HTTP_200_OK
    assert resposta.json()[0] == {
        "value": "nao_enviado_dre",
        "label": "Não enviada para a DRE",
    }
    assert len(resposta.json()) == 9


def test_lista_fases_da_solicitacao(api_cliente: APIClient) -> None:
    """Retorna os valores e rótulos das fases da solicitação."""
    resposta = api_cliente.get(URL_FASES)

    assert resposta.status_code == status.HTTP_200_OK
    assert resposta.json() == [
        {"value": "solicitacao", "label": "Solicitação"},
        {"value": "vistoria", "label": "Vistoria"},
        {"value": "execucao", "label": "Execução"},
    ]


def test_lista_tipos_atendimento(api_cliente: APIClient) -> None:
    """Retorna os valores e rótulos dos tipos de atendimento."""
    resposta = api_cliente.get(URL_TIPOS_ATENDIMENTO)

    assert resposta.status_code == status.HTTP_200_OK
    assert resposta.json() == [
        {"value": "comum", "label": "Comum"},
        {"value": "urgente", "label": "Urgente"},
    ]


def test_documenta_choices_da_solicitacao_no_schema() -> None:
    """Expõe no OpenAPI a consulta de cada escolha da solicitação."""
    resposta = APIClient().get("/api/v1/schema/?format=json")

    assert resposta.status_code == status.HTTP_200_OK
    operacoes = {
        url: resposta.json()["paths"][url]["get"]
        for url in (URL_SITUACOES, URL_FASES, URL_TIPOS_ATENDIMENTO)
    }
    assert operacoes[URL_SITUACOES]["operationId"] == (
        "listarSituacoesSolicitacaoManutencao"
    )
    assert operacoes[URL_FASES]["operationId"] == (
        "listarFasesSolicitacaoManutencao"
    )
    assert operacoes[URL_TIPOS_ATENDIMENTO]["operationId"] == (
        "listarTiposAtendimentoSolicitacaoManutencao"
    )
    assert all(
        set(operacao["responses"]) == {"200", "401", "500"}
        for operacao in operacoes.values()
    )


def test_lista_solicitacoes_paginadas(
    api_cliente_ue: APIClient,
    unidade_educacional_emef: Any,
    usuario_ue: Usuario,
    usuario_inativo: Usuario,
    historico_responsavel: HistoricoResponsavel,
) -> None:
    """Lista solicitações da unidade vinculada ao usuário autenticado."""
    usuario_ue.username = historico_responsavel.responsavel.registro_funcional
    usuario_ue.save(update_fields=["username"])
    solicitacao = SolicitacaoManutencao.objects.create(
        codigo="0000001",
        tipo_atendimento="urgente",
        unidade_educacional=unidade_educacional_emef,
        criado_por=usuario_ue,
    )
    SolicitacaoManutencao.objects.create(
        codigo="0000002",
        tipo_atendimento="comum",
        unidade_educacional=unidade_educacional_emef,
        criado_por=usuario_inativo,
    )

    resposta = api_cliente_ue.get(URL_SOLICITACOES)

    assert resposta.status_code == status.HTTP_200_OK
    assert resposta.json() == {
        "count": 2,
        "next": None,
        "previous": None,
        "results": [
            {
                "uuid": str(
                    SolicitacaoManutencao.objects.get(codigo="0000002").uuid
                ),
                "codigo": "0000002",
                "tipo_atendimento": "comum",
                "situacao": "nao_enviado_dre",
                "data_envio": None,
                "fase": "solicitacao",
            },
            {
                "uuid": str(solicitacao.uuid),
                "codigo": "0000001",
                "tipo_atendimento": "urgente",
                "situacao": "nao_enviado_dre",
                "data_envio": None,
                "fase": "solicitacao",
            },
        ],
    }


def test_busca_solicitacao_por_uuid(
    api_cliente_ue: APIClient,
    unidade_educacional_emef: Any,
    usuario_ue: Usuario,
    historico_responsavel: HistoricoResponsavel,
) -> None:
    """Retorna os dados completos da solicitação pelo UUID."""
    usuario_ue.username = historico_responsavel.responsavel.registro_funcional
    usuario_ue.save(update_fields=["username"])
    solicitacao = SolicitacaoManutencao.objects.create(
        codigo="0000003",
        tipo_atendimento="urgente",
        informacoes_adicionais="Reparo prioritário.",
        unidade_educacional=unidade_educacional_emef,
        criado_por=usuario_ue,
    )

    resposta = api_cliente_ue.get(URL_SOLICITACAO.format(solicitacao.uuid))

    assert resposta.status_code == status.HTTP_200_OK
    assert resposta.json() == {
        "uuid": str(solicitacao.uuid),
        "codigo": "0000003",
        "tipo_atendimento": "urgente",
        "informacoes_adicionais": "Reparo prioritário.",
        "unidade_educacional": {
            "id": unidade_educacional_emef.id,
            "uuid": str(unidade_educacional_emef.uuid),
            "codigo_eol": unidade_educacional_emef.codigo_eol,
            "nome": unidade_educacional_emef.nome,
            "diretoria_regional": {
                "id": unidade_educacional_emef.diretoria_regional.id,
                "nome_curto": (
                    unidade_educacional_emef.diretoria_regional.nome_curto
                ),
            },
            "tipo_escola": {
                "uuid": str(unidade_educacional_emef.tipo_escola.uuid),
                "sigla": unidade_educacional_emef.tipo_escola.sigla,
            },
            "subprefeitura": {
                "uuid": str(unidade_educacional_emef.subprefeitura.uuid),
                "nome": unidade_educacional_emef.subprefeitura.nome,
            },
            "lote": None,
            "status": unidade_educacional_emef.status,
            "dados": None,
            "responsaveis": [
                {
                    "uuid": str(historico_responsavel.responsavel.uuid),
                    "registro_funcional": (
                        historico_responsavel.responsavel.registro_funcional
                    ),
                    "nome": historico_responsavel.responsavel.nome,
                    "email": historico_responsavel.responsavel.email,
                    "telefone": historico_responsavel.responsavel.telefone,
                    "celular": historico_responsavel.responsavel.celular,
                    "cargo": {
                        "codigo": historico_responsavel.cargo.codigo,
                        "nome": historico_responsavel.cargo.nome,
                    },
                    "ativo": True,
                    "criado_pelo_sincronizador": False,
                }
            ],
        },
        "situacao": "nao_enviado_dre",
        "data_envio": None,
        "fase": "solicitacao",
        "servicos": [],
    }


def test_nao_busca_solicitacao_de_outra_ue(
    api_cliente_ue: APIClient,
    unidade_educacional_emef: Any,
    usuario_inativo: Usuario,
) -> None:
    """Oculta solicitação que não pertence ao usuário da UE autenticado."""
    solicitacao = SolicitacaoManutencao.objects.create(
        codigo="0000004",
        tipo_atendimento="comum",
        unidade_educacional=unidade_educacional_emef,
        criado_por=usuario_inativo,
    )

    resposta = api_cliente_ue.get(URL_SOLICITACAO.format(solicitacao.uuid))

    assert resposta.status_code == status.HTTP_404_NOT_FOUND


def test_edicao_retorna_404_para_solicitacao_invisivel(
    api_cliente_ue: APIClient,
) -> None:
    """Retorna 404 ao editar uma solicitação fora do escopo do usuário."""
    resposta = api_cliente_ue.put(
        URL_EDITAR_SOLICITACAO_UE.format(
            "00000000-0000-0000-0000-000000000000"
        ),
        {},
        format="json",
    )

    assert resposta.status_code == status.HTTP_404_NOT_FOUND


def test_edicao_rejeita_usuario_nao_identificado() -> None:
    """Rejeita atualização direta sem usuário autenticado identificado."""
    view = SolicitacaoManutencaoViewSet()
    view.request = Request(APIRequestFactory().put(URL_EDITAR_SOLICITACAO_UE))
    view.request.user = AnonymousUser()

    with pytest.raises(NotAuthenticated, match="Usuário não identificado"):
        view.editar_solicitacao_ue(
            view.request, "00000000-0000-0000-0000-000000000000"
        )


def test_busca_solicitacao_inexistente_por_uuid(
    api_cliente_ue: APIClient,
) -> None:
    """Retorna 404 quando não existe solicitação com o UUID informado."""
    resposta = api_cliente_ue.get(
        URL_SOLICITACAO.format("00000000-0000-0000-0000-000000000000")
    )

    assert resposta.status_code == status.HTTP_404_NOT_FOUND


def test_detalhes_rejeitam_servico_sem_arquivo(
    unidade_educacional_emef: Any,
    usuario_ativo: Usuario,
) -> None:
    """Rejeita serviço sem anexos ao validar a saída de detalhes."""
    solicitacao = SolicitacaoManutencao.objects.create(
        codigo="0000022",
        tipo_atendimento="comum",
        unidade_educacional=unidade_educacional_emef,
        criado_por=usuario_ativo,
    )
    ServicoManutencao.objects.create(
        solicitacao_manutencao=solicitacao,
        servico_especifico="Reparo",
        local_reparo="Sala",
        descricao="Descrição",
    )
    serializer_servico = ServicoManutencaoDetalhesSerializer()
    with pytest.raises(ValidationError, match="Informe ao menos um arquivo"):
        serializer_servico.validate_arquivos([])
    assert serializer_servico.validate_arquivos([{"uuid": "arquivo"}]) == [
        {"uuid": "arquivo"}
    ]


@pytest.mark.parametrize(
    ("parametros", "codigo_esperado"),
    [
        ({"codigo": "0002"}, "0000002"),
        ({"tipo_atendimento": "comum"}, "0000002"),
        ({"situacao": "aguardando_analise_dre"}, "0000002"),
    ],
)
def test_filtra_listagem_de_solicitacoes(
    api_cliente: APIClient,
    unidade_educacional_emef: Any,
    usuario_ativo: Usuario,
    parametros: dict[str, str],
    codigo_esperado: str,
    historico_responsavel: HistoricoResponsavel,
) -> None:
    """Filtra a listagem pelos dados da solicitação."""
    usuario_ativo.username = (
        historico_responsavel.responsavel.registro_funcional
    )
    usuario_ativo.save(update_fields=["username"])
    api_cliente.force_authenticate(user=usuario_ativo)
    SolicitacaoManutencao.objects.create(
        codigo="0000001",
        tipo_atendimento="urgente",
        unidade_educacional=unidade_educacional_emef,
        criado_por=usuario_ativo,
    )
    SolicitacaoManutencao.objects.create(
        codigo="0000002",
        tipo_atendimento="comum",
        unidade_educacional=unidade_educacional_emef,
        situacao="aguardando_analise_dre",
        criado_por=usuario_ativo,
    )

    resposta = api_cliente.get(URL_SOLICITACOES, parametros)

    assert resposta.status_code == status.HTTP_200_OK
    assert resposta.json()["count"] == 1
    assert resposta.json()["results"][0]["codigo"] == codigo_esperado


@pytest.mark.parametrize(
    ("campo", "valores"),
    [
        ("tipo_atendimento", "comum,urgente"),
        ("situacao", "nao_enviado_dre,aguardando_analise_dre"),
        ("fase", "solicitacao,vistoria"),
    ],
)
def test_filtra_listagem_de_solicitacoes_por_multiplos_valores(
    api_cliente: APIClient,
    unidade_educacional_emef: Any,
    usuario_ativo: Usuario,
    campo: str,
    valores: str,
    historico_responsavel: HistoricoResponsavel,
) -> None:
    """Filtra a listagem por múltiplos valores do mesmo campo."""
    usuario_ativo.username = (
        historico_responsavel.responsavel.registro_funcional
    )
    usuario_ativo.save(update_fields=["username"])
    api_cliente.force_authenticate(user=usuario_ativo)
    SolicitacaoManutencao.objects.create(
        codigo="0000001",
        tipo_atendimento="urgente",
        unidade_educacional=unidade_educacional_emef,
        criado_por=usuario_ativo,
    )
    SolicitacaoManutencao.objects.create(
        codigo="0000002",
        tipo_atendimento="comum",
        unidade_educacional=unidade_educacional_emef,
        situacao="aguardando_analise_dre",
        fase="vistoria",
        criado_por=usuario_ativo,
    )

    resposta = api_cliente.get(URL_SOLICITACOES, {campo: valores})

    assert resposta.status_code == status.HTTP_200_OK
    assert resposta.json()["count"] == 2


def test_filtra_listagem_por_intervalo_de_data_envio(
    api_cliente: APIClient,
    unidade_educacional_emef: Any,
    usuario_ativo: Usuario,
    historico_responsavel: HistoricoResponsavel,
) -> None:
    """Filtra solicitações cuja data de envio esteja no intervalo."""
    usuario_ativo.username = (
        historico_responsavel.responsavel.registro_funcional
    )
    usuario_ativo.save(update_fields=["username"])
    api_cliente.force_authenticate(user=usuario_ativo)
    for codigo, data_envio in (
        ("0000001", datetime(2026, 10, 9, 23, 59)),
        ("0000002", datetime(2026, 10, 10, 12)),
        ("0000003", datetime(2026, 10, 20, 23, 59)),
        ("0000004", datetime(2026, 10, 21)),
    ):
        SolicitacaoManutencao.objects.create(
            codigo=codigo,
            tipo_atendimento="comum",
            unidade_educacional=unidade_educacional_emef,
            data_envio=timezone.make_aware(data_envio),
            criado_por=usuario_ativo,
        )

    resposta = api_cliente.get(
        URL_SOLICITACOES,
        {
            "data_envio_after": "2026-10-10",
            "data_envio_before": "2026-10-20",
        },
    )

    assert resposta.status_code == status.HTTP_200_OK
    assert resposta.json()["count"] == 2
    assert {item["codigo"] for item in resposta.json()["results"]} == {
        "0000002",
        "0000003",
    }


def test_listagem_de_solicitacoes_exige_autenticacao() -> None:
    """Protege a listagem contra acesso não autenticado."""
    resposta = APIClient().get(URL_SOLICITACOES)

    assert resposta.status_code == status.HTTP_401_UNAUTHORIZED


def test_documenta_listagem_de_solicitacoes_no_schema() -> None:
    """Expõe a listagem paginada e seus filtros no OpenAPI."""
    resposta = APIClient().get("/api/v1/schema/?format=json")

    assert resposta.status_code == status.HTTP_200_OK
    operacao = resposta.json()["paths"][URL_SOLICITACOES]["get"]
    assert operacao["operationId"] == "listarSolicitacoesManutencao"
    assert operacao["summary"] == "Lista as solicitações de manutenção"
    assert {parametro["name"] for parametro in operacao["parameters"]} >= {
        "codigo",
        "tipo_atendimento",
        "situacao",
        "fase",
        "data_envio_after",
        "data_envio_before",
    }
    assert set(operacao["responses"]) == {"200", "401", "500"}


def test_requisicao_nao_autenticada_retorna_401(
    solicitacao_payload: dict[str, Any],
) -> None:
    """Rejeita a criação sem autenticação."""
    resposta = APIClient().post(
        URL_SOLICITACAO_UE,
        solicitacao_payload,
        format="json",
    )

    assert resposta.status_code == status.HTTP_401_UNAUTHORIZED


def test_solicitacao_ue_rejeita_usuario_nao_identificado() -> None:
    """Impede a criação quando a requisição não identifica um usuário."""
    requisicao = Request(APIRequestFactory().post(URL_SOLICITACAO_UE))
    requisicao.user = AnonymousUser()
    view = SolicitacaoManutencaoViewSet()
    view.request = requisicao

    with pytest.raises(NotAuthenticated, match="Usuário não identificado"):
        SolicitacaoManutencaoViewSet.solicitacao_ue(view, requisicao)


def test_documenta_criacao_da_solicitacao_no_schema() -> None:
    """Expõe no OpenAPI os detalhes da criação da solicitação."""
    resposta = APIClient().get("/api/v1/schema/?format=json")

    assert resposta.status_code == status.HTTP_200_OK
    operacao = resposta.json()["paths"][
        "/api/v1/solicitacoes-manutencao/solicitacao-ue/"
    ]["post"]
    assert operacao["operationId"] == "criarSolicitacaoManutencao"
    assert operacao["summary"] == "Cria uma solicitação de manutenção"
    assert operacao["parameters"][0]["name"] == "enviar"
    assert set(operacao["responses"]) == {"201", "400", "401", "500"}


def test_documenta_edicao_da_solicitacao_no_schema() -> None:
    """Expõe no OpenAPI a rota de edição e seu parâmetro de envio."""
    resposta = APIClient().get("/api/v1/schema/?format=json")

    assert resposta.status_code == status.HTTP_200_OK
    operacao = resposta.json()["paths"][
        "/api/v1/solicitacoes-manutencao/editar-solicitacao-ue/{uuid}/"
    ]["put"]
    assert operacao["operationId"] == "editarSolicitacaoManutencao"
    assert operacao["summary"] == "Edita uma solicitação de manutenção"
    assert any(
        parametro["name"] == "enviar" for parametro in operacao["parameters"]
    )
    assert set(operacao["responses"]) == {"200", "400", "401", "404", "500"}


def test_cria_solicitacao_com_servicos(
    api_cliente: APIClient,
    solicitacao_payload: dict[str, Any],
    usuario_ativo: Usuario,
) -> None:
    """Cria a solicitação e seus serviços em uma única requisição."""
    resposta = _postar_solicitacao(
        api_cliente,
        f"{URL_SOLICITACAO_UE}?enviar=true",
        solicitacao_payload,
    )

    assert resposta.status_code == status.HTTP_201_CREATED, resposta.json()
    solicitacao = SolicitacaoManutencao.objects.get(codigo="0000001")
    assert solicitacao.criado_por == usuario_ativo
    assert solicitacao.solicitante == "ue"
    assert solicitacao.data_envio is not None
    assert solicitacao.servicos_manutencao.count() == 1
    assert solicitacao.servicos_manutencao.get().criado_por == usuario_ativo
    assert resposta.json()["servicos"][0]["local_reparo"] == "Cozinha"
    assert len(resposta.json()["servicos"][0]["arquivos"]) == 1


def test_cria_solicitacao_sem_enviar_para_dre(
    api_cliente: APIClient,
    solicitacao_payload: dict[str, Any],
) -> None:
    """Mantém a solicitação sem envio quando o parâmetro não é informado."""
    resposta = _postar_solicitacao(
        api_cliente,
        URL_SOLICITACAO_UE,
        solicitacao_payload,
    )

    assert resposta.status_code == status.HTTP_201_CREATED
    solicitacao = SolicitacaoManutencao.objects.get(codigo="0000001")
    assert solicitacao.situacao == "nao_enviado_dre"
    assert solicitacao.data_envio is None


def test_exige_ao_menos_um_servico(
    api_cliente: APIClient,
    solicitacao_payload: dict[str, Any],
) -> None:
    """Não cria uma solicitação sem serviços de manutenção."""
    solicitacao_payload["servicos"] = []

    resposta = _postar_solicitacao(
        api_cliente,
        URL_SOLICITACAO_UE,
        solicitacao_payload,
    )

    assert resposta.status_code == status.HTTP_400_BAD_REQUEST
    assert SolicitacaoManutencao.objects.count() == 0


def test_exige_arquivos_em_cada_servico(
    api_cliente: APIClient,
    solicitacao_payload: dict[str, Any],
) -> None:
    """Não cria uma solicitação quando arquivos não são informados."""
    solicitacao_payload["servicos"][0].pop("arquivos")

    resposta = _postar_solicitacao(
        api_cliente,
        URL_SOLICITACAO_UE,
        solicitacao_payload,
    )
    assert resposta.status_code == status.HTTP_400_BAD_REQUEST
    erro_arquivos = resposta.json()["servicos"]["0"]["arquivos"]
    assert erro_arquivos == ["Este campo é obrigatório."]
    assert SolicitacaoManutencao.objects.count() == 0


def test_cria_solicitacao_sem_servico_catalogado(
    api_cliente: APIClient,
    solicitacao_payload: dict[str, Any],
) -> None:
    """Cria uma solicitação sem vincular um serviço catalogado."""
    dados_servico = solicitacao_payload["servicos"][0]
    dados_servico.pop("servico")
    dados_servico["servico_especifico"] = "Troca de disjuntor"

    resposta = _postar_solicitacao(
        api_cliente,
        URL_SOLICITACAO_UE,
        solicitacao_payload,
    )

    assert resposta.status_code == status.HTTP_201_CREATED
    solicitacao = SolicitacaoManutencao.objects.get(codigo="0000001")
    assert solicitacao.servicos_manutencao.get().servico is None


def test_edita_solicitacao_ue(
    api_cliente: APIClient,
    solicitacao_payload: dict[str, Any],
    usuario_ue: Usuario,
    historico_responsavel: HistoricoResponsavel,
) -> None:
    """Atualiza dados e serviços de uma solicitação existente."""
    usuario_ue.username = historico_responsavel.responsavel.registro_funcional
    usuario_ue.save(update_fields=["username"])
    api_cliente.force_authenticate(user=usuario_ue)
    resposta_criacao = _postar_solicitacao(
        api_cliente, URL_SOLICITACAO_UE, solicitacao_payload
    )
    uuid = resposta_criacao.json()["uuid"]
    payload_edicao = dict(solicitacao_payload)
    payload_edicao["informacoes_adicionais"] = "Atualização necessária."
    payload_edicao["servicos"] = [dict(solicitacao_payload["servicos"][0])]
    payload_edicao["servicos"][0]["uuid"] = resposta_criacao.json()[
        "servicos"
    ][0]["uuid"]
    payload_edicao["servicos"][0]["local_reparo"] = "Sala de aula"
    payload_edicao["servicos"][0]["arquivos"] = [
        {
            "uuid": resposta_criacao.json()["servicos"][0]["arquivos"][0][
                "uuid"
            ],
            "arquivo": SimpleUploadedFile(
                "reparo.jpg", b"conteudo", content_type="image/jpeg"
            ),
        }
    ]

    resposta = _postar_solicitacao(
        api_cliente,
        URL_EDITAR_SOLICITACAO_UE.format(uuid),
        payload_edicao,
        metodo="put",
    )

    assert resposta.status_code == status.HTTP_200_OK, resposta.json()
    solicitacao = SolicitacaoManutencao.objects.get(uuid=uuid)
    assert solicitacao.informacoes_adicionais == "Atualização necessária."
    assert solicitacao.servicos_manutencao.count() == 1
    assert solicitacao.servicos_manutencao.get().local_reparo == "Sala de aula"


def test_edicao_retorna_erro_quando_servico_nao_pertence_a_solicitacao(
    api_cliente: APIClient,
    unidade_educacional_emef: Any,
    usuario_ue: Usuario,
    historico_responsavel: HistoricoResponsavel,
) -> None:
    """Converte ValidationError do serviço em resposta HTTP 400."""
    usuario_ue.username = historico_responsavel.responsavel.registro_funcional
    usuario_ue.save(update_fields=["username"])
    api_cliente.force_authenticate(user=usuario_ue)
    solicitacao = SolicitacaoManutencao.objects.create(
        codigo="0000020",
        tipo_atendimento="comum",
        unidade_educacional=unidade_educacional_emef,
        criado_por=usuario_ue,
    )
    payload = {
        "tipo_atendimento": "comum",
        "informacoes_adicionais": "",
        "unidade_educacional": str(unidade_educacional_emef.uuid),
        "servicos": [
            {
                "uuid": "00000000-0000-0000-0000-000000000001",
                "servico_especifico": "Reparo",
                "local_reparo": "Sala",
                "descricao": "Descrição",
                "arquivos": [
                    {
                        "uuid": "00000000-0000-0000-0000-000000000002",
                        "arquivo": SimpleUploadedFile(
                            "reparo.jpg",
                            b"conteudo",
                            content_type="image/jpeg",
                        ),
                    }
                ],
            }
        ],
    }

    resposta = _postar_solicitacao(
        api_cliente,
        URL_EDITAR_SOLICITACAO_UE.format(solicitacao.uuid),
        payload,
        metodo="put",
    )

    assert resposta.status_code == status.HTTP_400_BAD_REQUEST
    assert resposta.json()["servicos"] == [
        "Serviço não encontrado na solicitação."
    ]


def test_edicao_retorna_erro_quando_anexo_e_muito_grande(
    api_cliente: APIClient,
    unidade_educacional_emef: Any,
    usuario_ue: Usuario,
    historico_responsavel: HistoricoResponsavel,
) -> None:
    """Converte AnexoArquivoError em resposta HTTP 400."""
    usuario_ue.username = historico_responsavel.responsavel.registro_funcional
    usuario_ue.save(update_fields=["username"])
    api_cliente.force_authenticate(user=usuario_ue)
    solicitacao = SolicitacaoManutencao.objects.create(
        codigo="0000021",
        tipo_atendimento="comum",
        unidade_educacional=unidade_educacional_emef,
        criado_por=usuario_ue,
    )
    payload = {
        "tipo_atendimento": "comum",
        "informacoes_adicionais": "",
        "unidade_educacional": str(unidade_educacional_emef.uuid),
        "servicos": [
            {
                "servico_especifico": "Reparo",
                "local_reparo": "Sala",
                "descricao": "Descrição",
                "arquivos": [
                    {
                        "arquivo": SimpleUploadedFile(
                            "grande.jpg",
                            b"x" * (2 * 1024 * 1024 + 1),
                            content_type="image/jpeg",
                        )
                    }
                ],
            }
        ],
    }

    resposta = _postar_solicitacao(
        api_cliente,
        URL_EDITAR_SOLICITACAO_UE.format(solicitacao.uuid),
        payload,
        metodo="put",
    )

    assert resposta.status_code == status.HTTP_400_BAD_REQUEST
    assert resposta.json()["title"] == "Arquivo muito grande"


def test_perfil_ue_pode_listar_servicos(api_cliente_perfil):
    """Permite que usuários UE listem serviços."""
    resposta = api_cliente_perfil(PerfilAcesso.UE).get("/api/v1/servicos/")

    assert resposta.status_code == status.HTTP_200_OK


@pytest.mark.parametrize(
    "perfil",
    [
        PerfilAcesso.DRE,
        PerfilAcesso.EMPRESA,
        None,
    ],
)
def test_demais_perfis_nao_podem_listar_servicos(api_cliente_perfil, perfil):
    """Bloqueia a listagem para perfis sem permissão de acesso."""
    resposta = api_cliente_perfil(perfil).get("/api/v1/servicos/")

    assert resposta.status_code == status.HTTP_403_FORBIDDEN
