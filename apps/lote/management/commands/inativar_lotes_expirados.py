"""Comando para inativação automática de lotes vencidos."""

from typing import Any

from django.core.management.base import BaseCommand

from apps.lote.services.lote_service import LoteService


class Command(BaseCommand):
    """Inativa os lotes cujo prazo da licitação terminou."""

    def handle(self, *args: Any, **options: Any) -> None:
        LoteService().inativar_lotes_com_prazo_finalizado()
