"""Comando para sincronização de tipos de escola com a API EOL.

Este módulo disponibiliza um comando Django responsável por consultar a API
externa do EOL, validar os registros retornados e sincronizar os tipos de
escola no banco de dados local.

A sincronização utiliza ``update_or_create`` para criar novos registros ou
atualizar registros existentes com base no código EOL. A operação de banco de
dados é executada dentro de uma transação atômica, garantindo que a importação
seja concluída integralmente ou revertida em caso de erro.
"""

from __future__ import annotations

import logging
from typing import Any

import requests
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.core.constants import TIMEOUT_DEFAULT
from apps.escola.constants import ENDPOINT_TIPO_ESCOLA
from apps.escola.models.tipos_escola import TipoEscola
from config.settings import SME_API_EOL_TOKEN, SME_API_EOL_URL

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Sincroniza os tipos de escola com os dados da API EOL.

    O comando realiza as seguintes etapas:

    1. Valida as configurações necessárias para acesso à API EOL.
    2. Consulta o endpoint de tipos de escola.
    3. Valida o formato da resposta recebida.
    4. Valida os campos obrigatórios de cada registro.
    5. Cria ou atualiza os tipos de escola no banco de dados.
    6. Registra no log a quantidade de registros criados e atualizados.

    A sincronização dos registros é executada dentro de uma transação atômica.
    Dessa forma, caso ocorra um erro durante o processamento, nenhuma
    alteração parcial será mantida no banco de dados.

    O comando pode ser executado com:
        python manage.py sincronizar_tipos_escolas
    """

    def handle(self, *args: Any, **options: Any) -> None:
        """Executa a sincronização dos tipos de escola.

        O método consulta a API EOL, valida os dados retornados e realiza a
        sincronização dos registros no banco de dados local.

        Args:
            *args: Argumentos posicionais recebidos pelo comando.
            **options: Opções recebidas pelo comando.

        Raises:
            CommandError: Erros ao executar o script
                - Quando as configurações da API não estão disponíveis.
                - Quando ocorre um erro na comunicação com a API.
                - Quando a API retorna um JSON inválido.
                - Quando a API retorna uma estrutura diferente de uma lista de
                    registros.
                - Quando um registro retornado pela API é inválido.
        """
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
        api_url = f"{base_url}{ENDPOINT_TIPO_ESCOLA}"

        logger.info("Iniciando importação de tipos de escola.")
        try:
            response = requests.get(
                api_url, headers=headers, timeout=TIMEOUT_DEFAULT
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

        logger.info(f"API retornou {len(payload)} registros para importação.")
        quantidade_criados = 0
        quantidade_atualizados = 0

        with transaction.atomic():
            for item in payload:
                self._validar_registro(item)

                codigo = item["codigo"]
                sigla = item["descricaoSigla"]
                _, foi_criado = TipoEscola.objects.update_or_create(
                    codigo_eol=codigo,
                    defaults={"sigla": sigla},
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
        """Valida a estrutura e os tipos dos dados de um registro.

        Verifica se o registro recebido da API é um objeto, se contém todos
        os campos obrigatórios e se os valores possuem os tipos esperados.

        Args:
            item: Registro retornado pela API EOL.

        Raises:
            CommandError: Erros ao executar o script
                - Se o registro não for um dicionário.
                - Se algum campo obrigatório estiver ausente.
                - Se o campo ``codigo`` não for um inteiro.
                - Se o campo ``descricaoSigla`` não for uma string.
        """
        if not isinstance(item, dict):
            raise CommandError(
                "Um dos registros retornados pela API não é um objeto."
            )

        campos_obrigatorios = ("codigo", "descricaoSigla")

        campos_ausentes = [
            campo for campo in campos_obrigatorios if campo not in item
        ]

        if campos_ausentes:
            raise CommandError(
                "Registro inválido. Campos ausentes: "
                + ", ".join(campos_ausentes)
            )

        if not isinstance(item["codigo"], int):
            raise CommandError(f"Campo 'codigo' inválido: {item['codigo']!r}")

        if not isinstance(item["descricaoSigla"], str):
            raise CommandError(
                f"Campo 'descricaoSigla' inválido para "
                f"o código {item['codigo']}."
            )
