"""Comando para sincronização de Subprefeituras com a API EOL.

Este módulo disponibiliza um comando Django responsável por consultar a API
externa do EOL, obter as Subprefeituras relacionadas às Diretorias Regionais
cadastradas e sincronizar os registros no banco de dados.

A sincronização consulta as Subprefeituras individualmente para cada Diretoria
Regional cadastrada. Os registros são criados ou atualizados utilizando o
código EOL da Subprefeitura como identificador.

A operação de banco de dados é executada dentro de uma transação atômica,
garantindo que as alterações realizadas durante a sincronização sejam
persistidas integralmente ou revertidas em caso de erro não tratado.
"""

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

    Para cada Diretoria Regional cadastrada no banco de dados, o comando
    consulta a API EOL para obter as Subprefeituras relacionadas à DRE.

    Os registros retornados pela API são validados e criados ou atualizados
    no banco de dados utilizando o código EOL da Subprefeitura como
    identificador.
    """

    def handle(self, *args: Any, **options: Any) -> None:
        """Executa a sincronização das Subprefeituras.

        A API EOL é consultada para cada Diretoria Regional cadastrada.
        Os registros retornados são validados individualmente e, quando
        válidos, criados ou atualizados no banco de dados local.

        Args:
            *args (Any): Argumentos posicionais recebidos pelo Django.
            **options (Any): Opções recebidas pelo Django.

        Raises:
            CommandError: Se as configurações obrigatórias não estiverem
                definidas, se não houver Diretorias Regionais cadastradas,
                se ocorrer falha na consulta à API ou se a API retornar
                dados em formato inválido.
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

        quantidades = {"criadas": 0, "atualizadas": 0}

        logger.info("Iniciando importação das Subprefeituras.")
        subprefeituras = self._coletar_registros(base_url, headers)
        with transaction.atomic():
            for item in subprefeituras:
                logging.info(f"Item {item}\n")
                codigo = item["codigoSubprefeitura"]
                nome = item["nomeSubprefeitura"]
                diretoria_regional = item["diretoria_regional"]
                _, foi_criada = Subprefeitura.objects.update_or_create(
                    codigo_eol=codigo,
                    defaults={
                        "nome": nome,
                        "diretoria_regional": diretoria_regional,
                    },
                )
                quantidades["criadas" if foi_criada else "atualizadas"] += 1

        logger.info(
            f"Importação concluída: {quantidades['criadas']} criadas, "
            f"{quantidades['atualizadas']} atualizadas.",
        )

    def _coletar_registros(
        self,
        base_url: str,
        headers: dict[str, str],
    ) -> list[dict[str, Any]]:
        """Coleta e valida as Subprefeituras de todas as Diretorias Regionais.

        Consulta a API EOL para cada Diretoria Regional cadastrada, valida os
        registros retornados e os reúne em uma única lista.

        Args:
            base_url (str): URL base da API EOL.
            headers (dict[str, str]): Cabeçalhos utilizados na requisição HTTP.

        Raises:
            CommandError: Se não houver Diretorias Regionais cadastradas ou se
            algum registro retornado pela API for inválido.

        Returns:
            list[dict[str, Any]]: Lista de Subprefeituras coletadas e validadas
            a partir das Diretorias Regionais cadastradas.
        """
        diretorias = DiretoriaRegional.objects.all()
        subprefeituras = []
        if not diretorias.exists():
            raise CommandError(
                "Nenhuma Diretoria Regional cadastrada. "
                "Execute primeiro a sincronização das DREs."
            )
        for dre in diretorias:
            logger.info(
                f"Consultando Subprefeituras da {dre.nome}.",
            )

            dados = self._obter_subprefeituras(
                base_url=base_url,
                headers=headers,
                codigo_dre=dre.codigo,
            )
            for item in dados:
                self._validar_registro(item)
                subprefeituras.append(
                    {
                        **item,
                        "diretoria_regional": dre,
                    }
                )

        return subprefeituras

    @staticmethod
    def _obter_subprefeituras(
        base_url: str,
        headers: dict[str, str],
        codigo_dre: str,
    ) -> list[dict[str, Any]]:
        """Consulta a API EOL para obter as Subprefeituras de uma DRE.

        Args:
            base_url (str): URL base da API EOL.
            headers (dict[str, str]): Cabeçalhos utilizados na requisição HTTP.
            codigo_dre (str): Código EOL da Diretoria Regional.

        Raises:
            CommandError: Se ocorrer erro na requisição HTTP, se a API
                retornar um JSON inválido ou se a resposta não for uma
                lista de registros.
        Returns:
            list[dict[str, Any]]: Lista de registros de Subprefeituras
                retornados pela API.
        """
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
        """Valida a estrutura e os dados de um registro de Subprefeitura.

        Args:
            item (Any): Registro de Subprefeitura retornado pela API EOL.

        Raises:
            CommandError: Se o registro não for um objeto, possuir campos
                obrigatórios ausentes, se o código ou nome não forem strings
                ou se algum dos campos obrigatórios estiver vazio.
        """
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
