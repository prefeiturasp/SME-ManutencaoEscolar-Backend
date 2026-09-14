"""Comando para inativação automática de lotes vencidos."""

import logging
from typing import Any

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.lote.models import Lote

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Inativa os lotes cujo prazo da licitação terminou."""

    help = "Inativa lotes cujo período final já terminou."

    def handle(self, *args: Any, **options: Any) -> None:
        logger.info("Iniciando a validação das datas de vigência do lote.")

        data_atual = timezone.localdate()

        data_formatada = data_atual.strftime("%d/%m/%Y")

        lotes = Lote.objects.filter(
            status=True, periodo_final__lt=data_atual, deletado_em__isnull=True
        )

        logger.info(
            f"{lotes.count()} lotes foram encontrados com data de "
            f"licitação expiradas em {data_formatada}."
        )

        for lote in lotes:
            logger.info(
                f"O lote {lote.nome} de codigo {lote.codigo_cadastro} "
                "chegou ao final da data de licitação."
            )

            lote.status = False
            lote.save()

        logger.info("Verificaçao concluida")
