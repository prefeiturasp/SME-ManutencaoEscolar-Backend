"""Notificações por e-mail das solicitações de manutenção."""

import logging
from typing import Any

from django.conf import settings
from django.utils import timezone

from apps.core.services.email_service import EmailService
from apps.solicitacao_manutencao.constants import (
    ROTA_VISUALIZAR_SOLICITACAO,
    TipoAtendimento,
)
from apps.usuarios.models import Usuario
from apps.usuarios.repository.usuario_repository import UsuarioRepository

logger = logging.getLogger(__name__)


class NotificacaoSolicitacaoService:
    """Envia e-mails sobre o andamento das solicitações de manutenção."""

    template_envio_dre = "solicitacao_manutencao/solicitacao_enviada_dre.html"

    def __init__(
        self,
        usuario_repository: type[UsuarioRepository] | None = None,
        email_service: type[EmailService] | None = None,
    ) -> None:
        """Inicializa o serviço com suas dependências.

        Args:
            usuario_repository: Repositório de usuários.
            email_service: Serviço de envio de e-mails.
        """
        self.usuario_repository = usuario_repository or UsuarioRepository
        self.email_service = email_service or EmailService

    def notificar_envio_para_dre(
        self, solicitacao: dict[str, Any], solicitante: Usuario
    ) -> None:
        """Avisa os gestores da DRE sobre uma solicitação enviada para análise.

        Cada gestor com e-mail cadastrado recebe uma mensagem própria. Uma
        falha no envio para um gestor é registrada e não impede o envio aos
        demais nem interrompe o fluxo de quem enviou a solicitação.

        Args:
            solicitacao: Dados da solicitação enviada.
            solicitante: Usuário da UE que enviou a solicitação.
        """
        unidade = solicitacao["unidade_educacional"]
        gestores = self.usuario_repository.listar_gestores_dre(
            unidade.diretoria_regional_id
        )
        if not gestores:
            logger.warning(
                "Nenhum gestor de DRE com e-mail para a solicitação '%s'.",
                solicitacao["codigo"],
            )
            return

        tipo = TipoAtendimento(solicitacao["tipo_atendimento"]).label
        assunto = (
            "Nova Solicitação de Manutenção Escolar "
            f"nº {solicitacao['codigo']} - {tipo}"
        )
        data_envio = timezone.localtime(solicitacao["data_envio"])
        for gestor in gestores:
            contexto = {
                "nome_responsavel": gestor["nome"],
                "rf_responsavel": gestor["registro_funcional"],
                "numero": solicitacao["codigo"],
                "tipo": tipo,
                "unidade": unidade.nome,
                "solicitante": solicitante.nome,
                "rf_solicitante": solicitante.registro_funcional,
                "data": data_envio.strftime("%d/%m/%Y"),
                "hora": data_envio.strftime("%H:%M"),
                "url": self._montar_url(solicitacao["uuid"]),
            }
            try:
                self.email_service.enviar(
                    assunto=assunto,
                    template=self.template_envio_dre,
                    contexto=contexto,
                    destinatarios=[gestor["email"]],
                )
            except Exception:
                logger.exception(
                    "Erro ao enviar e-mail da solicitação '%s' para '%s'.",
                    solicitacao["codigo"],
                    gestor["email"],
                )

    @staticmethod
    def _montar_url(uuid: object) -> str:
        """Monta o link de visualização da solicitação no frontend."""
        base = (settings.FRONTEND_URL or "").rstrip("/")
        return base + ROTA_VISUALIZAR_SOLICITACAO.format(uuid=uuid)
