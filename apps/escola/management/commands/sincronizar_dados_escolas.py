"""Comando para sincronização dos dados das unidades educacionais com o EOL.

Este módulo disponibiliza um comando Django responsável por consultar a API
externa do EOL, validar os registros retornados e sincronizar os dados de
contato e endereço das unidades educacionais no banco de dados.

A sincronização utiliza update_or_create para criar novos registros ou
atualizar registros existentes com base na unidade educacional relacionada.
São persistidos somente os dados de contato e endereço retornados pela API,
incluindo e-mail, telefone, logradouro, número, bairro, CEP, município e UF.

Registros com informações inválidas ou ausentes são ignorados e registrados
no log, permitindo que a sincronização das demais unidades educacionais
continue normalmente.

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
from apps.escola.constants import ENDPOINT_DADOS_ESCOLA
from apps.escola.models import DadosUnidadeEducacional, Unidadeeducacional
from config.settings import SME_API_EOL_TOKEN, SME_API_EOL_URL

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Sincroniza os dados das unidades educacionais com a API EOL.

    O comando consulta a API EOL, valida os registros retornados e cria
    ou atualiza os dados das unidades educacionais no banco de dados.

    A sincronização utiliza o código EOL da unidade educacional como
    identificador para consultar seus dados. São persistidos somente os
    dados de contato e endereço retornados pela API.

    Falhas relacionadas a uma unidade educacional específica são registradas
    no log e não interrompem a importação das demais unidades. Falhas na
    comunicação com a API ou respostas inválidas da API interrompem a
    execução do comando.
    """

    def handle(self, *args: Any, **options: Any) -> None:
        """Executa a sincronização dos dados das unidades educacionais.

        A API EOL é consultada individualmente para obter os dados de contato e
        endereço de cada unidade educacional cadastrada. Cada registro
        retornado é validado e, quando válido, persistido no banco de dados.

        Args:
            *args (Any): Argumentos posicionais recebidos pelo Django.
            **options (Any): Opções recebidas pelo Django.

        Raises:
            CommandError: Se as configurações obrigatórias não estiverem
                definidas, se houver falha na consulta à API, se a resposta da
                API for inválida ou se o payload não possuir o formato
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

        unidades = Unidadeeducacional.objects.all()[:10]

        if not unidades.exists():
            raise CommandError("Nenhuma unidade educacional cadastrada.")

        total = unidades.count()
        inicio = time.perf_counter()

        logger.info(
            f"Iniciando importação dos dados de {total} unidades "
            "educacionais.",
        )

        registros = []
        quantidade_erros = 0

        for numero, unidade in enumerate(unidades.iterator(), start=1):
            try:
                dados = self._obter_dados_escola(
                    base_url=base_url,
                    headers=headers,
                    codigo_eol=unidade.codigo_eol,
                )

                self._validar_registro(
                    dados=dados,
                    codigo_eol=unidade.codigo_eol,
                )

                registros.append(
                    {
                        "unidade_educacional": unidade,
                        **self._extrair_dados(dados),
                    }
                )

            except CommandError as exc:
                quantidade_erros += 1
                logger.warning(
                    "Não foi possível importar os dados da unidade "
                    f"{unidade.__str__()}: {exc}"
                )

            if numero % 500 == 0 or numero == total:
                logger.info(f"{numero} de {total} unidades processadas.")

        quantidade_criados = 0
        quantidade_atualizados = 0

        with transaction.atomic():
            for registro in registros:
                _, foi_criado = (
                    DadosUnidadeEducacional.objects.update_or_create(
                        unidade_educacional=registro["unidade_educacional"],
                        defaults={
                            "email": registro["email"],
                            "telefone": registro["telefone"],
                            "logradouro": registro["logradouro"],
                            "numero": registro["numero"],
                            "bairro": registro["bairro"],
                            "cep": registro["cep"],
                            "municipio": registro["municipio"],
                            "uf": registro["uf"],
                        },
                    )
                )

                if foi_criado:
                    quantidade_criados += 1
                else:
                    quantidade_atualizados += 1

        tempo_execucao = (time.perf_counter() - inicio) / 60

        logger.info(
            f"Importação concluída em {tempo_execucao:.2f} minutos: "
            f"{quantidade_criados} criados, {quantidade_atualizados} "
            f"atualizados, {quantidade_erros} erros."
        )

    @staticmethod
    def _obter_dados_escola(
        base_url: str,
        headers: dict[str, str],
        codigo_eol: str,
    ) -> dict[str, Any]:
        """Consulta os dados de uma unidade educacional na API EOL.

        Monta a URL do endpoint de dados da escola utilizando o código EOL
        da unidade e realiza uma requisição HTTP para obter seus dados
        cadastrais, de contato e endereço.

        Args:
            base_url (str):  URL base da API EOL.
            headers (dict[str, str]): Cabeçalhos utilizados na requisição HTTP.
            codigo_eol (str): Código EOL da unidade educacional.

        Raises:
            CommandError:
                - Se ocorrer um erro durante a comunicação com a API.
                - Se a API retornar um status HTTP diferente de 200.
                - Se a API retornar um JSON inválido.
                - Se a API não retornar um objeto JSON.

        Returns:
            dict[str, Any]: Dados da unidade educacional retornados pela API
                EOL.
        """
        endpoint = ENDPOINT_DADOS_ESCOLA.format(
            codigo_escola=codigo_eol,
        )
        api_url = f"{base_url}{endpoint}"

        try:
            response = requests.get(
                api_url,
                headers=headers,
                timeout=TIMEOUT_DEFAULT,
            )
        except requests.RequestException as exc:
            raise CommandError(
                f"Erro ao consultar a unidade {codigo_eol}: {exc}"
            ) from exc

        if response.status_code != 200:
            raise CommandError(
                f"API retornou HTTP {response.status_code} "
                f"para a unidade {codigo_eol}."
            )

        try:
            payload = response.json()
        except ValueError as exc:
            raise CommandError(
                f"A API retornou JSON inválido para a unidade {codigo_eol}."
            ) from exc

        if not isinstance(payload, dict):
            raise CommandError(
                f"A API deveria retornar um objeto "
                f"para a unidade {codigo_eol}."
            )

        return payload

    @staticmethod
    def _validar_registro(
        dados: Any,
        codigo_eol: str,
    ) -> None:
        """Valida a estrutura e os tipos dos dados retornados pela API.

        Verifica se o registro retornado é um objeto, se contém todos os
        campos necessários para a sincronização e se os campos possuem
        os tipos esperados.

        Os campos textuais podem receber ``None``, pois essa condição é
        tratada posteriormente durante a normalização dos dados. O CEP
        pode ser retornado pela API como número inteiro ou como string.


        Args:
            dados (Any): Registro da unidade educacional retornado pelo EOL.
            codigo_eol (str): Código EOL da unidade educacional.

        Raises:
            CommandError:
                - Se o registro não for um objeto.
                - Se algum campo obrigatório estiver ausente.
                - Se algum campo textual possuir tipo inválido.
                - Se o CEP possuir tipo diferente de string ou inteiro.
        """
        if not isinstance(dados, dict):
            raise CommandError(
                f"Registro inválido para a unidade {codigo_eol}: "
                "esperado um objeto."
            )

        campos_obrigatorios = (
            "email",
            "telefone",
            "tipoLogradouro",
            "logradouro",
            "numero",
            "bairro",
            "cep",
            "municipio",
            "uf",
        )

        campos_ausentes = [
            campo for campo in campos_obrigatorios if campo not in dados
        ]

        if campos_ausentes:
            raise CommandError(
                f"Registro inválido para a unidade {codigo_eol}. "
                "Campos ausentes: " + ", ".join(campos_ausentes)
            )

        campos_string = (
            "email",
            "telefone",
            "tipoLogradouro",
            "logradouro",
            "numero",
            "bairro",
            "municipio",
            "uf",
        )

        for campo in campos_string:
            valor = dados[campo]

            if valor is not None and not isinstance(valor, str):
                raise CommandError(
                    f"Campo '{campo}' inválido para a unidade "
                    f"{codigo_eol}: {valor!r}."
                )

        cep = dados["cep"]

        if cep is not None and not isinstance(cep, (str | int)):
            raise CommandError(
                f"Campo 'cep' inválido para a unidade {codigo_eol}: {cep!r}."
            )

    def _extrair_dados(
        self,
        dados: dict[str, Any],
    ) -> dict[str, Any]:
        """Extrai e normaliza os dados que serão persistidos.

        Seleciona somente os campos de contato e endereço necessários para
        o cadastro local da unidade educacional. Os valores textuais são
        normalizados e o logradouro é formado pela combinação do tipo de
        logradouro com o nome do logradouro.

        O CEP é convertido para string e preenchido com zero à esquerda
        quando necessário. A UF é convertida para letras maiúsculas.

        Args:
            dados (dict[str, Any]): Dados da unidade educacional retornados
                pela API EOL.

        Returns:
            dict[str, Any]: Dicionário contendo os dados de contato e endereço
                normalizados para persistência.
        """
        tipo_logradouro = self._normalizar_string(dados.get("tipoLogradouro"))
        logradouro = self._normalizar_string(dados.get("logradouro"))

        return {
            "email": self._normalizar_string(dados.get("email")),
            "telefone": self._normalizar_string(dados.get("telefone")),
            "logradouro": f"{tipo_logradouro.upper()} {logradouro}",
            "numero": self._normalizar_string(dados.get("numero")),
            "bairro": self._normalizar_string(dados.get("bairro")),
            "cep": self._normalizar_cep(dados.get("cep")),
            "municipio": self._normalizar_string(dados.get("municipio")),
            "uf": self._normalizar_string(dados.get("uf")).upper(),
        }

    @staticmethod
    def _normalizar_string(valor: Any) -> str:
        """Normaliza um valor textual para persistência.

        Valores nulos ou que não sejam strings são convertidos para uma
        string vazia. Strings válidas têm os espaços em branco removidos
        das extremidades.

        Args:
            valor (Any): Valor recebido da API EOL.

        Returns:
            str: Valor normalizado como string ou string vazia quando o
                valor não for uma string válida.
        """
        if valor is None:
            return ""

        if not isinstance(valor, str):
            return ""

        return valor.strip()

    @staticmethod
    def _normalizar_cep(valor: Any) -> str:
        """Normaliza o CEP para armazenamento como texto.

        Quando o CEP é retornado como inteiro, adiciona zeros à esquerda
        para garantir oito dígitos. Quando é retornado como string, remove
        os espaços em branco das extremidades.

        Args:
            valor (Any): CEP retornado pela API EOL.

        Returns:
            str: CEP normalizado com até oito dígitos ou string vazia quando
                o valor não for informado ou possuir tipo inválido.
        """
        if valor is None:
            return ""

        if isinstance(valor, int):
            return str(valor).zfill(8)

        if isinstance(valor, str):
            return valor.strip()

        return ""
