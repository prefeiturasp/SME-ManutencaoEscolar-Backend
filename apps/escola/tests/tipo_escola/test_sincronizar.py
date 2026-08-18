from unittest.mock import Mock, patch

import pytest
import requests
from django.core.management import CommandError, call_command

from apps.escola.models import TipoEscola

pytestmark = pytest.mark.django_db


class TestSincronizarTiposEscolas:
    """Testes do comando de sincronização de tipos de escola."""

    @patch(
        "apps.escola.management.commands.sincronizar_tipos_escolas.requests."
        "get"
    )
    def test_deve_criar_tipos_de_escola(
        self,
        mock_get,
        resposta_api_tipos_escolas,
        configurar_api_eol,
    ):
        """Deve criar os tipos de escola retornados pela API."""
        mock_get.return_value = resposta_api_tipos_escolas

        call_command("sincronizar_tipos_escolas")

        assert TipoEscola.objects.count() == 2

        assert TipoEscola.objects.filter(
            codigo_eol=1,
            sigla="EMEF",
        ).exists()

        assert TipoEscola.objects.filter(
            codigo_eol=2,
            sigla="CEMEI",
        ).exists()

    @patch(
        "apps.escola.management.commands.sincronizar_tipos_escolas.requests.get"
    )
    def test_deve_atualizar_tipo_de_escola_existente(
        self, mock_get, resposta_api_tipos_escolas, configurar_api_eol
    ):
        """Deve atualizar um tipo de escola existente."""
        tipo_escola = TipoEscola.objects.create(
            codigo_eol=1,
            sigla="EMEI",
        )

        mock_get.return_value = resposta_api_tipos_escolas

        call_command("sincronizar_tipos_escolas")

        tipo_escola.refresh_from_db()

        assert tipo_escola.sigla == "EMEF"
        assert TipoEscola.objects.count() == 2

    @patch(
        "apps.escola.management.commands.sincronizar_tipos_escolas.requests."
        "get"
    )
    def test_deve_criar_e_atualizar_registros(
        self, mock_get, resposta_api_tipos_escolas, configurar_api_eol
    ):
        """Deve criar novos registros e atualizar os existentes."""
        TipoEscola.objects.create(
            codigo_eol=1,
            sigla="EMEI",
        )

        mock_get.return_value = resposta_api_tipos_escolas

        call_command("sincronizar_tipos_escolas")

        assert TipoEscola.objects.count() == 2

        tipo_existente = TipoEscola.objects.get(codigo_eol=1)

        assert tipo_existente.sigla == "EMEF"

    @patch(
        "apps.escola.management.commands.sincronizar_tipos_escolas.requests."
        "get"
    )
    def test_deve_falhar_quando_api_retornar_json_invalido(
        self, mock_get, configurar_api_eol
    ):
        """Deve falhar quando a API retornar JSON inválido."""
        resposta = Mock()
        resposta.raise_for_status.return_value = None
        resposta.json.side_effect = ValueError

        mock_get.return_value = resposta

        with pytest.raises(
            CommandError,
            match="A API externa retornou um JSON inválido.",
        ):
            call_command("sincronizar_tipos_escolas")

    @patch(
        "apps.escola.management.commands.sincronizar_tipos_escolas.requests."
        "get"
    )
    def test_deve_falhar_quando_api_nao_retornar_lista(
        self, mock_get, configurar_api_eol
    ):
        """Deve falhar quando a API não retornar uma lista."""
        resposta = Mock()
        resposta.raise_for_status.return_value = None
        resposta.json.return_value = {
            "codigo": 1,
            "descricaoSigla": "EMEF",
        }

        mock_get.return_value = resposta

        with pytest.raises(
            CommandError,
            match="A API externa deveria retornar uma lista",
        ):
            call_command("sincronizar_tipos_escolas")

    def test_deve_falhar_quando_registro_nao_for_um_dicionario(
        self, configurar_api_eol
    ):
        """Deve rejeitar registro que não seja um objeto."""
        from apps.escola.management.commands.sincronizar_tipos_escolas import (
            Command,
        )

        with pytest.raises(
            CommandError,
            match="Um dos registros retornados pela API não é um objeto.",
        ):
            Command._validar_registro("registro inválido")

    def test_deve_falhar_quando_campo_obrigatorio_estiver_ausente(
        self, configurar_api_eol
    ):
        """Deve rejeitar registro com campo obrigatório ausente."""
        from apps.escola.management.commands.sincronizar_tipos_escolas import (
            Command,
        )

        with pytest.raises(
            CommandError,
            match="Campos ausentes: descricaoSigla",
        ):
            Command._validar_registro(
                {
                    "codigo": 1,
                }
            )

    def test_deve_falhar_quando_codigo_nao_for_inteiro(
        self, configurar_api_eol
    ):
        """Deve rejeitar código que não seja inteiro."""
        from apps.escola.management.commands.sincronizar_tipos_escolas import (
            Command,
        )

        with pytest.raises(
            CommandError,
            match="Campo 'codigo' inválido",
        ):
            Command._validar_registro(
                {
                    "codigo": "1",
                    "descricaoSigla": "EMEF",
                }
            )

    def test_deve_falhar_quando_sigla_nao_for_string(self, configurar_api_eol):
        """Deve rejeitar sigla que não seja uma string."""
        from apps.escola.management.commands.sincronizar_tipos_escolas import (
            Command,
        )

        with pytest.raises(
            CommandError,
            match="Campo 'descricaoSigla' inválido",
        ):
            Command._validar_registro(
                {
                    "codigo": 1,
                    "descricaoSigla": 123,
                }
            )

    def test_deve_aceitar_registro_valido(self, configurar_api_eol):
        """Deve aceitar um registro válido."""
        from apps.escola.management.commands.sincronizar_tipos_escolas import (
            Command,
        )

        Command._validar_registro(
            {
                "codigo": 1,
                "descricaoSigla": "EMEF",
            }
        )

    @patch(
        "apps.escola.management.commands.sincronizar_tipos_escolas.requests."
        "get"
    )
    def test_deve_falhar_quando_api_retornar_erro(
        self, mock_get, configurar_api_eol
    ):
        """Deve retornar erro quando a API externa falhar."""
        mock_get.side_effect = requests.RequestException("Erro de conexão")

        with pytest.raises(
            CommandError,
            match="Erro ao consultar a API externa",
        ):
            call_command("sincronizar_tipos_escolas")

    @patch(
        "apps.escola.management.commands.sincronizar_tipos_escolas.requests."
        "get"
    )
    def test_deve_consultar_api_com_token(
        self, mock_get, resposta_api_tipos_escolas, configurar_api_eol
    ):
        """Deve consultar a API EOL com o token configurado."""
        mock_get.return_value = resposta_api_tipos_escolas

        call_command("sincronizar_tipos_escolas")

        mock_get.assert_called_once()

        argumentos = mock_get.call_args

        assert argumentos.kwargs["headers"]["accept"] == "application/json"
        assert argumentos.kwargs["headers"]["x-api-eol-key"] == "token-teste"

    @patch(
        "apps.escola.management.commands.sincronizar_tipos_escolas."
        "SME_API_EOL_URL",
        "",
    )
    def test_deve_falhar_sem_url_da_api(self):
        """Deve falhar quando a URL da API não estiver configurada."""
        with pytest.raises(
            CommandError,
            match="SME_API_EOL_URL",
        ):
            call_command("sincronizar_tipos_escolas")

    @patch(
        "apps.escola.management.commands.sincronizar_tipos_escolas."
        "SME_API_EOL_TOKEN",
        "",
    )
    def test_deve_falhar_sem_token_da_api(self):
        """Deve falhar quando o token da API não estiver configurado."""
        with pytest.raises(
            CommandError,
            match="SME_API_EOL_TOKEN",
        ):
            call_command("sincronizar_tipos_escolas")

    @patch(
        "apps.escola.management.commands.sincronizar_tipos_escolas.requests."
        "get"
    )
    def test_deve_reverter_importacao_quando_um_registro_for_invalido(
        self, mock_get, configurar_api_eol
    ):
        """Deve desfazer alterações quando um registro for inválido."""
        resposta = Mock()
        resposta.raise_for_status.return_value = None
        resposta.json.return_value = [
            {
                "codigo": 1,
                "descricaoSigla": "EMEF",
            },
            {
                "codigo": "invalido",
                "descricaoSigla": "EMEI",
            },
        ]

        mock_get.return_value = resposta

        with pytest.raises(
            CommandError,
            match="Campo 'codigo' inválido",
        ):
            call_command("sincronizar_tipos_escolas")

        assert not TipoEscola.objects.exists()
