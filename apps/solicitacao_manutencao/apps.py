"""Configuração da aplicação Solicitação de Manutenção."""

from django.apps import AppConfig


class SolicitacaoManutencaoConfig(AppConfig):
    """Configura o domínio de solicitações de manutenção."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.solicitacao_manutencao"
    verbose_name = "Solicitações de manutenção"
