"""_summary_."""

from __future__ import annotations

import logging
from typing import Any

import requests
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import ObjectDoesNotExist

from apps.core.constants import TIMEOUT_DEFAULT
from apps.escola.constants import ENDPOINT_OBTER_ESCOLA
from apps.escola.models import (
    DiretoriaRegional,
    Subprefeitura,
    TipoEscola,
    Unidadeeducacional,
)
from config.settings import SME_API_EOL_TOKEN, SME_API_EOL_URL

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Sincroniza as escolas com os dados da API EOL.

    O comando consulta a API EOL, valida os registros retornados e cria ou
    atualiza as escolas no banco de dados local.

    A sincronização utiliza o código EOL da escola como identificador.
    """

    def handle(self, *args: Any, **options: Any) -> None:
        """Executa a sincronização das escolas."""
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

        api_url = f"{base_url}{ENDPOINT_OBTER_ESCOLA}"

        logger.info("Iniciando importação de escolas.")

        try:
            response = requests.get(
                api_url,
                headers=headers,
                timeout=TIMEOUT_DEFAULT,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            logger.exception("Erro ao consultar a API externa.")
            raise CommandError(
                f"Erro ao consultar a API externa: {exc}"
            ) from exc

        try:
            payload = response.json()
        except ValueError as exc:
            logger.exception("A API externa retornou um JSON inválido.")
            raise CommandError(
                "A API externa retornou um JSON inválido."
            ) from exc

        if not isinstance(payload, list):
            raise CommandError(
                "A API externa deveria retornar uma lista de registros."
            )

        logger.info(
            f"API retornou {len(payload)} registros para importação.",
        )

        quantidade_criados = 0
        quantidade_atualizados = 0

        with transaction.atomic():
            for item in payload:
                self._validar_registro(item)

                codigo_eol = item["codigoEscola"]
                dre = self._obter_dre(item["codigoDRE"])
                tipo_escola = self._obter_tipo_escola(
                    item["siglaTipoEscola"],
                )
                subprefeitura = self._obter_subprefeitura(
                    base_url=base_url,
                    headers=headers,
                    codigo_escola=codigo_eol,
                )

                _, foi_criado = Unidadeeducacional.objects.update_or_create(
                    codigo_eol=codigo_eol,
                    defaults={
                        "nome": item["nomeEscola"],
                        "diretoria_regional": dre,
                        "tipo_escola": tipo_escola,
                        "subprefeitura": subprefeitura,
                    },
                )

                if foi_criado:
                    quantidade_criados += 1
                else:
                    quantidade_atualizados += 1

        logger.info(
            "Importação concluída: %d criados, %d atualizados.",
            quantidade_criados,
            quantidade_atualizados,
        )

    @staticmethod
    def _validar_registro(item: Any) -> None:
        """Valida a estrutura e os tipos de um registro da API."""
        if not isinstance(item, dict):
            raise CommandError(
                "Um dos registros retornados pela API não é um objeto."
            )

        campos_obrigatorios = (
            "codigoEscola",
            "nomeEscola",
            "nomeDRE",
            "siglaDRE",
            "codigoDRE",
            "tipoEscola",
            "siglaTipoEscola",
        )

        campos_ausentes = [
            campo for campo in campos_obrigatorios if campo not in item
        ]

        if campos_ausentes:
            raise CommandError(
                "Registro inválido. Campos ausentes: "
                + ", ".join(campos_ausentes)
            )

        campos_string = (
            "codigoEscola",
            "nomeEscola",
            "nomeDRE",
            "siglaDRE",
            "codigoDRE",
            "tipoEscola",
            "siglaTipoEscola",
        )

        for campo in campos_string:
            if not isinstance(item[campo], str):
                raise CommandError(
                    f"Campo '{campo}' inválido: {item[campo]!r}"
                )

            if not item[campo].strip():
                raise CommandError(f"Campo '{campo}' não pode ser vazio.")

    @staticmethod
    def _obter_dre(codigo: str) -> DiretoriaRegional:
        """Obtém a DRE pelo código EOL."""
        try:
            return DiretoriaRegional.objects.get(codigo=codigo)
        except ObjectDoesNotExist as exc:
            raise CommandError(
                f"DRE com código '{codigo}' não encontrada. "
                "Execute primeiro a sincronização das DREs."
            ) from exc

    @staticmethod
    def _obter_tipo_escola(sigla: str) -> TipoEscola:
        """Obtém o tipo de escola pela sigla."""
        try:
            return TipoEscola.objects.get(sigla=sigla)
        except ObjectDoesNotExist as exc:
            raise CommandError(
                f"Tipo de escola com sigla '{sigla}' não encontrado. "
                "Execute primeiro a sincronização dos tipos de escola."
            ) from exc

    @staticmethod
    def _obter_subprefeitura(
        base_url: str,
        headers: dict[str, str],
        codigo_escola: str,
    ) -> Subprefeitura:
        """Obtém ou cadastra a Subprefeitura vinculada à escola.

        Consulta o endpoint específico da escola e sincroniza a
        Subprefeitura retornada pela API.
        """
        api_url = f"{base_url}/escolas/{codigo_escola}/subprefeituras"
        try:
            response = requests.get(
                api_url,
                headers=headers,
                timeout=TIMEOUT_DEFAULT,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            logger.exception(
                "Erro ao consultar a Subprefeitura da escola %s.",
                codigo_escola,
            )
            raise CommandError(
                "Erro ao consultar a Subprefeitura da escola "
                f"{codigo_escola}: {exc}"
            ) from exc

        try:
            payload = response.json()
        except ValueError as exc:
            raise CommandError(
                "A API de Subprefeitura retornou um JSON inválido "
                f"para a escola {codigo_escola}."
            ) from exc

        if not isinstance(payload, list):
            raise CommandError(
                "A API de Subprefeitura deveria retornar uma lista "
                f"para a escola {codigo_escola}."
            )

        if not payload:
            raise CommandError(
                f"Nenhuma Subprefeitura encontrada para a escola "
                f"{codigo_escola}."
            )

        item = payload[0]

        if not isinstance(item, dict):
            raise CommandError(
                "O registro de Subprefeitura retornado pela API "
                f"é inválido para a escola {codigo_escola}."
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

        if not isinstance(codigo, str) or not codigo.strip():
            raise CommandError(
                "Campo 'codigoSubprefeitura' inválido para a escola "
                f"{codigo_escola}."
            )

        if not isinstance(nome, str) or not nome.strip():
            raise CommandError(
                "Campo 'nomeSubprefeitura' inválido para a escola "
                f"{codigo_escola}."
            )

        try:
            return Subprefeitura.objects.get(codigo_eol=codigo.strip())
        except ObjectDoesNotExist as exc:
            raise CommandError(
                f"Subprefeitura com código '{codigo}' não encontrada. "
                "Execute primeiro a sincronização das Subprefeitura."
            ) from exc
