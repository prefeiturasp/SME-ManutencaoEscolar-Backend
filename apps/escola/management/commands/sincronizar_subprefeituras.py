"""sumarry."""

from __future__ import annotations

import logging
from typing import Any

import requests
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.core.constants import TIMEOUT_DEFAULT
from apps.escola.constants import ENDPOINT_SUBPREFEITURA
from apps.escola.models import DiretoriaRegional, Subprefeitura
from config.settings import SME_API_EOL_TOKEN, SME_API_EOL_URL

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Sincroniza as Subprefeituras com os dados da API EOL.

    Para cada Diretoria Regional cadastrada no banco, o comando consulta
    a API EOL para obter as Subprefeituras relacionadas à DRE.

    Os registros são criados ou atualizados utilizando o código da
    Subprefeitura como identificador.
    """

    def handle(self, *args: Any, **options: Any) -> None:
        """Executa a sincronização das Subprefeituras."""
        base_url = (SME_API_EOL_URL or "").strip()
        token = (SME_API_EOL_TOKEN or "").strip()

        if not base_url or not token:
            raise CommandError(
                """As variáveis SME_API_EOL_URL
                e SME_API_EOL_TOKEN devem estar configuradas."""
            )

        headers = {
            "accept": "application/json",
            "x-api-eol-key": token,
        }

        diretorias = DiretoriaRegional.objects.all()

        if not diretorias.exists():
            raise CommandError(
                "Nenhuma Diretoria Regional cadastrada. "
                "Execute primeiro a sincronização das DREs."
            )

        quantidade_criadas = 0
        quantidade_atualizadas = 0

        logger.info("Iniciando importação das Subprefeituras.")

        with transaction.atomic():
            for dre in diretorias:
                logger.info(
                    f"Consultando Subprefeituras da {dre.nome}.",
                )

                subprefeituras = self._obter_subprefeituras(
                    base_url=base_url,
                    headers=headers,
                    codigo_dre=dre.codigo,
                )

                for item in subprefeituras:
                    self._validar_registro(item)

                    codigo = item["codigoSubprefeitura"]
                    nome = item["nomeSubprefeitura"]

                    _, foi_criada = Subprefeitura.objects.update_or_create(
                        codigo_eol=codigo,
                        defaults={
                            "nome": nome,
                        },
                    )

                    if foi_criada:
                        quantidade_criadas += 1
                    else:
                        quantidade_atualizadas += 1

        logger.info(
            "Importação concluída: %d criadas, %d atualizadas.",
            quantidade_criadas,
            quantidade_atualizadas,
        )

    @staticmethod
    def _obter_subprefeituras(
        base_url: str,
        headers: dict[str, str],
        codigo_dre: str,
    ) -> list[dict[str, Any]]:
        """Consulta as Subprefeituras relacionadas a uma DRE."""
        endpoint = ENDPOINT_SUBPREFEITURA.format(
            codigo_dre=codigo_dre,
        )

        api_url = f"{base_url}{endpoint}"
        params = {
            "codigoEolDRE": codigo_dre,
        }
        try:
            response = requests.get(
                api_url,
                headers=headers,
                params=params,
                timeout=TIMEOUT_DEFAULT,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            logger.exception(
                f"Erro ao consultar Subprefeituras da DRE {codigo_dre}."
            )
            raise CommandError(
                f"Erro ao consultar Subprefeituras da DRE {codigo_dre}: {exc}"
            ) from exc

        try:
            payload = response.json()
        except ValueError as exc:
            raise CommandError(
                "A API de Subprefeituras retornou um JSON inválido "
                f"para a DRE {codigo_dre}."
            ) from exc

        if not isinstance(payload, list):
            raise CommandError(
                "A API de Subprefeituras deveria retornar uma lista "
                f"para a DRE {codigo_dre}."
            )

        return payload

    @staticmethod
    def _validar_registro(item: Any) -> None:
        """Valida a estrutura e os tipos de um registro."""
        if not isinstance(item, dict):
            raise CommandError(
                "Um dos registros de Subprefeitura não é um objeto."
            )

        campos_obrigatorios = (
            "codigoSubprefeitura",
            "nomeSubprefeitura",
        )

        campos_ausentes = [
            campo for campo in campos_obrigatorios if campo not in item
        ]

        if campos_ausentes:
            raise CommandError(
                "Registro de Subprefeitura inválido. "
                "Campos ausentes: " + ", ".join(campos_ausentes)
            )

        codigo = item["codigoSubprefeitura"]
        nome = item["nomeSubprefeitura"]

        if not isinstance(codigo, str):
            raise CommandError(
                f"Campo 'codigoSubprefeitura' inválido: {codigo!r}"
            )

        if not codigo.strip():
            raise CommandError(
                "Campo 'codigoSubprefeitura' não pode ser vazio."
            )

        if not isinstance(nome, str):
            raise CommandError(f"Campo 'nomeSubprefeitura' inválido: {nome!r}")

        if not nome.strip():
            raise CommandError("Campo 'nomeSubprefeitura' não pode ser vazio.")
