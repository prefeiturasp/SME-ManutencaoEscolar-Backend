"""Testes unitários do comando gerar_docs."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent
from unittest.mock import Mock, patch

import pytest
from django.apps import AppConfig
from django.core.management.base import CommandError

from apps.core.management.commands.gerar_docs import Command


class TestAddArguments:
    """Testes dos argumentos do comando."""

    def test_adiciona_nome_app(self) -> None:
        """Deve registrar o argumento nome_app."""
        parser = Mock()

        Command().add_arguments(parser)

        parser.add_argument.assert_called_once_with(
            "nome_app",
            help="Nome do app Django. Exemplos: core, empresa ou escola.",
        )


class TestHandle:
    """Testes da execução principal do comando."""

    @patch(
        "apps.core.management.commands.gerar_docs.settings.BASE_DIR", "/tmp"
    )
    @patch(
        "apps.core.management.commands.gerar_docs.Command."
        "criar_glossario_geral"
    )
    @patch(
        "apps.core.management.commands.gerar_docs.Command."
        "atualizar_indice_dominios"
    )
    @patch(
        "apps.core.management.commands.gerar_docs.Command."
        "gerar_documentacao_modulos"
    )
    @patch(
        "apps.core.management.commands.gerar_docs.Command."
        "criar_estrutura_dominio"
    )
    @patch(
        "apps.core.management.commands.gerar_docs.Command."
        "obter_configuracao_app"
    )
    def test_executa_fluxo_completo(
        self,
        mock_obter: Mock,
        mock_estrutura: Mock,
        mock_documentacao: Mock,
        mock_indice: Mock,
        mock_glossario: Mock,
    ) -> None:
        """Deve executar todas as etapas da geração."""
        config = Mock()
        config.name = "apps.core"
        config.label = "core"
        mock_obter.return_value = config

        Command().handle(nome_app="core")

        mock_obter.assert_called_once_with("core")
        mock_estrutura.assert_called_once()
        mock_documentacao.assert_called_once()
        mock_indice.assert_called_once()
        mock_glossario.assert_called_once()


class TestObterConfiguracaoApp:
    """Testes para localização da configuração do app."""

    @patch("apps.core.management.commands.gerar_docs.apps.get_app_configs")
    def test_encontra_app_pelo_label(
        self,
        mock_get_app_configs: Mock,
    ) -> None:
        """Deve localizar o app pelo label."""
        config = Mock()
        config.label = "core"
        config.name = "apps.core"
        mock_get_app_configs.return_value = [config]

        assert Command().obter_configuracao_app(" core ") is config

    @patch("apps.core.management.commands.gerar_docs.apps.get_app_configs")
    def test_encontra_app_pelo_nome_completo(
        self,
        mock_get_app_configs: Mock,
    ) -> None:
        """Deve localizar o app pelo caminho completo."""
        config = Mock()
        config.label = "core"
        config.name = "apps.core"
        mock_get_app_configs.return_value = [config]

        assert Command().obter_configuracao_app("apps.core") is config

    @patch("apps.core.management.commands.gerar_docs.apps.get_app_configs")
    @patch.object(Command, "obter_apps_disponiveis")
    def test_lanca_erro_para_app_inexistente(
        self,
        mock_disponiveis: Mock,
        mock_get_app_configs: Mock,
    ) -> None:
        """Deve lançar CommandError para app inexistente."""
        config = Mock()
        config.label = "core"
        config.name = "apps.core"
        mock_get_app_configs.return_value = [config]
        mock_disponiveis.return_value = ["core", "empresa"]

        with pytest.raises(
            CommandError,
            match="App 'inexistente' não encontrado",
        ) as exc_info:
            Command().obter_configuracao_app("inexistente")

        assert "core" in str(exc_info.value)
        assert "empresa" in str(exc_info.value)


class TestObterAppsDisponiveis:
    """Testes dos apps disponíveis."""

    @patch("apps.core.management.commands.gerar_docs.apps.get_app_configs")
    def test_retorna_labels_ordenados(
        self,
        mock_get_app_configs: Mock,
    ) -> None:
        """Deve retornar labels em ordem alfabética."""
        primeiro = Mock(label="zeta")
        segundo = Mock(label="alpha")
        mock_get_app_configs.return_value = [primeiro, segundo]

        assert Command().obter_apps_disponiveis() == ["alpha", "zeta"]


class TestCriarEstruturaDominio:
    """Testes da estrutura do domínio."""

    def test_cria_arquivos_e_diretorios(
        self,
        app_config: AppConfig,
        tmp_path: Path,
    ) -> None:
        """Deve criar a estrutura inicial."""
        dominio = tmp_path / "core"

        Command().criar_estrutura_dominio(dominio, app_config)

        assert (dominio / "index.rst").exists()
        assert (dominio / "regras_negocio.rst").exists()
        assert (dominio / "codigo" / "index.rst").exists()
        assert not (dominio / "glossario.rst").exists()

    def test_preserva_arquivos_existentes(
        self,
        app_config: AppConfig,
        tmp_path: Path,
    ) -> None:
        """Deve preservar a documentação manual existente."""
        dominio = tmp_path / "core"
        codigo = dominio / "codigo"
        codigo.mkdir(parents=True)

        arquivos = {
            dominio / "index.rst": "índice manual",
            dominio / "regras_negocio.rst": "regras manuais",
            codigo / "index.rst": "índice de código manual",
        }
        for caminho, conteudo in arquivos.items():
            caminho.write_text(conteudo, encoding="utf-8")

        Command().criar_estrutura_dominio(dominio, app_config)

        for caminho, conteudo in arquivos.items():
            assert caminho.read_text(encoding="utf-8") == conteudo


class TestCriarArquivoSeNaoExistir:
    """Testes de criação e preservação de arquivos."""

    def test_cria_arquivo(
        self,
        tmp_path: Path,
    ) -> None:
        """Deve criar arquivo inexistente."""
        caminho = tmp_path / "documento.rst"

        Command().criar_arquivo_se_nao_existir(caminho, "conteúdo")

        assert caminho.read_text(encoding="utf-8") == "conteúdo"

    def test_preserva_arquivo_existente(
        self,
        tmp_path: Path,
    ) -> None:
        """Não deve sobrescrever arquivo existente."""
        caminho = tmp_path / "documento.rst"
        caminho.write_text("manual", encoding="utf-8")

        Command().criar_arquivo_se_nao_existir(caminho, "novo")

        assert caminho.read_text(encoding="utf-8") == "manual"


class TestAtualizarIndiceDominios:
    """Testes do índice central."""

    def test_cria_diretorio_e_atualiza_indice(
        self,
        tmp_path: Path,
    ) -> None:
        """Deve criar o diretório e escrever o índice."""
        raiz = tmp_path / "docs" / "dominios"
        dominio = raiz / "core"
        dominio.mkdir(parents=True)
        (dominio / "index.rst").write_text("Core", encoding="utf-8")

        Command().atualizar_indice_dominios(raiz)

        indice = raiz / "index.rst"
        assert indice.exists()
        assert "core/index" in indice.read_text(encoding="utf-8")
        assert "glossario" in indice.read_text(encoding="utf-8")


class TestObterDominiosDocumentados:
    """Testes de descoberta dos domínios."""

    def test_retorna_apenas_diretorios_com_indice(
        self,
        tmp_path: Path,
    ) -> None:
        """Deve ignorar arquivos e diretórios sem index.rst."""
        (tmp_path / "core").mkdir()
        (tmp_path / "core" / "index.rst").write_text("", encoding="utf-8")
        (tmp_path / "empresa").mkdir()
        (tmp_path / "arquivo.rst").write_text("", encoding="utf-8")

        assert Command().obter_dominios_documentados(tmp_path) == ["core"]

    def test_retorna_lista_vazia(self, tmp_path: Path) -> None:
        """Deve retornar vazio sem domínios documentados."""
        assert Command().obter_dominios_documentados(tmp_path) == []


class TestConteudoDominio:
    """Testes do conteúdo dos documentos de domínio."""

    def test_indice_dominio(
        self,
        app_config: AppConfig,
    ) -> None:
        """Deve gerar o índice do domínio."""
        resultado = Command().criar_conteudo_indice_dominio(app_config)

        assert "Teste" in resultado
        assert "Visão Geral" in resultado
        assert "Regras de Negócio" in resultado
        assert "regras_negocio" in resultado
        assert "codigo/index" in resultado

    def test_regras_negocio(
        self,
        app_config: AppConfig,
    ) -> None:
        """Deve gerar as regras padrão."""
        resultado = Command().criar_conteudo_regras_negocio(app_config)

        for termo in (
            "Identificador Único",
            "UUID",
            "Auditoria de Criação",
            "Auditoria de Atualização",
            "Exclusão e Restauração",
            "exclusão lógica",
        ):
            assert termo in resultado

    def test_indice_codigo_sem_modulos(
        self,
        app_config: AppConfig,
    ) -> None:
        """Deve gerar somente a introdução sem categorias."""
        resultado = Command().criar_conteudo_indice_codigo(app_config)

        assert "Teste" in resultado
        assert "documentação técnica" in resultado
        assert "Models" not in resultado

    def test_indice_codigo_com_todas_as_categorias(
        self,
        app_config: AppConfig,
    ) -> None:
        """Deve agrupar módulos em todas as categorias."""
        modulos = [
            ("apps.teste.models", "models"),
            ("apps.teste.serializers", "serializers"),
            ("apps.teste.views", "views"),
            ("apps.teste.services", "services"),
            ("apps.teste.repository", "repository"),
            ("apps.teste.management.commands.command", "command"),
            ("apps.teste.tasks", "tasks"),
            ("apps.teste.constants", "constants"),
        ]

        resultado = Command().criar_conteudo_indice_codigo(
            app_config,
            modulos,
        )

        for categoria in (
            "Models",
            "Serializers",
            "Views",
            "Services",
            "Repositories",
            "Commands",
            "Tasks",
            "Outros Módulos",
        ):
            assert categoria in resultado

        for _, nome_arquivo in modulos:
            assert nome_arquivo in resultado

    def test_indice_codigo_ordena_modulos(
        self,
        app_config: AppConfig,
    ) -> None:
        """Deve ordenar os módulos dentro da categoria."""
        resultado = Command().criar_conteudo_indice_codigo(
            app_config,
            [
                ("apps.teste.models.z", "z"),
                ("apps.teste.models.a", "a"),
            ],
        )

        assert resultado.index("   a") < resultado.index("   z")

    def test_indice_dominios_com_glossario(
        self,
    ) -> None:
        """Deve colocar o glossário por último."""
        resultado = Command().criar_conteudo_indice_dominios(
            ["core", "empresa", "escola"],
        )

        assert resultado.startswith("Documentação\n")
        assert resultado.index("core/index") < resultado.index("glossario")
        assert resultado.index("escola/index") < resultado.index("glossario")
        assert resultado.endswith("   glossario\n")

    def test_formatar_nome_dominio(self) -> None:
        """Deve formatar nomes técnicos."""
        assert (
            Command().formatar_nome_dominio("gestao_escolar")
            == "Gestao Escolar"
        )


class TestGerarDocumentacaoModulos:
    """Testes da geração dos arquivos de módulos."""

    @patch.object(Command, "atualizar_indice_codigo")
    @patch.object(Command, "criar_conteudo_modulo")
    @patch.object(Command, "obter_modulos_python")
    def test_gera_modulos_e_atualiza_indice(
        self,
        mock_obter: Mock,
        mock_conteudo: Mock,
        mock_indice: Mock,
        app_config: AppConfig,
        tmp_path: Path,
    ) -> None:
        """Deve gerar os arquivos RST e atualizar o índice."""
        mock_obter.return_value = [
            "apps.teste.models",
            "apps.teste.services.usuario",
        ]
        mock_conteudo.side_effect = ["modelo rst", "serviço rst"]

        Command().gerar_documentacao_modulos(app_config, tmp_path)

        assert (tmp_path / "apps_teste_models.rst").read_text(
            encoding="utf-8"
        ) == "modelo rst"
        assert (tmp_path / "apps_teste_services_usuario.rst").read_text(
            encoding="utf-8"
        ) == "serviço rst"

        mock_indice.assert_called_once_with(
            configuracao_app=app_config,
            diretorio_codigo=tmp_path,
            modulos=[
                ("apps.teste.models", "apps_teste_models"),
                ("apps.teste.services.usuario", "apps_teste_services_usuario"),
            ],
        )


class TestObterModulosPython:
    """Testes da descoberta dos módulos Python."""

    def test_aplica_todas_as_regras_de_exclusao(
        self,
        app_config: AppConfig,
        tmp_path: Path,
    ) -> None:
        """Deve ignorar diretórios e nomes de arquivo configurados."""
        arquivos_validos = [
            "models.py",
            "services.py",
            "domain.py",
        ]
        for nome in arquivos_validos:
            (tmp_path / nome).write_text("", encoding="utf-8")

        (tmp_path / "__init__.py").write_text("", encoding="utf-8")
        for nome in (
            "test_models.py",
            "my_test_service.py",
            "schemas.py",
            "user_schemas.py",
            "urls.py",
            "api_urls.py",
        ):
            (tmp_path / nome).write_text("", encoding="utf-8")

        for diretorio in ("migrations", "tests", "schemas"):
            pasta = tmp_path / diretorio
            pasta.mkdir()
            (pasta / "modulo.py").write_text("", encoding="utf-8")

        resultado = Command().obter_modulos_python(app_config)

        assert resultado == [
            "apps.teste.domain",
            "apps.teste.models",
            "apps.teste.services",
        ]

    def test_exclusoes_sao_case_insensitive(
        self,
        app_config: AppConfig,
        tmp_path: Path,
    ) -> None:
        """Deve aplicar exclusões independentemente de maiúsculas."""
        (tmp_path / "URLS_API.py").write_text("", encoding="utf-8")
        (tmp_path / "TEST_service.py").write_text("", encoding="utf-8")
        (tmp_path / "USER_SCHEMAS.py").write_text("", encoding="utf-8")

        pasta = tmp_path / "SCHEMAS"
        pasta.mkdir()
        (pasta / "modelo.py").write_text("", encoding="utf-8")

        (tmp_path / "service.py").write_text("", encoding="utf-8")

        assert Command().obter_modulos_python(app_config) == [
            "apps.teste.service",
        ]

    def test_encontra_modulos_em_subdiretorios(
        self,
        app_config: AppConfig,
        tmp_path: Path,
    ) -> None:
        """Deve encontrar módulos válidos em subdiretórios."""
        repository = tmp_path / "repository"
        repository.mkdir()
        (repository / "usuario_repository.py").write_text("", encoding="utf-8")

        assert Command().obter_modulos_python(app_config) == [
            "apps.teste.repository.usuario_repository",
        ]


class TestAtualizarIndiceCodigo:
    """Testes da atualização do índice de código."""

    def test_escreve_indice(
        self,
        app_config: AppConfig,
        tmp_path: Path,
    ) -> None:
        """Deve escrever o índice gerado."""
        Command().atualizar_indice_codigo(
            app_config,
            tmp_path,
            [("apps.teste.models", "models")],
        )

        conteudo = (tmp_path / "index.rst").read_text(encoding="utf-8")
        assert "Models" in conteudo
        assert "models" in conteudo


class TestClassificarModulo:
    """Testes da classificação dos módulos."""

    @pytest.mark.parametrize(
        ("modulo", "categoria"),
        [
            ("apps.core.models", "Models"),
            ("apps.core.serializers", "Serializers"),
            ("apps.core.views", "Views"),
            ("apps.core.services", "Services"),
            ("apps.core.repository", "Repositories"),
            ("apps.core.management.commands.gerar_docs", "Commands"),
            ("apps.core.tasks", "Tasks"),
            ("apps.core.constants", "Outros Módulos"),
        ],
    )
    def test_classifica_modulo(
        self,
        modulo: str,
        categoria: str,
    ) -> None:
        """Deve classificar cada responsabilidade."""
        assert Command().classificar_modulo(modulo) == categoria


class TestObterTasksCelery:
    """Testes da descoberta das tasks Celery."""

    def test_encontra_tasks_sync_async_e_com_argumentos(
        self,
        app_config: AppConfig,
        tmp_path: Path,
    ) -> None:
        """Deve encontrar tasks síncronas, assíncronas e parametrizadas."""
        (tmp_path / "tasks.py").write_text(
            dedent(
                """\
                from celery import shared_task


                @shared_task
                def tarefa_sync():
                    pass


                @shared_task(bind=True)
                def tarefa_parametrizada():
                    pass


                @shared_task
                async def tarefa_async():
                    pass


                @other_decorator
                def nao_e_task():
                    pass


                @other_decorator
                @shared_task
                def outra_task():
                    pass
                """
            ),
            encoding="utf-8",
        )

        assert Command().obter_tasks_celery(app_config) == [
            "outra_task",
            "tarefa_async",
            "tarefa_parametrizada",
            "tarefa_sync",
        ]

    def test_ignora_decorators_nao_shared_task(
        self,
        app_config: AppConfig,
        tmp_path: Path,
    ) -> None:
        """Deve ignorar decorators sem shared_task."""
        (tmp_path / "tasks.py").write_text(
            dedent(
                """\
                def decorator():
                    pass


                @decorator
                def funcao_normal():
                    pass


                @decorator(valor=1)
                def outra_funcao():
                    pass
                """
            ),
            encoding="utf-8",
        )

        assert Command().obter_tasks_celery(app_config) == []

    def test_retorna_vazio_sem_tasks_py(
        self,
        app_config: AppConfig,
    ) -> None:
        """Deve retornar vazio quando tasks.py não existir."""
        assert Command().obter_tasks_celery(app_config) == []

    def test_erro_de_sintaxe_e_propagado(
        self,
        app_config: AppConfig,
        tmp_path: Path,
    ) -> None:
        """Deve propagar erro quando tasks.py possuir sintaxe inválida."""
        (tmp_path / "tasks.py").write_text(
            "def tarefa(:\n    pass\n",
            encoding="utf-8",
        )

        with pytest.raises(SyntaxError):
            Command().obter_tasks_celery(app_config)


class TestCriarConteudoModulo:
    """Testes da documentação de módulos."""

    def test_modulo_normal(
        self,
        app_config: AppConfig,
    ) -> None:
        """Não deve adicionar automethod fora de tasks."""
        resultado = Command().criar_conteudo_modulo(
            "apps.teste.services",
            app_config,
        )

        assert ".. automodule:: apps.teste.services" in resultado
        assert ".. automethod::" not in resultado

    def test_tasks_sem_tasks(
        self,
        app_config: AppConfig,
    ) -> None:
        """Não deve adicionar automethod sem tasks."""
        with patch.object(Command, "obter_tasks_celery", return_value=[]):
            resultado = Command().criar_conteudo_modulo(
                "apps.teste.tasks",
                app_config,
            )

        assert ".. automodule:: apps.teste.tasks" in resultado
        assert ".. automethod::" not in resultado

    def test_tasks_com_tasks(
        self,
        app_config: AppConfig,
    ) -> None:
        """Deve documentar cada task encontrada."""
        with patch.object(
            Command,
            "obter_tasks_celery",
            return_value=["segunda", "primeira"],
        ):
            resultado = Command().criar_conteudo_modulo(
                "apps.teste.tasks",
                app_config,
            )

        assert ".. automethod:: apps.teste.tasks.segunda.run" in resultado
        assert ".. automethod:: apps.teste.tasks.primeira.run" in resultado


class TestCriarGlossarioGeral:
    """Testes do glossário geral."""

    def test_cria_glossario(
        self,
        tmp_path: Path,
    ) -> None:
        """Deve criar o glossário inicial."""
        caminho = tmp_path / "glossario.rst"

        Command().criar_glossario_geral(caminho)

        conteudo = caminho.read_text(encoding="utf-8")
        assert "Glossário" in conteudo
        assert "UE" in conteudo
        assert "Unidade Educacional" in conteudo
        assert "DRE" in conteudo
        assert "Diretoria Regional de Educação" in conteudo

    def test_preserva_glossario_existente(
        self,
        tmp_path: Path,
    ) -> None:
        """Deve preservar glossário manual."""
        caminho = tmp_path / "glossario.rst"
        caminho.write_text("Glossário personalizado.", encoding="utf-8")

        Command().criar_glossario_geral(caminho)

        assert (
            caminho.read_text(encoding="utf-8") == "Glossário personalizado."
        )
