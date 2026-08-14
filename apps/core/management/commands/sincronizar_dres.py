"""Comando para sincronizar as Diretorias Regionais de Educação (DREs)."""

from __future__ import annotations

import logging

import requests
from django.core.management.base import BaseCommand, CommandError

from apps.core.models import DiretoriaRegional as Dre
from config.settings import SME_API_EOL_TOKEN, SME_API_EOL_URL

logger = logging.getLogger(__name__)

TIMEOUT = 30


class Command(BaseCommand):
    """Sincroniza as Diretorias Regionais utilizando a API externa."""

    def handle(self, *args: object, **options: object) -> None:
        """Executa a sincronização."""
        base_url = (SME_API_EOL_URL or "").strip()
        token = (SME_API_EOL_TOKEN or "").strip()

        if not base_url or not token:
            raise CommandError(
                """As variáveis SME_API_EOL_URL
                e SME_API_EOL_TOKEN devem estar configuradas."""
            )

        api_url = base_url.rstrip("/") + "/abrangencia/nome-abreviacao-dres"

        headers = {
            "x-api-eol-key": token,
            "accept": "text/plain",
        }

        try:
            response = requests.get(
                api_url,
                headers=headers,
                timeout=TIMEOUT,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise CommandError(f"Erro ao consultar a API: {exc}") from exc

        dados = response.json()

        if not isinstance(dados, list):
            raise CommandError("A API retornou um formato inválido.")

        criadas = 0
        atualizadas = 0

        for item in dados:
            self.stdout.write(f"Processando DRE: {item}")
            codigo = (item.get("codigo") or "").strip()

            if not codigo:
                logger.warning(
                    "Registro ignorado por não possuir código: %s", item
                )
                continue

            _, created = Dre.objects.update_or_create(
                codigo=codigo,
                defaults={
                    "nome": (item.get("nome") or "").strip(),
                    "abreviacao": (item.get("abreviacao") or "").strip(),
                },
            )

            if created:
                criadas += 1
            else:
                atualizadas += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Sincronização concluída: {criadas} criada(s) "
                f"e {atualizadas} atualizada(s)."
            )
        )
