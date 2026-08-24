"""Sincroniza os diretores das unidades educacionais com a API EOL.

O comando consulta os diretores de cada unidade educacional, obtém seus
dados complementares e prepara os registros para persistência local.

O processo de sincronização:

1. Valida as configurações de acesso à API EOL.
2. Obtém as unidades educacionais cadastradas.
3. Consulta o diretor de cada unidade pelo código do cargo.
4. Considera apenas os vínculos atuais e, quando houver mais de um,
   seleciona o registro com a `dataInicio` mais recente.
5. Consulta os dados complementares do servidor.
6. Valida e normaliza os dados recebidos.
7. Cria ou atualiza os responsáveis e seus vínculos com as unidades.
8. Registra as informações de auditoria da operação.
9. Executa a persistência dentro de uma transação atômica.

A sincronização utiliza o cadastro local de `CargoEOL` para identificar
o código EOL correspondente ao cargo de Diretor de Escola.
"""

from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import Any

import requests
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.core.constants import ENDPOINT_DADOS_PARA_COMAPRE, TIMEOUT_DEFAULT
from apps.escola.constants import (
    ENDPOINT_OBTER_FUNCIONARIOS_POR_CARGO,
    FORMATO_DATA_FUNCIONARIOS_POR_CARGO,
)
from apps.escola.models.responsavel_unidade import (
    HistoricoResponsavel,
    ResponsavelUnidade,
)
from apps.escola.models.unidade_educacional import Unidadeeducacional
from apps.usuarios.models import (
    CargoEOL,
    Usuario,
)
from config.settings import SME_API_EOL_TOKEN, SME_API_EOL_URL

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Sincroniza os diretores das unidades educacionais com a API EOL.

    O comando integra os dados de diretores disponibilizados pela API EOL
    com os cadastros locais de responsáveis e vínculos com unidades
    educacionais.

    A operação é realizada em duas etapas: primeiro os dados são consultados,
    validados e preparados em memória; depois os registros válidos são
    persistidos dentro de uma transação atômica.

    Quando uma unidade possui mais de um diretor com vínculo atual, o
    registro com a data de início mais recente é utilizado.

    A persistência mantém as informações de auditoria de criação e
    atualização dos registros.

    """

    def handle(self, *args: Any, **options: Any) -> None:
        """Executa a sincronização dos diretores das unidades educacionais.

        Valida as configurações da API EOL, consulta as unidades cadastradas,
        obtém os diretores atuais na API e persiste os responsáveis e seus
        vínculos com as unidades dentro de uma transação atômica.

        Args:
            *args (Any): Argumentos posicionais recebidos pelo Django.
            **options (Any): Opções recebidas pelo Django.

        Raises:
            CommandError: Quando as credenciais da API EOL não estão
                configuradas.
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

        inicio = time.perf_counter()

        logger.info("Iniciando importação de diretores.")

        unidades = Unidadeeducacional.objects.all().order_by("codigo_eol")
        total_unidades = unidades.count()

        if total_unidades == 0:
            logger.info(
                "Nenhuma unidade educacional cadastrada para sincronização."
            )
            return

        lista_diretores = self._coletar_registros(
            base_url=base_url,
            headers=headers,
            unidades=unidades,
        )

        logger.info(
            "Análise finalizada. %s diretores válidos serão processados.",
            len(lista_diretores),
        )

        quantidades = {
            "criados": 0,
            "atualizados": 0,
            "historicos_criados": 0,
            "historicos_atualizados": 0,
        }

        usuario = Usuario.objects.get(username="sincronizacao_eol")

        with transaction.atomic():
            for numero, registro in enumerate(
                lista_diretores,
                start=1,
            ):
                responsavel, responsavel_criado = self._salvar_responsavel(
                    registro=registro,
                    usuario=usuario,
                )

                quantidades[
                    "criados" if responsavel_criado else "atualizados"
                ] += 1

                _, historico_criado = self._salvar_historico(
                    responsavel=responsavel,
                    registro=registro,
                    usuario=usuario,
                )

                quantidades[
                    (
                        "historicos_criados"
                        if historico_criado
                        else "historicos_atualizados"
                    )
                ] += 1

                if numero % 500 == 0 or numero == len(lista_diretores):
                    logger.info(
                        "%s de %s diretores processados. Aguarde ...",
                        numero,
                        len(lista_diretores),
                    )

        tempo_execucao_minutos = (time.perf_counter() - inicio) / 60

        logger.info(
            "Importação de diretores concluída em "
            f"{tempo_execucao_minutos:.2f} minutos:\n"
            f"{quantidades['criados']} responsáveis criados\n"
            f"{quantidades['atualizados']} responsáveis atualizados\n"
            f"{quantidades['historicos_criados']} históricos criados\n"
            f"{quantidades['historicos_atualizados']} históricos atualizados\n"
        )

    def _coletar_registros(
        self,
        base_url: str,
        headers: dict[str, str],
        unidades: Any,
    ) -> list[dict[str, Any]]:
        """Obtém e prepara os diretores das unidades para persistência.

        Percorre as unidades educacionais, consulta o diretor atual de cada
        unidade e monta os dados necessários para a atualização dos
        responsáveis e seus vínculos.

        Unidades sem diretor são contabilizadas separadamente. Erros
        individuais durante a consulta são registrados e não interrompem
        o processamento das demais unidades..

        Args:
            base_url (str): URL base da API EOL.
            headers (dict[str, str]): Cabeçalhos utilizados nas requisições à
                API.
            unidades (Any): QuerySet contendo as unidades educacionais a
                processar.

        Returns:
            list[dict[str, Any]]: Lista de dicionários contendo os dados dos
                diretores encontrados.
        """
        lista_diretores: list[dict[str, Any]] = []
        quantidade_erros = 0
        quantidade_sem_diretor = 0

        total_unidades = unidades.count()
        diretor = self._obter_cargo_diretor()
        for numero, unidade in enumerate(unidades, start=1):
            try:
                registro = self._obter_dados_diretor(
                    base_url=base_url,
                    headers=headers,
                    codigo_escola=unidade.codigo_eol,
                    codigo_diretor=diretor.codigo,
                )

                if registro is None:
                    quantidade_sem_diretor += 1
                    continue

                lista_diretores.append(
                    self._montar_registro(
                        base_url=base_url,
                        headers=headers,
                        unidade=unidade,
                        registro=registro,
                        cargo_diretor=diretor,
                    )
                )

            except CommandError as exc:
                quantidade_erros += 1
                logger.error(
                    "Unidade %s ignorada: %s",
                    unidade.codigo_eol,
                    exc,
                )

            if numero % 500 == 0 or numero == total_unidades:
                logger.info(
                    "%s de %s unidades analisadas. Aguarde ...",
                    numero,
                    total_unidades,
                )

        logger.info(
            f"{len(lista_diretores)} diretores válidos encontrados.\n"
            f"{quantidade_sem_diretor} unidades sem diretor.\n"
            f"{quantidade_erros} unidades com erro.",
        )

        return lista_diretores

    def _obter_dados_diretor(
        self,
        base_url: str,
        headers: dict[str, str],
        codigo_escola: str,
        codigo_diretor: str,
    ) -> dict[str, Any] | None:
        """Obtém o diretor atual de uma unidade na API EOL.

        Consulta o endpoint de funcionários por cargo. Quando existem
        múltiplos registros ativos para a mesma unidade, retorna aquele cuja
        data de início é a mais recente.

        Registros com `dataFim` preenchido não são considerados atuais.

        Args:
            base_url (str): URL base da API EOL.
            headers (dict[str, str]): Cabeçalhos utilizados na requisição.
            codigo_escola (str): Código EOL da unidade educacional.
            codigo_diretor (str): Código EOL do cargo de diretor.

        Raises:
            CommandError:
                - Quando ocorre erro de comunicação com a API.
                -  Quando a API retorna um status HTTP diferente
                    de 200 ou 204.
                - Quando a API retorna JSON inválido.
                - Quando a resposta da API possui formato inválido.

        Returns:
            dict[str, Any] | None:  Dicionário contendo o diretor atual ou
                `None` quando a unidade não possui diretor atual.
        """
        endpoint = ENDPOINT_OBTER_FUNCIONARIOS_POR_CARGO.format(
            codigo_escola=codigo_escola, codigo_cargo=codigo_diretor
        )
        url = f"{base_url}{endpoint}"

        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=TIMEOUT_DEFAULT,
            )
        except requests.RequestException as exc:
            raise CommandError(
                f"Erro ao consultar o diretor da escola {codigo_escola}: {exc}"
            ) from exc

        if response.status_code == 204:
            return None

        if response.status_code != 200:
            raise CommandError(
                f"API de diretores retornou HTTP {response.status_code} "
                f"para a escola {codigo_escola}."
            )

        try:
            payload = response.json()
        except ValueError as exc:
            raise CommandError(
                f"A API de diretores retornou JSON inválido "
                f"para a escola {codigo_escola}."
            ) from exc

        if not isinstance(payload, list):
            raise CommandError(
                f"A API de diretores deveria retornar uma lista "
                f"para a escola {codigo_escola}."
            )

        if not payload:
            return None

        registros_validos = []

        for item in payload:
            self._validar_registro_diretor(
                registro=item,
                codigo_escola=codigo_escola,
            )

            if item["dataFim"] is None:
                registros_validos.append(item)

        if not registros_validos:
            return None

        return self._obter_mais_recente(registros_validos)

    @staticmethod
    def _obter_mais_recente(
        registros: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Retorna o registro com a data de início mais recente.

        Registros sem `dataInicio` são considerados anteriores aos registros
        que possuem uma data válida.

        Args:
            registros (list[dict[str, Any]]): Lista de registros de diretores
                a serem comparados.

        Returns:
            dict[str, Any]: Registro de diretor cuja `dataInicio` é a mais
                recente.
        """
        return max(
            registros,
            key=lambda registro: (
                datetime.strptime(
                    registro["dataInicio"].strip(),
                    FORMATO_DATA_FUNCIONARIOS_POR_CARGO,
                )
                if registro.get("dataInicio")
                else datetime.min
            ),
        )

    def _montar_registro(
        self,
        base_url: str,
        headers: dict[str, str],
        unidade: Unidadeeducacional,
        registro: dict[str, Any],
        cargo_diretor: CargoEOL,
    ) -> dict[str, Any]:
        """Monta os dados do diretor para persistência no banco.

        Obtém os dados complementares do servidor, valida as informações
        retornadas pela API e normaliza os campos opcionais de contato..

        Args:
            base_url (str): URL base da API EOL.
            headers (dict[str, str]): Cabeçalhos utilizados nas requisições.
            unidade (Unidadeeducacional): Unidade educacional à qual o diretor
                está vinculado.
            registro (dict[str, Any]): Registro do diretor retornado pela API
                EOL.
            cargo_diretor (CargoEOL): Cargo EOL de diretor de escola.

        Returns:
            dict[str, Any]: Dicionário com os dados necessários para criar ou
            atualizar o responsável e seu vínculo com a unidade.
        """
        codigo_rf = registro["codigoRF"].strip()

        dados_adicionais = self._obter_dados_complementares(
            base_url=base_url,
            headers=headers,
            registro_funcional=codigo_rf,
            codigo_escola=unidade.codigo_eol,
        )

        self._validar_dados_adicionais(
            dados=dados_adicionais,
            codigo_escola=unidade.codigo_eol,
            registro_funcional=codigo_rf,
        )

        return {
            "registro_funcional": codigo_rf,
            "nome": registro["nomeServidor"].strip(),
            "email": self._normalizar_string(
                dados_adicionais.get("email"),
            ),
            "telefone": self._normalizar_string(
                dados_adicionais.get("telefoneUe"),
            ),
            "esta_afastado": registro["estaAfastado"],
            "unidade_educacional": unidade,
            "cargo_diretor": cargo_diretor,
        }

    @staticmethod
    def _normalizar_string(valor: Any) -> str:
        """Normaliza um valor textual para persistência.

        Valores `None` e valores que não sejam strings são convertidos
        para string vazia. Strings válidas têm seus espaços externos
        removidos.

        Args:
            valor (Any): Valor recebido da API.

        Returns:
            str: Valor normalizado como string.
        """
        if valor is None:
            return ""

        if not isinstance(valor, str):
            return ""

        return valor.strip()

    def _obter_dados_complementares(
        self,
        base_url: str,
        headers: dict[str, str],
        registro_funcional: str,
        codigo_escola: str,
    ) -> dict[str, Any]:
        """Obtém os dados complementares do servidor na API EOL.

        Consulta os dados utilizados para complementar o cadastro do
        responsável, principalmente e-mail e telefone da unidade.
        .

        Args:
            base_url (str): URL base da API EOL.
            headers (dict[str, str]): Cabeçalhos utilizados na requisição.
            registro_funcional (str): Registro funcional do servidor.
            codigo_escola (str): Código EOL da unidade educacional.

        Raises:
            CommandError:
                - Quando ocorre erro de comunicação com a API.
                - Quando a API retorna status HTTP diferente de 200.
                - Quando a API retorna JSON inválido.
                - Quando a resposta da API não é um objeto.

        Returns:
            dict[str, Any]: Dicionário com os dados complementares retornados
                pela API.
        """
        endpoint = ENDPOINT_DADOS_PARA_COMAPRE.format(
            registro_funcional=registro_funcional
        )
        url = f"{base_url}{endpoint}"

        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=TIMEOUT_DEFAULT,
            )
        except requests.RequestException as exc:
            raise CommandError(
                f"Erro ao consultar os dados adicionais do RF "
                f"{registro_funcional}, escola {codigo_escola}: {exc}"
            ) from exc

        if response.status_code != 200:
            raise CommandError(
                f"API de autenticação retornou HTTP "
                f"{response.status_code} para o RF "
                f"{registro_funcional}, escola {codigo_escola}."
            )

        try:
            payload = response.json()
        except ValueError as exc:
            raise CommandError(
                f"A API de autenticação retornou JSON inválido "
                f"para o RF {registro_funcional}."
            ) from exc

        if not isinstance(payload, dict):
            raise CommandError(
                f"A API de autenticação deveria retornar um objeto "
                f"para o RF {registro_funcional}."
            )

        return payload

    @staticmethod
    def _validar_registro_diretor(
        registro: Any,
        codigo_escola: str,
    ) -> None:
        """Valida a estrutura e os tipos do registro de diretor.

        Verifica a existência dos campos utilizados pelo sincronizador e
        garante que os campos textuais obrigatórios sejam strings
        preenchidas. Os campos de data podem receber `None`.

        Args:
            registro (Any): Registro retornado pela API EOL.
            codigo_escola (str): Código EOL da unidade educacional.

        Raises:
            CommandError:
                - Quando o registro não é um dicionário.
                - Quando existem campos obrigatórios ausentes.
                - Quando um campo textual possui tipo inválido
                    ou está vazio.
                - Quando um campo de data possui tipo inválido.
                - Quando `estaAfastado` não é booleano.
        """
        if not isinstance(registro, dict):
            raise CommandError(
                f"Registro de diretor inválido para a escola "
                f"{codigo_escola}: esperado um objeto."
            )

        campos_obrigatorios = (
            "codigoRF",
            "nomeServidor",
            "dataInicio",
            "dataFim",
            "cargo",
            "estaAfastado",
        )

        campos_ausentes = [
            campo for campo in campos_obrigatorios if campo not in registro
        ]

        if campos_ausentes:
            raise CommandError(
                f"Registro de diretor inválido para a escola "
                f"{codigo_escola}. Campos ausentes: "
                f"{', '.join(campos_ausentes)}."
            )

        for campo in ("codigoRF", "nomeServidor", "cargo"):
            valor = registro[campo]

            if not isinstance(valor, str):
                raise CommandError(
                    f"Campo '{campo}' inválido para a escola "
                    f"{codigo_escola}: {valor!r}."
                )

            if not valor.strip():
                raise CommandError(
                    f"Campo '{campo}' não pode ser vazio para a escola "
                    f"{codigo_escola}."
                )

        for campo in ("dataInicio", "dataFim"):
            valor = registro[campo]

            if valor is not None and not isinstance(valor, str):
                raise CommandError(
                    f"Campo '{campo}' inválido para a escola "
                    f"{codigo_escola}: {valor!r}."
                )

        if not isinstance(registro["estaAfastado"], bool):
            raise CommandError(
                f"Campo 'estaAfastado' inválido para a escola {codigo_escola}."
            )

    @staticmethod
    def _validar_dados_adicionais(
        dados: Any,
        codigo_escola: str,
        registro_funcional: str,
    ) -> None:
        """Valida os dados complementares retornados pela API.

        Os campos `email` e `telefoneUe` são obrigatórios na estrutura da
        resposta, mas podem conter `None` ou string vazia.

        Args:
            dados (Any):  Dados complementares retornados pela API.
            codigo_escola (str): Código EOL da unidade educacional.
            registro_funcional (str): Registro funcional do servidor.

        Raises:
            CommandError:
                - Quando os dados não são um objeto.
                - Quando `email` ou `telefoneUe` não está presente.
                - Quando `email` ou `telefoneUe` possui tipo inválido.
        """
        if not isinstance(dados, dict):
            raise CommandError(
                f"Dados adicionais inválidos para o RF {registro_funcional}."
            )

        for campo in ("email", "telefoneUe"):
            if campo not in dados:
                raise CommandError(
                    f"Dados adicionais inválidos para a escola "
                    f"{codigo_escola}, RF {registro_funcional}. "
                    f"Campo '{campo}' ausente."
                )

            valor = dados[campo]

            if valor is not None and not isinstance(valor, str):
                raise CommandError(
                    f"Campo '{campo}' inválido para a escola "
                    f"{codigo_escola}, RF {registro_funcional}: "
                    f"{valor!r}."
                )

    @staticmethod
    def _obter_cargo(codigo: str) -> CargoEOL:
        """Obtém um cargo EOL pelo código.

        Args:
            codigo (str): Código EOL do cargo.

        Raises:
            CommandError: Quando não existe cargo com o código informado.

        Returns:
            CargoEOL: Instância de `CargoEOL` correspondente ao código "
            "informado.
        """
        try:
            return CargoEOL.objects.get(codigo=codigo)
        except CargoEOL.DoesNotExist as exc:
            raise CommandError(
                f"Cargo EOL com código '{codigo}' não encontrado."
            ) from exc

    def _obter_cargo_diretor(self) -> CargoEOL:
        """Obtém o cargo EOL correspondente a Diretor de Escola.

        Busca o cargo pelo nome utilizado no cadastro de cargos EOL.

        Raises:
            CommandError:
                - Quando o cargo não está cadastrado.
                - Quando existem múltiplos cargos com o mesmo nome.

        Returns:
            CargoEOL: Instância de `CargoEOL` correspondente a Diretor de
                Escola.
        """
        try:
            cargo_diretor = CargoEOL.objects.get(
                nome="DIRETOR DE ESCOLA",
            )
        except CargoEOL.DoesNotExist:
            raise CommandError(
                "Código EOL para DIRETOR DE ESCOLA não encontrado."
            ) from None
        except CargoEOL.MultipleObjectsReturned:
            raise CommandError(
                "Mais de um cargo DIRETOR DE ESCOLA encontrado "
                "no cadastro de cargos EOL."
            ) from None

        return cargo_diretor

    def _salvar_responsavel(
        self,
        registro: dict[str, Any],
        usuario: Any | None,
    ) -> tuple[ResponsavelUnidade, bool]:
        """Cria ou atualiza um responsável com informações de auditoria.

        Na criação, os dados do responsável e os usuários de criação e
        atualização são definidos a partir do registro e do usuário informado.

        Na atualização, os dados do responsável são atualizados e o usuário
        responsável pela alteração é registrado em `atualizado_por`. Os dados
        originais de criação são preservados.

        Args:
            registro (dict[str, Any]): Dados do responsável obtidos durante a
            sincronização. Deve conter `registro_funcional`, `nome`, `email`,
            `telefone` e `esta_afastado`.
            usuario (Any | None): Usuário responsável pela execução da
                sincronização. Pode   ser `None` quando não houver usuário
                associado à operação.
        Returns:
            tuple[ResponsavelUnidade, bool]: Tupla contendo o responsável
                criado ou atualizado e um booleano indicando se um novo
                registro foi criado.
        """
        responsavel, foi_criado = ResponsavelUnidade.objects.get_or_create(
            registro_funcional=registro["registro_funcional"],
            defaults={
                "nome": registro["nome"],
                "email": registro["email"],
                "telefone": registro["telefone"],
                "esta_afastado": registro["esta_afastado"],
                "criado_por": usuario,
                "atualizado_por": usuario,
            },
        )

        if not foi_criado:
            responsavel.nome = registro["nome"]
            responsavel.email = registro["email"]
            responsavel.telefone = registro["telefone"]
            responsavel.esta_afastado = registro["esta_afastado"]
            responsavel.atualizado_por = usuario
            responsavel.save()

        return responsavel, foi_criado

    def _salvar_historico(
        self,
        responsavel: ResponsavelUnidade,
        registro: dict[str, Any],
        usuario: Any | None,
    ) -> tuple[HistoricoResponsavel, bool]:
        """Cria ou atualiza o vínculo do responsável com a unidade.

        O vínculo é identificado pelo responsável, unidade educacional e cargo.
        Na criação, o vínculo é marcado como ativo e são registrados os
        usuários de criação e atualização.

        Na atualização, o vínculo é marcado como ativo e o usuário responsável
        pela alteração é registrado em `atualizado_por`. Os dados originais de
        criação são preservados.

        Args:
            responsavel (ResponsavelUnidade): Responsável associado ao vínculo.
            registro (dict[str, Any]): Dados do vínculo obtidos durante a
            sincronização. Deve conter `unidade_educacional` e `cargo_diretor`.
            usuario (Any | None): Usuário responsável pela execução da
                sincronização. Pode ser `None` quando não houver usuário
                associado à operação.

        Returns:
            tuple[HistoricoResponsavel, bool]: Tupla contendo o histórico
                criado ou atualizado e um booleano indicando se um novo
                registro foi criado.
        """
        historico, foi_criado = HistoricoResponsavel.objects.get_or_create(
            responsavel=responsavel,
            unidade_educacional=registro["unidade_educacional"],
            cargo=registro["cargo_diretor"],
            defaults={
                "ativo": True,
                "criado_por": usuario,
                "atualizado_por": usuario,
            },
        )

        if not foi_criado:
            historico.ativo = True
            historico.atualizado_por = usuario
            historico.save()

        return historico, foi_criado
