"""Configuração do app Equipe."""

from django.apps import AppConfig


class EquipeConfig(AppConfig):
    """Configura o domínio de equipes."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.equipe"
