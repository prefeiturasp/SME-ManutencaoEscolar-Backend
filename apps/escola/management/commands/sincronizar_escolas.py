"""Comando para sincronização de escolas com a API EOL.

Este módulo disponibiliza um comando Django responsável por consultar a API
externa do EOL, validar os registros retornados e sincronizar as escolas no
banco de dados.

A sincronização utiliza ``update_or_create`` para criar novos registros ou
atualizar registros existentes com base no código EOL da escola. Registros
com tipos de escola não aceitos ou com informações necessárias ausentes são
ignorados e registrados no log, permitindo que a sincronização das demais
escolas continue normalmente.

A operação de banco de dados é executada dentro de uma transação atômica,
garantindo que as alterações realizadas durante a importação sejam
persistidas integralmente ou revertidas em caso de erro não tratado.
"""

from __future__ import annotations

import logging
import time
from typing import Any

import requests
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.core.constants import TIMEOUT_DEFAULT
from apps.escola.constants import ENDPOINT_OBTER_ESCOLA
from apps.escola.exceptions import DadosEscolaError
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

    O comando consulta a API EOL, valida os registros retornados e cria
    ou atualiza as escolas no banco de dados local.

    A sincronização utiliza o código EOL da escola como identificador.
    Falhas relacionadas a uma escola específica são registradas no log
    e não interrompem a importação das demais escolas. Falhas na
    comunicação com a API principal ou respostas inválidas da API
    interrompem a execução do comando.
    """

    def handle(self, *args: Any, **options: Any) -> None:
        """Executa a sincronização das escolas.

        A API principal é consultada para obter os registros das escolas.
        Cada registro é validado individualmente e, quando possível,
        persistido no banco de dados.

        Args:
            *args (Any): Argumentos posicionais recebidos pelo Django.
            **options (Any): Opções recebidas pelo Django.

        Raises:
            CommandError: Se as configurações obrigatórias não estiverem
                definidas, se houver falha na consulta à API principal,
                se a resposta da API for inválida ou se o payload não
                possuir o formato esperado.
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

        api_url = f"{base_url}{ENDPOINT_OBTER_ESCOLA}"
        inicio = time.perf_counter()

        logger.info("Iniciando importação de escolas.")
        payload = self._obter_escolas_da_api(
            api_url=api_url,
            headers=headers,
        )
        logger.info(
            f"API retornou {len(payload)} registros para importação.",
        )
        logger.info("Iniciando análise das informações. Aguarde...")
        unidades_educacionais = self._coletar_registros(
            base_url, headers, payload
        )
        total_escolas = len(unidades_educacionais)
        logger.info(
            "Análise finalizada. \n Processando informações de "
            f"{total_escolas} unidades para base de dados."
        )
        quantidades = {"criadas": 0, "atualizadas": 0}
        with transaction.atomic():
            for numero, registro in enumerate(unidades_educacionais, start=1):
                _, foi_criado = Unidadeeducacional.objects.update_or_create(
                    codigo_eol=registro["codigo_eol"],
                    defaults={
                        "nome": registro["nome"],
                        "diretoria_regional": registro["diretoria_regional"],
                        "tipo_escola": registro["tipo_escola"],
                        "subprefeitura": registro["subprefeitura"],
                    },
                )
                quantidades["criadas" if foi_criado else "atualizadas"] += 1

                if numero % 500 == 0 or numero == total_escolas:
                    logger.info(
                        f"{numero} de {total_escolas} escolas processadas. "
                        "Aguarde ..."
                    )

        tempo_execucao_segundos = time.perf_counter() - inicio
        tempo_execucao_minutos = tempo_execucao_segundos / 60
        logger.info(
            f"Importação concluída em {tempo_execucao_minutos:.2f} minutos:\n"
            f"{quantidades['criadas']} criados\n"
            f"{quantidades['atualizadas']} atualizados\n"
        )

    def _coletar_registros(
        self,
        base_url: str,
        headers: dict[str, str],
        payload: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Coleta e prepara os registros de escolas para persistência.

        Valida os registros recebidos da API, ignora escolas com tipos não
        aceitos e consulta os dados relacionados à Diretoria Regional, Tipo
        de Escola e Subprefeitura. Os registros válidos são reunidos em uma
        lista para posterior persistência no banco de dados.

        Args:
            base_url (str): URL base da API EOL.
            headers (dict[str, str]): Cabeçalhos utilizados nas requisições
                HTTP para a API EOL.
            payload (list[dict[str, Any]]): Registros de escolas retornados
                pela API EOL.

        Returns:
            list[dict[str, Any]]: Lista de registros de escolas validados e
                enriquecidos com os dados relacionados necessários para
                persistência.
        """
        siglas_aceitas = TipoEscola.objects.aceitos().values_list(
            "sigla",
            flat=True,
        )
        registros = []
        quantidade_erros = 0
        quantidades_ignorados = 0
        for numero, item in enumerate(payload, start=1):
            self._validar_registro(item)
            sigla = item["siglaTipoEscola"]
            codigo_eol = item["codigoEscola"]
            nome_escola = f"{sigla} {item['nomeEscola']}"
            if sigla not in siglas_aceitas:
                quantidades_ignorados += 1
                continue
            try:
                diretoria_regional = self._obter_dre(item["codigoDRE"])
                tipo_escola = self._obter_tipo_escola(sigla)
                subprefeitura = self._obter_subprefeitura(
                    base_url=base_url,
                    headers=headers,
                    codigo_escola=codigo_eol,
                )
            except DadosEscolaError as exc:
                logger.info(f"{nome_escola}: {exc}")
                quantidade_erros += 1
                continue

            registros.append(
                {
                    "codigo_eol": codigo_eol,
                    "nome": nome_escola,
                    "diretoria_regional": diretoria_regional,
                    "tipo_escola": tipo_escola,
                    "subprefeitura": subprefeitura,
                }
            )
            if numero % 500 == 0 or numero == len(payload):
                logger.info(
                    f"{numero} de {len(payload)} escolas analizadas. "
                    "Aguarde ..."
                )
        logger.info(
            f"{quantidades_ignorados} têm as siglas não aceitas\n"
            f"{quantidade_erros} com erros ao obter dados de Diretoria "
            f"Regional, Tipo de escola ou Subprefeitura."
        )
        return registros

    @staticmethod
    def _validar_registro(item: Any) -> None:
        """Valida a estrutura e os tipos de um registro da API.

        Args:
            item (Any): Registro retornado pela API EOL.

        Raises:
            CommandError: Se o registro não for um dicionário, se
                possuir campos obrigatórios ausentes, se algum campo
                obrigatório não for uma string ou se algum campo
                obrigatório estiver vazio.
        """
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
        """Obtém uma Diretoria Regional pelo código EOL.

        Args:
            codigo (str): Código EOL da Diretoria Regional.

        Returns:
            DiretoriaRegional: Instância da Diretoria Regional correspondente
                ao código.

        Raises:
            DadosEscolaError: Se nenhuma Diretoria Regional for encontrada
                para o código informado.
        """
        try:
            return DiretoriaRegional.objects.get(codigo=codigo)
        except DiretoriaRegional.DoesNotExist as exc:
            raise DadosEscolaError(
                f"Diretoria Regional com código '{codigo}' não encontrada."
            ) from exc

    @staticmethod
    def _obter_tipo_escola(sigla: str) -> TipoEscola:
        """Obtém o tipo de escola pela sigla.

        Args:
            sigla (str): Sigla do tipo de escola.

        Returns:
            TipoEscola: Instância do tipo de escola correspondente à sigla.

        Raises:
            DadosEscolaError: Se nenhum tipo de escola for encontrado
                para a sigla informada.
        """
        tipo_escola = TipoEscola.objects.filter(sigla=sigla).first()
        if tipo_escola is None:
            raise DadosEscolaError(
                f"Tipo de escola com sigla '{sigla}' não encontrado."
            )
        return tipo_escola

    @staticmethod
    def _obter_subprefeitura(
        base_url: str,
        headers: dict[str, str],
        codigo_escola: str,
    ) -> Subprefeitura | None:
        """Obtém a Subprefeitura vinculada a uma escola.

        Consulta o endpoint específico da escola, valida o registro
        retornado e busca a Subprefeitura correspondente no banco
        de dados local.

        Args:
            base_url (str): URL base da API EOL.
            headers (dict[str, str]): Cabeçalhos utilizados na requisição HTTP.
            codigo_escola (str): Código EOL da escola.

        Returns:
            Subprefeitura | None: Instância da Subprefeitura correspondente à
                escola, ou None quando nenhuma Subprefeitura for encontrada na
                API ou quando a Subprefeitura retornada não existir no banco
                de dados.

        Raises:
            DadosEscolaError: Se ocorrer erro na consulta à API, se
                a resposta for inválida, se não houver Subprefeitura
                ou se a Subprefeitura não existir no banco local.
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
                f"Erro ao consultar a Subprefeitura da escola {codigo_escola}."
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
            logger.info(
                "Nenhuma Subprefeitura encontrada para a escola "
                f"{codigo_escola}."
            )
            return None

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
        except Subprefeitura.DoesNotExist:
            logger.info(
                f"Subprefeitura com código '{codigo.strip()}' "
                f"não encontrada para a escola {codigo_escola}."
            )
            return None

    @staticmethod
    def _obter_escolas_da_api(
        api_url: str,
        headers: dict[str, str],
    ) -> list[Any]:
        """Consulta a API EOL e retorna os registros das escolas.

        Args:
            api_url (str): URL completa do endpoint de escolas.
            headers (dict[str, str]): Cabeçalhos utilizados na requisição HTTP.

        Returns:
            list[Any]: Lista de registros retornados pela API.

        Raises:
            CommandError: Se ocorrer erro HTTP, erro de comunicação,
                JSON inválido ou se a API retornar um payload que não
                seja uma lista.
        """
        try:
            response = requests.get(
                api_url,
                headers=headers,
                timeout=TIMEOUT_DEFAULT,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            logger.exception("Falha ao consultar a API EOL de escolas.")
            raise CommandError(
                f"Erro ao consultar a API EOL de escolas: {exc}"
            ) from exc

        try:
            payload = response.json()
        except ValueError as exc:
            logger.exception("A API EOL de escolas retornou um JSON inválido.")
            raise CommandError(
                "A API EOL de escolas retornou um JSON inválido."
            ) from exc

        if not isinstance(payload, list):
            raise CommandError(
                "A API EOL de escolas deveria retornar uma lista de registros."
            )

        return payload
