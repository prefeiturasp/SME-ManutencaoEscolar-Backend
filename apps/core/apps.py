"""Configuração da aplicação Core."""

from django.apps import AppConfig
from sme_workflow_sdk import configure

from config import settings


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"

    def ready(self) -> None:
        """Inicializa o SDK de workflow."""
        configure(settings.WORKFLOW_CONFIG_PATH)
