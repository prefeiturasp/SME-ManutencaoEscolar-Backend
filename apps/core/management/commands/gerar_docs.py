"""Gera a estrutura inicial do Sphinx para cada app."""

from __future__ import annotations

import ast
from pathlib import Path
from textwrap import dedent
from typing import Any

from django.apps import AppConfig, apps
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

INDEX = "index.rst"


class Command(BaseCommand):
    """Gera a estrutura de documentação Sphinx para um domínio Django."""

    help = (
        "Cria a estrutura de documentação Sphinx para um app Django "
        "e o registra automaticamente no índice de domínios."
    )

    def add_arguments(self, parser: Any) -> None:
        """Adiciona os argumentos aceitos pelo comando."""
        parser.add_argument(
            "nome_app",
            help=("Nome do app Django. Exemplos: core, empresa ou escola."),
        )

    def handle(self, *args: Any, **options: Any) -> None:
        """Executa a geração da documentação do domínio informado."""
        nome_app: str = options["nome_app"]

        configuracao_app = self.obter_configuracao_app(nome_app)

        diretorio_projeto = Path(settings.BASE_DIR)
        diretorio_dominios = diretorio_projeto / "docs" / "dominios"
        diretorio_dominio = diretorio_dominios / configuracao_app.label
        diretorio_codigo = diretorio_dominio / "codigo"

        self.stdout.write(
            f"Criando documentação para: {configuracao_app.name}"
        )

        self.criar_estrutura_dominio(
            diretorio_dominio=diretorio_dominio,
            configuracao_app=configuracao_app,
        )
        self.gerar_documentacao_modulos(
            configuracao_app=configuracao_app,
            diretorio_codigo=diretorio_codigo,
        )

        self.atualizar_indice_dominios(
            diretorio_dominios=diretorio_dominios,
        )

        self.stdout.write(
            self.style.SUCCESS(
                "\nDocumentação do domínio "
                f"'{configuracao_app.label}' criada com sucesso."
            )
        )

        self.stdout.write(f"\nDiretório: {diretorio_dominio}")

    def obter_configuracao_app(
        self,
        nome_app: str,
    ) -> AppConfig:
        """
        Localiza a configuração de um app registrado no Django.

        O app pode ser informado pelo label ou pelo caminho completo
        definido no INSTALLED_APPS.

        Args:
            nome_app: Nome ou caminho do app Django.

        Returns:
            A configuração do app encontrada.

        Raises:
            CommandError: Caso o app não esteja registrado no Django.
        """
        nome_normalizado = nome_app.strip()

        for configuracao_app in apps.get_app_configs():
            if nome_normalizado in {
                configuracao_app.label,
                configuracao_app.name,
            }:
                return configuracao_app

        apps_disponiveis = self.obter_apps_disponiveis()

        lista_apps = "\n".join(f"  - {nome}" for nome in apps_disponiveis)

        raise CommandError(
            f"App '{nome_app}' não encontrado.\n\n"
            f"Apps disponíveis:\n{lista_apps}"
        )

    def obter_apps_disponiveis(self) -> list[str]:
        """
        Retorna os labels dos apps registrados no Django.

        Returns:
            Lista ordenada com os nomes dos apps disponíveis.
        """
        return sorted(
            configuracao_app.label
            for configuracao_app in apps.get_app_configs()
        )

    def criar_estrutura_dominio(
        self,
        diretorio_dominio: Path,
        configuracao_app: AppConfig,
    ) -> None:
        """
        Cria os diretórios e arquivos iniciais da documentação do domínio.

        Arquivos existentes são preservados para evitar a perda de
        documentação escrita manualmente.

        Args:
            diretorio_dominio: Diretório onde ficará a documentação.
            configuracao_app: Configuração do app Django.
        """
        diretorio_codigo = diretorio_dominio / "codigo"

        diretorio_dominio.mkdir(
            parents=True,
            exist_ok=True,
        )

        diretorio_codigo.mkdir(
            parents=True,
            exist_ok=True,
        )

        caminho_indice_dominio = diretorio_dominio / INDEX
        caminho_regras_negocio = diretorio_dominio / "regras_negocio.rst"
        caminho_glossario = diretorio_dominio / "glossario.rst"
        caminho_indice_codigo = diretorio_codigo / INDEX

        arquivos: dict[Path, str] = {
            caminho_indice_dominio: self.criar_conteudo_indice_dominio(
                configuracao_app=configuracao_app,
            ),
            caminho_regras_negocio: self.criar_conteudo_regras_negocio(
                configuracao_app=configuracao_app,
            ),
            caminho_glossario: self.criar_conteudo_glossario(
                configuracao_app=configuracao_app,
            ),
            caminho_indice_codigo: self.criar_conteudo_indice_codigo(
                configuracao_app=configuracao_app,
            ),
        }

        for caminho_arquivo, conteudo in arquivos.items():
            self.criar_arquivo_se_nao_existir(
                caminho_arquivo=caminho_arquivo,
                conteudo=conteudo,
            )

    def criar_arquivo_se_nao_existir(
        self,
        caminho_arquivo: Path,
        conteudo: str,
    ) -> None:
        """
        Cria um arquivo apenas quando ele ainda não existe.

        Isso garante que conteúdos escritos manualmente não sejam
        sobrescritos em execuções posteriores do comando.

        Args:
            caminho_arquivo: Caminho do arquivo a ser criado.
            conteudo: Conteúdo inicial do arquivo.
        """
        if caminho_arquivo.exists():
            self.stdout.write(f"Preservado: {caminho_arquivo}")
            return

        caminho_arquivo.write_text(
            conteudo,
            encoding="utf-8",
        )

        self.stdout.write(self.style.SUCCESS(f"Criado: {caminho_arquivo}"))

    def atualizar_indice_dominios(
        self,
        diretorio_dominios: Path,
    ) -> None:
        """
        Atualiza o índice central com todos os domínios documentados.

        O índice é reconstruído com base nos diretórios que possuem
        um arquivo index.rst.

        Args:
            diretorio_dominios: Diretório raiz dos domínios.
        """
        diretorio_dominios.mkdir(
            parents=True,
            exist_ok=True,
        )

        dominios = self.obter_dominios_documentados(
            diretorio_dominios=diretorio_dominios,
        )

        caminho_indice = diretorio_dominios / INDEX

        conteudo = self.criar_conteudo_indice_dominios(
            dominios=dominios,
        )

        caminho_indice.write_text(
            conteudo,
            encoding="utf-8",
        )

        self.stdout.write(
            self.style.SUCCESS(f"Índice atualizado: {caminho_indice}")
        )

    def obter_dominios_documentados(
        self,
        diretorio_dominios: Path,
    ) -> list[str]:
        """
        Retorna os domínios que possuem documentação criada.

        Um diretório é considerado um domínio quando contém
        um arquivo index.rst.

        Args:
            diretorio_dominios: Diretório raiz dos domínios.

        Returns:
            Lista ordenada dos nomes dos domínios.
        """
        dominios: list[str] = []

        for caminho in diretorio_dominios.iterdir():
            if not caminho.is_dir():
                continue

            caminho_indice = caminho / INDEX

            if caminho_indice.exists():
                dominios.append(caminho.name)

        return sorted(dominios)

    def criar_conteudo_indice_dominio(
        self,
        configuracao_app: AppConfig,
    ) -> str:
        """
        Cria o conteúdo inicial do índice de um domínio.

        Args:
            configuracao_app: Configuração do app Django.

        Returns:
            Conteúdo do arquivo index.rst do domínio.
        """
        nome_dominio = self.formatar_nome_dominio(configuracao_app.label)
        separador = "=" * len(nome_dominio)

        return dedent(
            f"""\
            {separador}
            {nome_dominio}
            {separador}

            Visão Geral
            ===========

            O domínio **{nome_dominio}** é responsável por concentrar as
            funcionalidades relacionadas ao seu contexto de negócio.

            O app disponibiliza operações para gerenciamento das informações
            do domínio, incluindo, quando aplicável, funcionalidades de
            cadastro, consulta, alteração e exclusão (CRUD).

            Também podem existir comandos administrativos específicos para
            criação, atualização ou manutenção de informações relacionadas
            ao domínio.

            Regras de Negócio
            =================

            Esta seção apresenta as regras de negócio que orientam o
            funcionamento do domínio **{nome_dominio}**.

            As regras descrevem comportamentos, restrições, validações
            e condições que precisam ser respeitados pelas funcionalidades
            do domínio.

            .. toctree::
               :maxdepth: 1

               regras_negocio

            Documentação do código
            ======================

            Esta seção apresenta a documentação técnica dos componentes que
            implementam o domínio **{nome_dominio}**.

            A documentação é gerada automaticamente a partir dos módulos
            Python do app e tem como objetivo facilitar a compreensão da
            implementação e de suas responsabilidades técnicas.

            .. toctree::
               :maxdepth: 1

               codigo/index
            """
        )

    def criar_conteudo_regras_negocio(
        self,
        configuracao_app: AppConfig,
    ) -> str:
        """
        Cria o conteúdo inicial do documento de regras de negócio.

        Args:
            configuracao_app: Configuração do app Django.

        Returns:
            Conteúdo inicial do arquivo regras-negocio.rst.
        """
        nome_dominio = self.formatar_nome_dominio(configuracao_app.label)

        return dedent(
            f"""\
            Esta seção documenta as regras de negócio que orientam o
            funcionamento do domínio **{nome_dominio}**.

            Identificador Único
            -------------------

            Cada registro do domínio possui um identificador único no formato
            **UUID (Universally Unique Identifier)**.

            O identificador é gerado automaticamente pelo sistema no momento
            da criação do registro e não pode ser alterado manualmente.

            O UUID deve ser utilizado para identificar de forma inequívoca
            cada registro do domínio.

            Auditoria de Criação
            --------------------

            Os registros possuem informações de auditoria relacionadas à sua
            criação.

            A data e hora de criação são registradas automaticamente pelo
            sistema. Quando disponível, o usuário responsável pela criação
            também é registrado.

            Auditoria de Atualização
            ------------------------

            Os registros possuem informações de auditoria relacionadas às
            alterações realizadas.

            A data e hora da última atualização são atualizadas
            automaticamente pelo sistema. Quando disponível, o usuário
            responsável pela atualização também é registrado.

            Exclusão e Restauração
            ----------------------

            Os registros utilizam exclusão lógica para preservar as
            informações após uma exclusão.

            Ao realizar uma exclusão lógica, o sistema registra a data e hora
            da exclusão e, quando disponível, o usuário responsável pela ação.

            Registros excluídos logicamente não são retornados pelo
            gerenciamento padrão dos objetos.

            Registros excluídos podem ser restaurados, retornando ao conjunto
            de registros disponíveis para consulta e utilização.
        """
        )

    def criar_conteudo_glossario(
        self,
        configuracao_app: AppConfig,
    ) -> str:
        """
        Cria o conteúdo inicial do glossário do domínio.

        Args:
            configuracao_app: Configuração do app Django.

        Returns:
            Conteúdo inicial do arquivo glossario.rst.
        """
        nome_dominio = self.formatar_nome_dominio(configuracao_app.label)
        titulo = "Glossário"
        separador = "=" * len(titulo)

        return dedent(
            f"""\
            {separador}
            {titulo}
            {separador}

            Esta seção contém termos de negócio utilizados pelo domínio
            **{nome_dominio}**.

            Termo
            =====

            Definição do termo.

            Novo termo
            ==========

            Definição do novo termo.

            Evite definições exclusivamente técnicas quando o termo possuir
            um significado específico para o negócio.
            """
        )

    def criar_conteudo_indice_codigo(
        self,
        configuracao_app: AppConfig,
        modulos: list[tuple[str, str]] | None = None,
    ) -> str:
        """
        Cria o índice da documentação técnica do código.

        Este arquivo será preservado nas execuções posteriores para permitir
        referências à documentação gerada automaticamente.

        Args:
            configuracao_app: Configuração do app Django.
            modulos: Lista dos arquivos RST dos módulos.

        Returns:
            Conteúdo inicial do arquivo codigo/index.rst.
        """
        nome_dominio = self.formatar_nome_dominio(configuracao_app.label)
        categorias = [
            "Models",
            "Serializers",
            "Views",
            "Services",
            "Repositories",
            "Commands",
            "Tasks",
            "Outros Módulos",
        ]

        modulos_por_categoria: dict[str, list[str]] = {
            categoria: [] for categoria in categorias
        }

        for modulo, nome_arquivo in modulos or []:
            categoria = self.classificar_modulo(modulo)
            modulos_por_categoria[categoria].append(nome_arquivo)

        linhas = [
            "Esta seção contém a documentação técnica gerada a partir do",
            f"código-fonte do domínio **{nome_dominio}**.",
            "",
            "A documentação de código complementa a documentação de negócio.",
            "",
        ]

        for categoria in categorias:
            modulos_categoria = sorted(modulos_por_categoria[categoria])

            if not modulos_categoria:
                continue

            linhas.extend(
                [
                    categoria,
                    "-" * len(categoria),
                    "",
                    ".. toctree::",
                    "   :maxdepth: 2",
                    "",
                ]
            )

            for nome_arquivo in modulos_categoria:
                linhas.append(f"   {nome_arquivo}")

            linhas.append("")

        return "\n".join(linhas)

    def criar_conteudo_indice_dominios(
        self,
        dominios: list[str],
    ) -> str:
        """
        Cria o conteúdo do índice central de domínios.

        Args:
            dominios: Lista de domínios que possuem documentação.

        Returns:
            Conteúdo do arquivo docs/dominios/index.rst.
        """
        titulo = "Domínios"

        linhas = [
            titulo,
            "=" * len(titulo),
            "",
            "Esta seção apresenta os domínios de negócio do sistema.",
            "",
            ".. toctree::",
            "   :maxdepth: 2",
            "   :caption: Domínios:",
            "",
        ]

        for dominio in dominios:
            linhas.append(f"   {dominio}/index")

        linhas.append("")

        return "\n".join(linhas)

    def formatar_nome_dominio(
        self,
        nome_app: str,
    ) -> str:
        """
        Altera o label técnico do app em um nome legível.

        Args:
            nome_app: Label técnico do app.

        Returns:
            Nome formatado para apresentação na documentação.
        """
        return nome_app.replace("_", " ").title()

    def gerar_documentacao_modulos(
        self,
        configuracao_app: AppConfig,
        diretorio_codigo: Path,
    ) -> None:
        """Gera a documentação automática dos módulos Python do app.

        Args:
            configuracao_app: Configuração do app Django.
            diretorio_codigo: Diretório da documentação automática.
        """
        modulos = self.obter_modulos_python(configuracao_app)
        modulos_documentados: list[tuple[str, str]] = []

        for modulo in modulos:
            nome_arquivo = modulo.replace(".", "_")
            caminho_arquivo = diretorio_codigo / f"{nome_arquivo}.rst"

            caminho_arquivo.write_text(
                self.criar_conteudo_modulo(
                    modulo=modulo,
                    configuracao_app=configuracao_app,
                ),
                encoding="utf-8",
            )

            modulos_documentados.append((modulo, nome_arquivo))
            self.stdout.write(
                self.style.SUCCESS(f"Código documentado: {caminho_arquivo}")
            )

        self.atualizar_indice_codigo(
            configuracao_app=configuracao_app,
            diretorio_codigo=diretorio_codigo,
            modulos=modulos_documentados,
        )

    def obter_modulos_python(
        self,
        configuracao_app: AppConfig,
    ) -> list[str]:
        """Retorna os módulos Python encontrados no app.

        Args:
            configuracao_app: Configuração do app Django.

        Returns:
            Lista ordenada dos módulos Python encontrados.
        """
        diretorio_app = Path(configuracao_app.path)
        modulos: list[str] = []

        for arquivo in sorted(diretorio_app.rglob("*.py")):
            if arquivo.name == "__init__.py":
                continue
            if "migrations" in arquivo.parts:
                continue
            if "tests" in arquivo.parts:
                continue

            caminho_relativo = arquivo.relative_to(diretorio_app)
            partes = caminho_relativo.with_suffix("").parts

            modulo = ".".join([configuracao_app.name, *partes])

            modulos.append(modulo)

        return modulos

    def criar_conteudo_modulo(
        self,
        modulo: str,
        configuracao_app: AppConfig,
    ) -> str:
        """Cria o conteúdo RST para documentação automática de um módulo.

        Args:
            modulo: Caminho completo do módulo Python.
            configuracao_app: Configuração do app Django.

        Returns:
            Conteúdo RST do módulo.
        """
        partes = modulo.split(".")

        conteudo = (
            f"{modulo}\n"
            f"{'=' * len(modulo)}\n\n"
            f".. automodule:: {modulo}\n"
            "   :members:\n"
            "   :undoc-members:\n"
            "   :show-inheritance:\n"
        )
        if "tasks" not in partes:
            return conteudo

        tarefas = self.obter_tasks_celery(
            configuracao_app=apps.get_app_config(partes[1]),
        )

        if not tarefas:
            return conteudo

        conteudo += ""

        for tarefa in tarefas:
            conteudo += f".. automethod:: {modulo}.{tarefa}.run\n\n"

        return conteudo

    def atualizar_indice_codigo(
        self,
        configuracao_app: AppConfig,
        diretorio_codigo: Path,
        modulos: list[tuple[str, str]],
    ) -> None:
        """Atualiza o índice da documentação automática do código.

        Args:
            configuracao_app: Configuração do app Django.
            diretorio_codigo: Diretório da documentação automática.
            modulos: Lista dos nomes dos arquivos RST dos módulos.
        """
        caminho_indice = diretorio_codigo / INDEX

        conteudo = self.criar_conteudo_indice_codigo(
            configuracao_app=configuracao_app,
            modulos=modulos,
        )

        caminho_indice.write_text(
            conteudo,
            encoding="utf-8",
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Índice de código atualizado: {caminho_indice}"
            )
        )

    def classificar_modulo(
        self,
        modulo: str,
    ) -> str:
        """
        Classifica um módulo Python conforme sua responsabilidade.

        Args:
            modulo: Caminho completo do módulo Python.

        Returns:
            Categoria do módulo.
        """
        partes = modulo.split(".")

        if "models" in partes:
            return "Models"

        if "serializers" in partes:
            return "Serializers"

        if "views" in partes:
            return "Views"

        if "services" in partes:
            return "Services"

        if "repository" in partes:
            return "Repositories"

        if "management" in partes and "commands" in partes:
            return "Commands"

        if "tasks" in partes:
            return "Tasks"

        return "Outros Módulos"

    def obter_tasks_celery(
        self,
        configuracao_app: AppConfig,
    ) -> list[str]:
        """Retorna os nomes das funções decoradas com shared_task.

        Args:
            configuracao_app: Configuração do app Django.

        Returns:
            Lista ordenada dos nomes das tasks Celery encontradas.
        """
        diretorio_app = Path(configuracao_app.path)
        caminho_tasks = diretorio_app / "tasks.py"

        if not caminho_tasks.exists():
            return []

        arvore = ast.parse(
            caminho_tasks.read_text(encoding="utf-8"),
            filename=str(caminho_tasks),
        )

        tasks: list[str] = []

        for no in ast.walk(arvore):
            if not isinstance(no, ast.FunctionDef | ast.AsyncFunctionDef):
                continue

            for decorator in no.decorator_list:
                if (
                    isinstance(decorator, ast.Name)
                    and decorator.id == "shared_task"
                ) or (
                    isinstance(decorator, ast.Call)
                    and isinstance(decorator.func, ast.Name)
                    and decorator.func.id == "shared_task"
                ):
                    tasks.append(no.name)
                    break

        return sorted(tasks)
