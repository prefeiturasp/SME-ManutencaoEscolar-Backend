"""Testes das notificações por e-mail das solicitações."""

from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock

import pytest
from django.template.loader import render_to_string
from django.test import override_settings
from django.utils import timezone

from apps.escola.models import DiretoriaRegional, Unidadeeducacional
from apps.solicitacao_manutencao.models import SolicitacaoManutencao
from apps.solicitacao_manutencao.services import notificacao_service
from apps.solicitacao_manutencao.services.notificacao_service import (
    NotificacaoSolicitacaoService,
)
from apps.solicitacao_manutencao.services.ue_services import (
    SolicitacaoManutencaoUeService,
)
from apps.usuarios.constants import PerfilAcesso
from apps.usuarios.models import CargoEOL, Usuario

pytestmark = pytest.mark.django_db

TEMPLATE = "solicitacao_manutencao/solicitacao_enviada_dre.html"


@pytest.fixture
def gestor_dre(
    diretoria_regional_centro: DiretoriaRegional,
) -> Usuario:
    """Cria um gestor de DRE com e-mail na DRE da unidade de teste."""
    cargo = CargoEOL.objects.create(
        codigo="7001", nome="Gestor DRE", perfil=PerfilAcesso.DRE
    )
    return Usuario.objects.create(
        username="1234567",
        registro_funcional="1234567",
        nome="Ana Gestora",
        email="ana.gestora@dre.com",
        cargo=cargo,
        diretoria_regional=diretoria_regional_centro,
    )


@pytest.fixture
def solicitacao(
    unidade_educacional_emef: Unidadeeducacional, usuario_ue: Usuario
) -> Callable[..., dict[str, Any]]:
    """Fábrica de solicitações enviadas, no formato retornado pelo serviço."""

    def _criar(tipo: str = "comum") -> dict[str, Any]:
        instancia = SolicitacaoManutencao.objects.create(
            codigo="0000007",
            tipo_atendimento=tipo,
            unidade_educacional=unidade_educacional_emef,
            situacao="aguardando_analise_dre",
            data_envio=timezone.now(),
            criado_por=usuario_ue,
        )
        return {
            "uuid": instancia.uuid,
            "codigo": instancia.codigo,
            "tipo_atendimento": instancia.tipo_atendimento,
            "unidade_educacional": unidade_educacional_emef,
            "data_envio": instancia.data_envio,
        }

    return _criar


@pytest.fixture
def email_service() -> MagicMock:
    """Dublê do serviço de envio de e-mails."""
    return MagicMock()


def _service(email_service: MagicMock) -> NotificacaoSolicitacaoService:
    return NotificacaoSolicitacaoService(email_service=email_service)


@override_settings(FRONTEND_URL="https://comapre.exemplo.gov.br/")
def test_envia_e_mail_para_cada_gestor_da_dre(
    gestor_dre: Usuario,
    solicitacao: Callable[..., dict[str, Any]],
    usuario_ue: Usuario,
    email_service: MagicMock,
) -> None:
    """Envia a cada gestor um e-mail com os dados da solicitação."""
    dados = solicitacao()

    _service(email_service).notificar_envio_para_dre(dados, usuario_ue)

    email_service.enviar.assert_called_once()
    chamada = email_service.enviar.call_args.kwargs
    assert chamada["assunto"] == (
        "Nova Solicitação de Manutenção Escolar nº 0000007 - Comum"
    )
    assert chamada["template"] == TEMPLATE
    assert chamada["destinatarios"] == ["ana.gestora@dre.com"]
    data_envio = timezone.localtime(dados["data_envio"])
    assert chamada["contexto"] == {
        "nome_responsavel": "Ana Gestora",
        "rf_responsavel": "1234567",
        "numero": "0000007",
        "tipo": "Comum",
        "unidade": "EMEF ESCOLA TESTE",
        "solicitante": usuario_ue.nome,
        "rf_solicitante": usuario_ue.registro_funcional,
        "data": data_envio.strftime("%d/%m/%Y"),
        "hora": data_envio.strftime("%H:%M"),
        "url": (
            "https://comapre.exemplo.gov.br"
            f"/solicitacao_manutencao/visualizar/{dados['uuid']}"
        ),
    }


def test_assunto_acompanha_o_tipo_da_solicitacao(
    gestor_dre: Usuario,
    solicitacao: Callable[..., dict[str, Any]],
    usuario_ue: Usuario,
    email_service: MagicMock,
) -> None:
    """Informa o tipo Urgente no assunto do e-mail."""
    _service(email_service).notificar_envio_para_dre(
        solicitacao("urgente"), usuario_ue
    )

    assunto = email_service.enviar.call_args.kwargs["assunto"]
    assert assunto.endswith("nº 0000007 - Urgente")


def test_nao_envia_quando_a_dre_nao_tem_gestores(
    solicitacao: Callable[..., dict[str, Any]],
    usuario_ue: Usuario,
    email_service: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Registra um aviso e não envia nada sem gestores elegíveis."""
    logger = MagicMock()
    monkeypatch.setattr(notificacao_service, "logger", logger)

    _service(email_service).notificar_envio_para_dre(solicitacao(), usuario_ue)

    email_service.enviar.assert_not_called()
    logger.warning.assert_called_once()


def test_falha_em_um_envio_nao_impede_os_demais(
    gestor_dre: Usuario,
    diretoria_regional_centro: DiretoriaRegional,
    solicitacao: Callable[..., dict[str, Any]],
    usuario_ue: Usuario,
    email_service: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Segue enviando aos outros gestores quando um envio falha."""
    logger = MagicMock()
    monkeypatch.setattr(notificacao_service, "logger", logger)
    Usuario.objects.create(
        username="7654321",
        nome="Bia Gestora",
        email="bia.gestora@dre.com",
        cargo=gestor_dre.cargo,
        diretoria_regional=diretoria_regional_centro,
    )
    email_service.enviar.side_effect = [RuntimeError("broker fora"), None]

    _service(email_service).notificar_envio_para_dre(solicitacao(), usuario_ue)

    assert email_service.enviar.call_count == 2
    logger.exception.assert_called_once()


@override_settings(FRONTEND_URL="")
def test_url_sem_frontend_configurado_mantem_a_rota() -> None:
    """Gera apenas a rota quando FRONTEND_URL não está definida."""
    url = NotificacaoSolicitacaoService._montar_url("abc")

    assert url == "/solicitacao_manutencao/visualizar/abc"


def test_template_exibe_os_dados_e_o_botao() -> None:
    """Renderiza o corpo do e-mail conforme a história."""
    html = render_to_string(
        TEMPLATE,
        {
            "nome_responsavel": "Ana Gestora",
            "rf_responsavel": "1234567",
            "numero": "0000007",
            "tipo": "Urgente",
            "unidade": "EMEF ESCOLA TESTE",
            "solicitante": "Maria Diretora",
            "rf_solicitante": "7654321",
            "data": "06/11/2026",
            "hora": "09:15",
            "url": "https://exemplo.gov.br/visualizar/1",
        },
    )

    assert "Prezado(a) Ana Gestora - RF1234567," in html
    assert "Número da Solicitação:</strong> 0000007" in html
    assert "Grau de Urgência:</strong> Urgente" in html
    assert "Unidade Escolar (UE):</strong> EMEF ESCOLA TESTE" in html
    assert "Maria Diretora - RF 7654321" in html
    assert "Data de envio:</strong> 06/11/2026" in html
    assert "Hora:</strong> 09:15" in html
    assert 'href="https://exemplo.gov.br/visualizar/1"' in html
    assert ">AQUI</a>" in html
    assert "Sistema Manutenção Escolar" in html
    assert "Mensagem automática. Por favor, não responda" in html


def test_template_omite_rf_quando_nao_informado() -> None:
    """Não exibe o RF de quem não possui registro funcional."""
    html = render_to_string(
        TEMPLATE,
        {
            "nome_responsavel": "Ana Gestora",
            "rf_responsavel": None,
            "solicitante": "Maria Diretora",
            "rf_solicitante": None,
        },
    )

    assert "Prezado(a) Ana Gestora," in html
    assert "Maria Diretora</li>" in html
    assert "RF" not in html


def test_envio_da_solicitacao_notifica_apos_o_commit(
    unidade_educacional_emef: Unidadeeducacional,
    usuario_ue: Usuario,
    django_capture_on_commit_callbacks: Any,
) -> None:
    """Dispara o aviso somente depois que a transação é confirmada."""
    notificacao = MagicMock()
    service = SolicitacaoManutencaoUeService(notificacao_service=notificacao)

    with django_capture_on_commit_callbacks(execute=False) as callbacks:
        resultado = service.criar(
            {
                "tipo_atendimento": "comum",
                "unidade_educacional": unidade_educacional_emef,
                "servicos": [],
            },
            usuario_ue,
            enviar=True,
        )

    notificacao.notificar_envio_para_dre.assert_not_called()
    assert len(callbacks) == 1
    callbacks[0]()
    notificacao.notificar_envio_para_dre.assert_called_once_with(
        resultado, usuario_ue
    )


def test_rascunho_nao_notifica_a_dre(
    unidade_educacional_emef: Unidadeeducacional,
    usuario_ue: Usuario,
    django_capture_on_commit_callbacks: Any,
) -> None:
    """Não avisa a DRE quando a solicitação não é enviada."""
    notificacao = MagicMock()
    service = SolicitacaoManutencaoUeService(notificacao_service=notificacao)

    with django_capture_on_commit_callbacks(execute=True) as callbacks:
        service.criar(
            {
                "tipo_atendimento": "comum",
                "unidade_educacional": unidade_educacional_emef,
                "servicos": [],
            },
            usuario_ue,
        )

    assert callbacks == []
    notificacao.notificar_envio_para_dre.assert_not_called()
