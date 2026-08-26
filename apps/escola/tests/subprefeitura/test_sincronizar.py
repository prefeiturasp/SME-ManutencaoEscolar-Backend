from unittest.mock import Mock, patch

import pytest
import requests
from django.core.management import CommandError, call_command

from apps.escola.management.commands.sincronizar_subprefeituras import Command
from apps.escola.models import DiretoriaRegional, Subprefeitura

pytestmark = pytest.mark.django_db


class TestSincronizarSubprefeituras:
    """Testes do comando de sincronização de Subprefeituras."""

    @patch(
        "apps.escola.management.commands.sincronizar_subprefeituras.requests."
        "get"
    )
    def test_deve_criar_subprefeituras(
        self,
        mock_get,
        resposta_api_subprefeituras,
        configurar_api_eol,
        diretoria_regional_centro,
    ):
        """Deve criar as Subprefeituras retornadas pela API."""
        mock_get.return_value = resposta_api_subprefeituras

        call_command("sincronizar_subprefeituras")

        assert Subprefeitura.objects.count() == 2

        assert Subprefeitura.objects.filter(
            codigo_eol="SP01",
            nome="Subprefeitura Sé",
            diretoria_regional=diretoria_regional_centro,
        ).exists()

        assert Subprefeitura.objects.filter(
            codigo_eol="SP02",
            nome="Subprefeitura Lapa",
            diretoria_regional=diretoria_regional_centro,
        ).exists()

    @patch(
        "apps.escola.management.commands.sincronizar_subprefeituras.requests."
        "get"
    )
    def test_deve_atualizar_subprefeitura_existente(
        self,
        mock_get,
        resposta_api_subprefeituras,
        configurar_api_eol,
        diretoria_regional_centro,
    ):
        """Deve atualizar uma Subprefeitura existente."""
        subprefeitura = Subprefeitura.objects.create(
            codigo_eol="SP01",
            nome="Nome antigo",
            diretoria_regional=diretoria_regional_centro,
        )

        mock_get.return_value = resposta_api_subprefeituras

        call_command("sincronizar_subprefeituras")

        subprefeitura.refresh_from_db()

        assert subprefeitura.nome == "Subprefeitura Sé"
        assert Subprefeitura.objects.count() == 2

    @patch(
        "apps.escola.management.commands.sincronizar_subprefeituras.requests."
        "get"
    )
    def test_deve_criar_e_atualizar_registros(
        self,
        mock_get,
        resposta_api_subprefeituras,
        configurar_api_eol,
        diretoria_regional_centro,
    ):
        """Deve criar novos registros e atualizar os existentes."""
        Subprefeitura.objects.create(
            codigo_eol="SP01",
            nome="Nome antigo",
            diretoria_regional=diretoria_regional_centro,
        )

        mock_get.return_value = resposta_api_subprefeituras

        call_command("sincronizar_subprefeituras")

        assert Subprefeitura.objects.count() == 2

        subprefeitura_existente = Subprefeitura.objects.get(
            codigo_eol="SP01",
        )

        assert subprefeitura_existente.nome == "Subprefeitura Sé"

        assert Subprefeitura.objects.filter(
            codigo_eol="SP02",
            nome="Subprefeitura Lapa",
        ).exists()

    @patch(
        "apps.escola.management.commands.sincronizar_subprefeituras.requests."
        "get"
    )
    def test_deve_falhar_quando_nao_houver_diretorias_regionais(
        self,
        mock_get,
        configurar_api_eol,
    ):
        """Deve falhar quando não houver Diretorias Regionais."""
        with pytest.raises(
            CommandError,
            match="Nenhuma Diretoria Regional cadastrada",
        ):
            call_command("sincronizar_subprefeituras")

        mock_get.assert_not_called()

    @patch(
        "apps.escola.management.commands.sincronizar_subprefeituras.requests."
        "get"
    )
    def test_deve_falhar_quando_api_retornar_json_invalido(
        self,
        mock_get,
        configurar_api_eol,
        diretoria_regional_centro,
    ):
        """Deve falhar quando a API retornar JSON inválido."""
        resposta = Mock()
        resposta.raise_for_status.return_value = None
        resposta.json.side_effect = ValueError

        mock_get.return_value = resposta

        with pytest.raises(
            CommandError,
            match="A API de Subprefeituras retornou um JSON inválido",
        ):
            call_command("sincronizar_subprefeituras")

    @patch(
        "apps.escola.management.commands.sincronizar_subprefeituras.requests."
        "get"
    )
    def test_deve_falhar_quando_api_nao_retornar_lista(
        self,
        mock_get,
        configurar_api_eol,
        diretoria_regional_centro,
    ):
        """Deve falhar quando a API não retornar uma lista."""
        resposta = Mock()
        resposta.raise_for_status.return_value = None
        resposta.json.return_value = {
            "codigoSubprefeitura": "SP01",
            "nomeSubprefeitura": "Subprefeitura Sé",
        }

        mock_get.return_value = resposta

        with pytest.raises(
            CommandError,
            match="A API de Subprefeituras deveria retornar uma lista",
        ):
            call_command("sincronizar_subprefeituras")

    def test_deve_falhar_quando_registro_nao_for_um_dicionario(
        self,
        configurar_api_eol,
    ):
        """Deve rejeitar registro que não seja um objeto."""
        with pytest.raises(
            CommandError,
            match="Um dos registros de Subprefeitura não é um objeto",
        ):
            Command._validar_registro("registro inválido")

    def test_deve_falhar_quando_campo_obrigatorio_estiver_ausente(
        self,
        configurar_api_eol,
    ):
        """Deve rejeitar registro com campo obrigatório ausente."""
        with pytest.raises(
            CommandError,
            match="Campos ausentes: nomeSubprefeitura",
        ):
            Command._validar_registro(
                {
                    "codigoSubprefeitura": "SP01",
                }
            )

    def test_deve_falhar_quando_codigo_nao_for_string(
        self,
        configurar_api_eol,
    ):
        """Deve rejeitar código que não seja uma string."""
        with pytest.raises(
            CommandError,
            match="Campo 'codigoSubprefeitura' inválido",
        ):
            Command._validar_registro(
                {
                    "codigoSubprefeitura": 1,
                    "nomeSubprefeitura": "Subprefeitura Sé",
                }
            )

    def test_deve_falhar_quando_codigo_for_vazio(
        self,
        configurar_api_eol,
    ):
        """Deve rejeitar código vazio."""
        with pytest.raises(
            CommandError,
            match="Campo 'codigoSubprefeitura' não pode ser vazio",
        ):
            Command._validar_registro(
                {
                    "codigoSubprefeitura": "   ",
                    "nomeSubprefeitura": "Subprefeitura Sé",
                }
            )

    def test_deve_falhar_quando_nome_nao_for_string(
        self,
        configurar_api_eol,
    ):
        """Deve rejeitar nome que não seja uma string."""
        with pytest.raises(
            CommandError,
            match="Campo 'nomeSubprefeitura' inválido",
        ):
            Command._validar_registro(
                {
                    "codigoSubprefeitura": "SP01",
                    "nomeSubprefeitura": 123,
                }
            )

    def test_deve_falhar_quando_nome_for_vazio(
        self,
        configurar_api_eol,
    ):
        """Deve rejeitar nome vazio."""
        with pytest.raises(
            CommandError,
            match="Campo 'nomeSubprefeitura' não pode ser vazio",
        ):
            Command._validar_registro(
                {
                    "codigoSubprefeitura": "SP01",
                    "nomeSubprefeitura": "   ",
                }
            )

    def test_deve_aceitar_registro_valido(
        self,
        configurar_api_eol,
    ):
        """Deve aceitar um registro válido."""
        Command._validar_registro(
            {
                "codigoSubprefeitura": "SP01",
                "nomeSubprefeitura": "Subprefeitura Sé",
            }
        )

    @patch(
        "apps.escola.management.commands.sincronizar_subprefeituras.requests."
        "get"
    )
    def test_deve_falhar_quando_api_retornar_erro(
        self,
        mock_get,
        configurar_api_eol,
        diretoria_regional_centro,
    ):
        """Deve retornar erro quando a API externa falhar."""
        mock_get.side_effect = requests.RequestException(
            "Erro de conexão",
        )

        with pytest.raises(
            CommandError,
            match="Erro ao consultar Subprefeituras da DRE",
        ):
            call_command("sincronizar_subprefeituras")

    @patch(
        "apps.escola.management.commands.sincronizar_subprefeituras.requests."
        "get"
    )
    def test_deve_consultar_api_com_token(
        self,
        mock_get,
        resposta_api_subprefeituras,
        configurar_api_eol,
        diretoria_regional_centro,
    ):
        """Deve consultar a API EOL com o token configurado."""
        mock_get.return_value = resposta_api_subprefeituras

        call_command("sincronizar_subprefeituras")

        mock_get.assert_called_once()

        argumentos = mock_get.call_args

        assert argumentos.kwargs["headers"]["accept"] == "application/json"
        assert argumentos.kwargs["headers"]["x-api-eol-key"] == "token-teste"

    @patch(
        "apps.escola.management.commands.sincronizar_subprefeituras.requests."
        "get"
    )
    def test_deve_consultar_api_com_codigo_da_dre(
        self,
        mock_get,
        resposta_api_subprefeituras,
        configurar_api_eol,
        diretoria_regional_centro,
    ):
        """Deve enviar o código da DRE nos parâmetros da requisição."""
        mock_get.return_value = resposta_api_subprefeituras

        call_command("sincronizar_subprefeituras")

        argumentos = mock_get.call_args

        assert argumentos.kwargs["params"]["codigoEolDRE"] == "DRE01"

    @patch(
        "apps.escola.management.commands.sincronizar_subprefeituras.requests."
        "get"
    )
    def test_deve_consultar_endpoint_da_dre(
        self,
        mock_get,
        resposta_api_subprefeituras,
        configurar_api_eol,
        diretoria_regional_centro,
    ):
        """Deve consultar o endpoint utilizando o código da DRE."""
        mock_get.return_value = resposta_api_subprefeituras

        call_command("sincronizar_subprefeituras")

        argumentos = mock_get.call_args

        assert "DRE01" in argumentos.args[0]

    @patch(
        "apps.escola.management.commands.sincronizar_subprefeituras."
        "SME_API_EOL_URL",
        "",
    )
    def test_deve_falhar_sem_url_da_api(self):
        """Deve falhar quando a URL da API não estiver configurada."""
        with pytest.raises(
            CommandError,
            match="SME_API_EOL_URL",
        ):
            call_command("sincronizar_subprefeituras")

    @patch(
        "apps.escola.management.commands.sincronizar_subprefeituras."
        "SME_API_EOL_TOKEN",
        "",
    )
    def test_deve_falhar_sem_token_da_api(self):
        """Deve falhar quando o token da API não estiver configurado."""
        with pytest.raises(
            CommandError,
            match="SME_API_EOL_TOKEN",
        ):
            call_command("sincronizar_subprefeituras")

    @patch(
        "apps.escola.management.commands.sincronizar_subprefeituras.requests."
        "get"
    )
    def test_deve_reverter_importacao_quando_um_registro_for_invalido(
        self,
        mock_get,
        configurar_api_eol,
        diretoria_regional_centro,
    ):
        """Deve desfazer alterações quando um registro for inválido."""
        resposta = Mock()
        resposta.raise_for_status.return_value = None
        resposta.json.return_value = [
            {
                "codigoSubprefeitura": "SP01",
                "nomeSubprefeitura": "Subprefeitura Sé",
            },
            {
                "codigoSubprefeitura": 123,
                "nomeSubprefeitura": "Subprefeitura Lapa",
            },
        ]

        mock_get.return_value = resposta

        with pytest.raises(
            CommandError,
            match="Campo 'codigoSubprefeitura' inválido",
        ):
            call_command("sincronizar_subprefeituras")

        assert not Subprefeitura.objects.exists()

    @patch(
        "apps.escola.management.commands.sincronizar_subprefeituras.requests."
        "get"
    )
    def test_deve_consultar_todas_as_dres(
        self,
        mock_get,
        resposta_api_subprefeituras,
        configurar_api_eol,
    ):
        """Deve consultar a API uma vez para cada DRE cadastrada."""
        primeira_dre = DiretoriaRegional.objects.create(
            codigo="DRE01",
            nome="Diretoria Regional Centro",
        )
        segunda_dre = DiretoriaRegional.objects.create(
            codigo="DRE02",
            nome="Diretoria Regional Sul",
        )

        resposta_primeira_dre = Mock()
        resposta_primeira_dre.raise_for_status.return_value = None
        resposta_primeira_dre.json.return_value = [
            {
                "codigoSubprefeitura": "SP01",
                "nomeSubprefeitura": "Subprefeitura Sé",
            },
        ]

        resposta_segunda_dre = Mock()
        resposta_segunda_dre.raise_for_status.return_value = None
        resposta_segunda_dre.json.return_value = [
            {
                "codigoSubprefeitura": "SP02",
                "nomeSubprefeitura": "Subprefeitura Santo Amaro",
            },
        ]

        mock_get.side_effect = [
            resposta_primeira_dre,
            resposta_segunda_dre,
        ]

        call_command("sincronizar_subprefeituras")

        assert mock_get.call_count == 2

        assert Subprefeitura.objects.filter(
            codigo_eol="SP01",
            nome="Subprefeitura Sé",
            diretoria_regional=primeira_dre,
        ).exists()

        assert Subprefeitura.objects.filter(
            codigo_eol="SP02",
            nome="Subprefeitura Santo Amaro",
            diretoria_regional=segunda_dre,
        ).exists()

        assert mock_get.call_args_list[0].kwargs["params"]["codigoEolDRE"] == (
            primeira_dre.codigo
        )
        assert mock_get.call_args_list[1].kwargs["params"]["codigoEolDRE"] == (
            segunda_dre.codigo
        )
