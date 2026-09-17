from unittest.mock import Mock, patch

import pytest
import requests
from django.core.management import CommandError, call_command

from apps.usuarios.constants import PerfilAcesso
from apps.usuarios.models.cargo_eol import CargoEOL

pytestmark = pytest.mark.django_db


class TestSincronizarCargosEol:
    """Testes do comando de sincronização de cargos EOL."""

    @patch(
        "apps.usuarios.management.commands.sincronizar_cargos_eol.requests.get"
    )
    def test_deve_criar_cargos(
        self,
        mock_get,
        resposta_api_cargos,
        configurar_api_eol,
    ):
        """Deve criar os cargos retornados pela API."""
        CargoEOL.objects.all().delete()
        mock_get.return_value = resposta_api_cargos

        call_command("sincronizar_cargos_eol")

        assert CargoEOL.objects.count() == 2

        cargo = CargoEOL.objects.get(codigo="1000")

        assert cargo.nome == "ASSISTENTE ADMINISTRATIVO"
        assert cargo.perfil == ""
        assert cargo.ativo is True

        cargo = CargoEOL.objects.get(codigo="2000")

        assert cargo.nome == "SUPERVISOR ESCOLAR"
        assert cargo.perfil == ""
        assert cargo.ativo is True

    @patch(
        "apps.usuarios.management.commands.sincronizar_cargos_eol.requests.get"
    )
    def test_deve_atualizar_cargo_existente(
        self,
        mock_get,
        resposta_api_cargos,
        configurar_api_eol,
    ):
        """Deve atualizar o nome de um cargo existente."""
        CargoEOL.objects.all().delete()
        CargoEOL.objects.create(
            codigo="1000",
            nome="Nome antigo",
        )

        mock_get.return_value = resposta_api_cargos

        call_command("sincronizar_cargos_eol")

        cargo = CargoEOL.objects.get(codigo="1000")

        assert cargo.nome == "ASSISTENTE ADMINISTRATIVO"
        assert CargoEOL.objects.count() == 2

    @patch(
        "apps.usuarios.management.commands.sincronizar_cargos_eol.requests.get"
    )
    def test_deve_criar_e_atualizar_registros(
        self,
        mock_get,
        resposta_api_cargos,
        configurar_api_eol,
    ):
        """Deve criar novos cargos e atualizar os existentes."""
        CargoEOL.objects.all().delete()
        CargoEOL.objects.create(
            codigo="1000",
            nome="Nome antigo",
        )

        mock_get.return_value = resposta_api_cargos

        call_command("sincronizar_cargos_eol")

        assert CargoEOL.objects.count() == 2

        cargo = CargoEOL.objects.get(codigo="1000")

        assert cargo.nome == "ASSISTENTE ADMINISTRATIVO"

        assert CargoEOL.objects.filter(
            codigo="2000",
            nome="SUPERVISOR ESCOLAR",
        ).exists()

    @patch(
        "apps.usuarios.management.commands.sincronizar_cargos_eol.requests.get"
    )
    def test_deve_preservar_perfil_do_cargo_existente(
        self,
        mock_get,
        configurar_api_eol,
    ):
        """Deve preservar o perfil já definido para o cargo."""
        CargoEOL.objects.create(
            codigo="1000",
            nome="Nome antigo",
            perfil=PerfilAcesso.UE,
        )

        resposta = Mock()
        resposta.raise_for_status.return_value = None
        resposta.json.return_value = [
            {
                "codigoCargo": 1000,
                "nomeCargo": "ASSISTENTE ADMINISTRATIVO ATUALIZADO",
            },
        ]

        mock_get.return_value = resposta

        call_command("sincronizar_cargos_eol")

        cargo = CargoEOL.objects.get(codigo="1000")

        assert cargo.nome == "ASSISTENTE ADMINISTRATIVO ATUALIZADO"
        assert cargo.perfil == PerfilAcesso.UE

    @patch(
        "apps.usuarios.management.commands.sincronizar_cargos_eol.requests.get"
    )
    def test_deve_preservar_cargo_inativo(
        self,
        mock_get,
        configurar_api_eol,
    ):
        """Deve preservar a situação de um cargo inativado manualmente."""
        CargoEOL.objects.create(
            codigo="1000",
            nome="Nome antigo",
            ativo=False,
        )

        resposta = Mock()
        resposta.raise_for_status.return_value = None
        resposta.json.return_value = [
            {
                "codigoCargo": 1000,
                "nomeCargo": "ASSISTENTE ADMINISTRATIVO",
            },
        ]

        mock_get.return_value = resposta

        call_command("sincronizar_cargos_eol")

        cargo = CargoEOL.objects.get(codigo="1000")

        assert cargo.nome == "ASSISTENTE ADMINISTRATIVO"
        assert cargo.ativo is False

    @patch(
        "apps.usuarios.management.commands.sincronizar_cargos_eol.requests.get"
    )
    def test_deve_preservar_perfil_e_ativo_do_cargo_existente(
        self,
        mock_get,
        configurar_api_eol,
    ):
        """Deve atualizar somente o nome do cargo existente."""
        CargoEOL.objects.create(
            codigo="1000",
            nome="Nome antigo",
            perfil=PerfilAcesso.UE,
            ativo=False,
        )

        resposta = Mock()
        resposta.raise_for_status.return_value = None
        resposta.json.return_value = [
            {
                "codigoCargo": 1000,
                "nomeCargo": "ASSISTENTE ADMINISTRATIVO ATUALIZADO",
            },
        ]

        mock_get.return_value = resposta

        call_command("sincronizar_cargos_eol")

        cargo = CargoEOL.objects.get(codigo="1000")

        assert cargo.nome == "ASSISTENTE ADMINISTRATIVO ATUALIZADO"
        assert cargo.perfil == PerfilAcesso.UE
        assert cargo.ativo is False

    @patch(
        "apps.usuarios.management.commands.sincronizar_cargos_eol.requests.get"
    )
    def test_deve_consultar_api_com_token(
        self,
        mock_get,
        resposta_api_cargos,
        configurar_api_eol,
    ):
        """Deve consultar a API EOL com o token configurado."""
        mock_get.return_value = resposta_api_cargos

        call_command("sincronizar_cargos_eol")

        mock_get.assert_called_once()

        argumentos = mock_get.call_args

        assert argumentos.kwargs["headers"]["accept"] == "application/json"
        assert argumentos.kwargs["headers"]["x-api-eol-key"] == "token-teste"

    @patch(
        "apps.usuarios.management.commands.sincronizar_cargos_eol.requests.get"
    )
    def test_deve_consultar_endpoint_de_cargos(
        self,
        mock_get,
        resposta_api_cargos,
        configurar_api_eol,
    ):
        """Deve consultar o endpoint de cargos da API EOL."""
        mock_get.return_value = resposta_api_cargos

        call_command("sincronizar_cargos_eol")

        mock_get.assert_called_once()

        url = mock_get.call_args.args[0]
        print(url)

        assert url == "https://api-eol-teste/cargos"

    @patch(
        "apps.usuarios.management.commands.sincronizar_cargos_eol.requests.get"
    )
    def test_deve_falhar_quando_api_retornar_erro(
        self,
        mock_get,
        configurar_api_eol,
    ):
        """Deve retornar erro quando a API externa falhar."""
        mock_get.side_effect = requests.RequestException(
            "Erro de conexão",
        )

        with pytest.raises(
            CommandError,
            match="Erro ao consultar a API EOL de cargos",
        ):
            call_command("sincronizar_cargos_eol")

    @patch(
        "apps.usuarios.management.commands.sincronizar_cargos_eol.requests.get"
    )
    def test_deve_falhar_quando_api_retornar_json_invalido(
        self,
        mock_get,
        configurar_api_eol,
    ):
        """Deve falhar quando a API retornar JSON inválido."""
        resposta = Mock()
        resposta.raise_for_status.return_value = None
        resposta.json.side_effect = ValueError

        mock_get.return_value = resposta

        with pytest.raises(
            CommandError,
            match="A API EOL de cargos retornou um JSON inválido",
        ):
            call_command("sincronizar_cargos_eol")

    @patch(
        "apps.usuarios.management.commands.sincronizar_cargos_eol.requests.get"
    )
    def test_deve_falhar_quando_api_nao_retornar_lista(
        self,
        mock_get,
        configurar_api_eol,
    ):
        """Deve falhar quando a API não retornar uma lista."""
        resposta = Mock()
        resposta.raise_for_status.return_value = None
        resposta.json.return_value = {
            "codigoCargo": 1000,
            "nomeCargo": "ASSISTENTE ADMINISTRATIVO",
        }

        mock_get.return_value = resposta

        with pytest.raises(
            CommandError,
            match="A API EOL de cargos deveria retornar uma lista",
        ):
            call_command("sincronizar_cargos_eol")

    def test_deve_falhar_sem_url_da_api(self):
        """Deve falhar quando a URL da API não estiver configurada."""
        with (
            patch(
                "apps.usuarios.management.commands."
                "sincronizar_cargos_eol.SME_API_EOL_URL",
                "",
            ),
            pytest.raises(
                CommandError,
                match="SME_API_EOL_URL",
            ),
        ):
            call_command("sincronizar_cargos_eol")

    def test_deve_falhar_sem_token_da_api(self):
        """Deve falhar quando o token da API não estiver configurado."""
        with (
            patch(
                "apps.usuarios.management.commands."
                "sincronizar_cargos_eol.SME_API_EOL_TOKEN",
                "",
            ),
            pytest.raises(
                CommandError,
                match="SME_API_EOL_TOKEN",
            ),
        ):
            call_command("sincronizar_cargos_eol")

    def test_deve_falhar_quando_registro_nao_for_um_dicionario(self):
        """Deve rejeitar registro que não seja um objeto."""
        from apps.usuarios.management.commands.sincronizar_cargos_eol import (
            Command,
        )

        with pytest.raises(
            CommandError,
            match="não é um objeto",
        ):
            Command._validar_registro("registro inválido")

    def test_deve_falhar_quando_campo_obrigatorio_estiver_ausente(self):
        """Deve rejeitar registro com campo obrigatório ausente."""
        from apps.usuarios.management.commands.sincronizar_cargos_eol import (
            Command,
        )

        with pytest.raises(
            CommandError,
            match="Campos ausentes: nomeCargo",
        ):
            Command._validar_registro(
                {
                    "codigoCargo": 1000,
                }
            )

    def test_deve_falhar_quando_codigo_nao_for_inteiro(self):
        """Deve rejeitar código que não seja inteiro."""
        from apps.usuarios.management.commands.sincronizar_cargos_eol import (
            Command,
        )

        with pytest.raises(
            CommandError,
            match="Campo 'codigoCargo' inválido",
        ):
            Command._validar_registro(
                {
                    "codigoCargo": "1000",
                    "nomeCargo": "ASSISTENTE ADMINISTRATIVO",
                }
            )

    def test_deve_falhar_quando_nome_nao_for_string(self):
        """Deve rejeitar nome que não seja uma string."""
        from apps.usuarios.management.commands.sincronizar_cargos_eol import (
            Command,
        )

        with pytest.raises(
            CommandError,
            match="Campo 'nomeCargo' inválido",
        ):
            Command._validar_registro(
                {
                    "codigoCargo": 1000,
                    "nomeCargo": 123,
                }
            )

    def test_deve_falhar_quando_nome_for_vazio(self):
        """Deve rejeitar nome vazio."""
        from apps.usuarios.management.commands.sincronizar_cargos_eol import (
            Command,
        )

        with pytest.raises(
            CommandError,
            match="Campo 'nomeCargo' não pode ser vazio",
        ):
            Command._validar_registro(
                {
                    "codigoCargo": 1000,
                    "nomeCargo": "   ",
                }
            )

    def test_deve_aceitar_registro_valido(self):
        """Deve aceitar um registro válido."""
        from apps.usuarios.management.commands.sincronizar_cargos_eol import (
            Command,
        )

        Command._validar_registro(
            {
                "codigoCargo": 1000,
                "nomeCargo": "ASSISTENTE ADMINISTRATIVO",
            }
        )

    @patch(
        "apps.usuarios.management.commands.sincronizar_cargos_eol.requests.get"
    )
    def test_deve_reverter_importacao_quando_um_registro_for_invalido(
        self,
        mock_get,
        configurar_api_eol,
    ):
        """Deve desfazer alterações quando um registro for inválido."""
        CargoEOL.objects.all().delete()
        resposta = Mock()
        resposta.raise_for_status.return_value = None
        resposta.json.return_value = [
            {
                "codigoCargo": 1000,
                "nomeCargo": "ASSISTENTE ADMINISTRATIVO",
            },
            {
                "codigoCargo": "invalido",
                "nomeCargo": "CARGO INVÁLIDO",
            },
        ]

        mock_get.return_value = resposta

        with pytest.raises(
            CommandError,
            match="Campo 'codigoCargo' inválido",
        ):
            call_command("sincronizar_cargos_eol")

        assert not CargoEOL.objects.exists()

    @patch(
        "apps.usuarios.management.commands.sincronizar_cargos_eol.requests.get"
    )
    def test_deve_ser_idempotente(
        self,
        mock_get,
        resposta_api_cargos,
        configurar_api_eol,
    ):
        """Deve manter somente um registro para cada cargo."""
        CargoEOL.objects.all().delete()
        mock_get.return_value = resposta_api_cargos

        call_command("sincronizar_cargos_eol")
        call_command("sincronizar_cargos_eol")

        assert CargoEOL.objects.count() == 2

        diretor = CargoEOL.objects.get(codigo="1000")

        assert diretor.nome == "ASSISTENTE ADMINISTRATIVO"
        assert diretor.perfil == ""
        assert diretor.ativo is True
