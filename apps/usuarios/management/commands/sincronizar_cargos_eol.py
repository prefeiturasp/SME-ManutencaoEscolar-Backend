"""Comando para sincronização de cargos com a API EOL.

Este módulo disponibiliza um comando Django responsável por consultar a API
externa do EOL, validar os registros retornados e sincronizar os cargos no
banco de dados.

A sincronização utiliza ``update_or_create`` para criar novos registros ou
atualizar registros existentes com base no código EOL do cargo. Para registros
existentes, somente o nome do cargo é atualizado, preservando os campos
``perfil`` e ``ativo``, que podem ser gerenciados manualmente no sistema.

Novos cargos são cadastrados com o perfil opcional não informado e com o
campo ``ativo`` definido como verdadeiro pelo valor padrão do modelo.

A operação de banco de dados é executada dentro de uma transação atômica,
garantindo que as alterações realizadas durante a importação sejam
persistidas integralmente ou revertidas em caso de erro não tratado.
"""

from __future__ import annotations

import logging
from typing import Any

import requests
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.core.constants import TIMEOUT_DEFAULT
from apps.usuarios.constants import ENDPOINT_CARGOS_EOL
from apps.usuarios.models import CargoEOL
from config.settings import SME_API_EOL_TOKEN, SME_API_EOL_URL

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Sincroniza os cargos EOL com os dados da API externa.

    O comando consulta a API EOL, valida os registros retornados e cria
    ou atualiza os cargos no banco de dados local.

    A sincronização utiliza o código EOL do cargo como identificador.
    Registros existentes têm somente o nome atualizado, preservando as
    informações de perfil e de ativação cadastradas localmente.

    Falhas na comunicação com a API ou respostas inválidas interrompem
    a execução do comando.
    """

    help = "Sincroniza os cargos EOL com a API externa."

    def handle(self, *args: Any, **options: Any) -> None:
        """Executa a sincronização dos cargos EOL.

        A API EOL é consultada para obter os cargos disponíveis. Cada
        registro retornado é validado e, quando válido, persistido no
        banco de dados local.

        Registros novos são criados com perfil não definido e com o campo
        ``ativo`` utilizando o valor padrão do modelo. Registros existentes
        têm somente o nome atualizado.

        Args:
            *args (Any): Argumentos posicionais recebidos pelo comando.
            **options (Any): Opções recebidas pelo comando.

        Raises:
            CommandError: Se as configurações obrigatórias não estiverem
                definidas, se houver falha na consulta à API, se a resposta
                da API for inválida ou se o payload não possuir o formato
                esperado.
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

        api_url = f"{base_url}{ENDPOINT_CARGOS_EOL}"

        logger.info("Iniciando importação dos cargos EOL.")

        payload = self._obter_cargos_da_api(
            api_url=api_url,
            headers=headers,
        )

        logger.info(f"API retornou {len(payload)} cargos para importação.")

        registros = self._coletar_registros(payload)

        quantidade_criados = 0
        quantidade_atualizados = 0

        with transaction.atomic():
            for registro in registros:
                _, foi_criado = self._salvar_cargo(registro)

                if foi_criado:
                    quantidade_criados += 1
                else:
                    quantidade_atualizados += 1

        logger.info(
            f"Importação de cargos concluída: {quantidade_criados} criados, "
            f"{quantidade_atualizados} atualizados.",
        )

    @staticmethod
    def _obter_cargos_da_api(
        api_url: str,
        headers: dict[str, str],
    ) -> list[Any]:
        """Consulta a API EOL e retorna os registros de cargos.

        Realiza uma requisição HTTP para o endpoint de cargos da API EOL,
        valida o status da resposta e converte o conteúdo retornado para
        JSON..

        Args:
            api_url (str): URL completa do endpoint de cargos da API EOL.
            headers (dict[str, str]): Cabeçalhos utilizados na requisição
                HTTP.

        Raises:
            CommandError:
                - Se ocorrer erro durante a comunicação com a API.
                - Se a API retornar um JSON inválido.
                - Se a API não retornar uma lista de registros.

        Returns:
            list[Any]: Lista de cargos retornados pela API EOL.
        """
        try:
            response = requests.get(
                api_url,
                headers=headers,
                timeout=TIMEOUT_DEFAULT,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            logger.exception("Erro ao consultar a API EOL de cargos.")
            raise CommandError(
                f"Erro ao consultar a API EOL de cargos: {exc}"
            ) from exc

        try:
            payload = response.json()
        except ValueError as exc:
            logger.exception("A API EOL de cargos retornou um JSON inválido.")
            raise CommandError(
                "A API EOL de cargos retornou um JSON inválido."
            ) from exc

        if not isinstance(payload, list):
            raise CommandError(
                "A API EOL de cargos deveria retornar uma lista de registros."
            )

        return payload

    def _coletar_registros(
        self,
        payload: list[Any],
    ) -> list[dict[str, Any]]:
        """Coleta e prepara os registros de cargos para persistência.

        Valida individualmente os registros retornados pela API e extrai
        somente os campos necessários para a sincronização local.

        Args:
            payload (list[Any]): Registros de cargos retornados pela API EOL.

        Returns:
            list[dict[str, Any]]: Lista de registros de cargos validados e
                normalizados para persistência.
        """
        registros: list[dict[str, Any]] = []

        for item in payload:
            self._validar_registro(item)

            codigo = item["codigoCargo"]
            nome = item["nomeCargo"].strip()

            registros.append(
                {
                    "codigo": str(codigo),
                    "nome": nome,
                }
            )

        return registros

    @staticmethod
    def _validar_registro(item: Any) -> None:
        """Valida a estrutura e os tipos de um registro de cargo.

        Verifica se o registro recebido da API é um objeto, se contém os
        campos obrigatórios e se os valores possuem os tipos esperados.

        Args:
            item (Any): Registro de cargo retornado pela API EOL.

        Raises:
            CommandError:
                - Se o registro não for um objeto.
                - Se algum campo obrigatório estiver ausente.
                - Se o campo ``codigoCargo`` não for um inteiro.
                - Se o campo ``nomeCargo`` não for uma string.
                - Se o campo ``nomeCargo`` estiver vazio.
        """
        if not isinstance(item, dict):
            raise CommandError(
                "Um dos registros retornados pela API de cargos "
                "não é um objeto."
            )

        campos_obrigatorios = (
            "codigoCargo",
            "nomeCargo",
        )

        campos_ausentes = [
            campo for campo in campos_obrigatorios if campo not in item
        ]

        if campos_ausentes:
            raise CommandError(
                "Registro de cargo inválido. Campos ausentes: "
                + ", ".join(campos_ausentes)
            )

        codigo = item["codigoCargo"]
        nome = item["nomeCargo"]

        if not isinstance(codigo, int):
            raise CommandError(f"Campo 'codigoCargo' inválido: {codigo}")

        if not isinstance(nome, str):
            raise CommandError(
                f"Campo 'nomeCargo' inválido para o código {codigo}: {nome}"
            )

        if not nome.strip():
            raise CommandError(
                f"Campo 'nomeCargo' não pode ser vazio para o código {codigo}."
            )

    @staticmethod
    def _salvar_cargo(
        registro: dict[str, Any],
    ) -> tuple[CargoEOL, bool]:
        """Cria ou atualiza um cargo sem alterar perfil ou ativo.

        O código EOL é utilizado como identificador do cargo. Quando o
        registro já existe, somente o nome é atualizado. Os campos
        ``perfil`` e ``ativo`` existentes são preservados.

        Para novos registros, o campo ``perfil`` permanece não informado
        e o campo ``ativo`` utiliza o valor padrão definido no modelo.

        Args:
            registro (dict[str, Any]): Dados do cargo contendo o código e
                o nome a serem persistidos.

        Returns:
            tuple[CargoEOL, bool]: Tupla contendo o cargo criado ou
                atualizado e um booleano indicando se um novo registro
                foi criado.
        """
        return CargoEOL.objects.update_or_create(
            codigo=registro["codigo"],
            defaults={
                "nome": registro["nome"],
            },
        )
