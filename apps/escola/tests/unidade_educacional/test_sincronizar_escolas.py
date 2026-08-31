"""Testes do comando de sincronização de escolas."""

from unittest.mock import Mock, patch

import pytest
import requests
from django.core.management import CommandError, call_command

from apps.escola.constants import TIPO_ESCOLA_NAO_ACEITAS
from apps.escola.management.commands.sincronizar_escolas import Command
from apps.escola.models import (
    Unidadeeducacional,
)

pytestmark = pytest.mark.django_db


class TestSincronizarEscolas:
    """Testes do comando de sincronização de escolas."""

    def test_deve_falhar_sem_url_da_api(self):
        """Deve falhar quando a URL da API não estiver configurada."""
        with (
            patch(
                "apps.escola.management.commands.sincronizar_escolas."
                "SME_API_EOL_URL",
                "",
            ),
            pytest.raises(
                CommandError,
                match="SME_API_EOL_URL",
            ),
        ):
            call_command("sincronizar_escolas")

    def test_deve_falhar_sem_token_da_api(self):
        """Deve falhar quando o token da API não estiver configurado."""
        with (
            patch(
                "apps.escola.management.commands.sincronizar_escolas."
                "SME_API_EOL_TOKEN",
                "",
            ),
            pytest.raises(
                CommandError,
                match="SME_API_EOL_TOKEN",
            ),
        ):
            call_command("sincronizar_escolas")

    @patch("apps.escola.management.commands.sincronizar_escolas.requests.get")
    def test_deve_criar_escola(
        self,
        mock_get,
        respostas_api,
        diretoria_regional_centro,
        tipo_escola_emef,
        subprefeitura_se,
        configurar_api_eol,
    ):
        """Deve criar uma escola retornada pela API."""
        mock_get.side_effect = respostas_api

        call_command("sincronizar_escolas")

        assert Unidadeeducacional.objects.count() == 1

        escola = Unidadeeducacional.objects.get(
            codigo_eol="100001",
        )

        assert escola.nome == "EMEF Escola Teste"
        assert escola.diretoria_regional == diretoria_regional_centro
        assert escola.tipo_escola == tipo_escola_emef
        assert escola.subprefeitura == subprefeitura_se

    @patch("apps.escola.management.commands.sincronizar_escolas.requests.get")
    def test_deve_atualizar_escola_existente(
        self,
        mock_get,
        respostas_api,
        diretoria_regional_centro,
        tipo_escola_emef,
        subprefeitura_se,
        configurar_api_eol,
    ):
        """Deve atualizar uma escola existente."""
        escola = Unidadeeducacional.objects.create(
            codigo_eol="100001",
            nome="Nome Antigo",
            diretoria_regional=diretoria_regional_centro,
            tipo_escola=tipo_escola_emef,
            subprefeitura=subprefeitura_se,
        )

        mock_get.side_effect = respostas_api

        call_command("sincronizar_escolas")

        escola.refresh_from_db()

        assert escola.nome == "EMEF Escola Teste"
        assert Unidadeeducacional.objects.count() == 1

    @patch("apps.escola.management.commands.sincronizar_escolas.requests.get")
    def test_deve_consultar_api_com_token(
        self,
        mock_get,
        respostas_api,
        diretoria_regional_centro,
        tipo_escola_emef,
        subprefeitura_se,
        configurar_api_eol,
    ):
        """Deve consultar a API EOL com o token configurado."""
        mock_get.side_effect = respostas_api

        call_command("sincronizar_escolas")

        assert mock_get.call_count == 2

        chamada_escolas = mock_get.call_args_list[0]

        assert (
            chamada_escolas.kwargs["headers"]["x-api-eol-key"] == "token-teste"
        )
        assert (
            chamada_escolas.kwargs["headers"]["accept"] == "application/json"
        )

    @patch("apps.escola.management.commands.sincronizar_escolas.requests.get")
    def test_deve_consultar_api_de_subprefeitura(
        self,
        mock_get,
        respostas_api,
        diretoria_regional_centro,
        tipo_escola_emef,
        subprefeitura_se,
        configurar_api_eol,
    ):
        """Deve consultar a Subprefeitura específica da escola."""
        mock_get.side_effect = respostas_api

        call_command("sincronizar_escolas")

        chamada_subprefeitura = mock_get.call_args_list[1]
        info = "/escolas/100001/subprefeituras"
        assert info in (chamada_subprefeitura.args[0])

    @patch("apps.escola.management.commands.sincronizar_escolas.requests.get")
    def test_deve_ignorar_escola_com_tipo_nao_aceito(
        self,
        mock_get,
        configurar_api_eol,
        diretoria_regional_centro,
    ):
        """Deve ignorar escolas com tipo não aceito."""
        sigla_nao_aceita = next(iter(TIPO_ESCOLA_NAO_ACEITAS))

        resposta = Mock()
        resposta.raise_for_status.return_value = None
        resposta.json.return_value = [
            {
                "codigoEscola": "100001",
                "nomeEscola": "Escola Não Aceita",
                "nomeDRE": "Diretoria Regional Centro",
                "siglaDRE": "DRE",
                "codigoDRE": "DRE01",
                "tipoEscola": "Tipo não aceito",
                "siglaTipoEscola": sigla_nao_aceita,
            },
        ]

        mock_get.return_value = resposta

        call_command("sincronizar_escolas")

        assert not Unidadeeducacional.objects.exists()

        mock_get.assert_called_once()

    def test_deve_falhar_quando_registro_nao_for_um_dicionario(
        self,
    ):
        """Deve rejeitar registro que não seja um objeto."""
        with pytest.raises(
            CommandError,
            match="Um dos registros retornados pela API não é um objeto",
        ):
            Command._validar_registro("registro inválido")

    def test_deve_falhar_quando_campo_obrigatorio_estiver_ausente(
        self,
    ):
        """Deve rejeitar registro com campo obrigatório ausente."""
        with pytest.raises(
            CommandError,
            match="Campos ausentes: nomeEscola",
        ):
            Command._validar_registro(
                {
                    "codigoEscola": "100001",
                }
            )

    @pytest.mark.parametrize(
        "campo",
        [
            "codigoEscola",
            "nomeEscola",
            "nomeDRE",
            "siglaDRE",
            "codigoDRE",
            "tipoEscola",
            "siglaTipoEscola",
        ],
    )
    def test_deve_falhar_quando_campo_nao_for_string(
        self,
        campo,
    ):
        """Deve rejeitar campo obrigatório que não seja string."""
        registro = {
            "codigoEscola": "100001",
            "nomeEscola": "Escola Teste",
            "nomeDRE": "Diretoria Regional Centro",
            "siglaDRE": "DRE",
            "codigoDRE": "DRE01",
            "tipoEscola": "Escola Municipal",
            "siglaTipoEscola": "EMEF",
        }

        registro[campo] = 123

        with pytest.raises(
            CommandError,
            match=f"Campo '{campo}' inválido",
        ):
            Command._validar_registro(registro)

    @pytest.mark.parametrize(
        "campo",
        [
            "codigoEscola",
            "nomeEscola",
            "nomeDRE",
            "siglaDRE",
            "codigoDRE",
            "tipoEscola",
            "siglaTipoEscola",
        ],
    )
    def test_deve_falhar_quando_campo_obrigatorio_for_vazio(
        self,
        campo,
    ):
        """Deve rejeitar campo obrigatório vazio."""
        registro = {
            "codigoEscola": "100001",
            "nomeEscola": "Escola Teste",
            "nomeDRE": "Diretoria Regional Centro",
            "siglaDRE": "DRE",
            "codigoDRE": "DRE01",
            "tipoEscola": "Escola Municipal",
            "siglaTipoEscola": "EMEF",
        }

        registro[campo] = "   "

        with pytest.raises(
            CommandError,
            match=f"Campo '{campo}' não pode ser vazio",
        ):
            Command._validar_registro(registro)

    def test_deve_aceitar_registro_valido(self):
        """Deve aceitar um registro válido."""
        Command._validar_registro(
            {
                "codigoEscola": "100001",
                "nomeEscola": "Escola Teste",
                "nomeDRE": "Diretoria Regional Centro",
                "siglaDRE": "DRE",
                "codigoDRE": "DRE01",
                "tipoEscola": "Escola Municipal",
                "siglaTipoEscola": "EMEF",
            }
        )

    def test_deve_obter_dre_pelo_codigo(
        self,
        diretoria_regional_centro,
    ):
        """Deve retornar a DRE correspondente ao código."""
        resultado = Command._obter_dre("DRE01")

        assert resultado == diretoria_regional_centro

    def test_deve_falhar_quando_dre_nao_existir(self):
        """Deve falhar quando a DRE não existir."""
        from apps.escola.exceptions import DadosEscolaError

        with pytest.raises(
            DadosEscolaError,
            match="Diretoria Regional com código 'DRE01' não encontrada",
        ):
            Command._obter_dre("DRE01")

    def test_deve_obter_tipo_escola_emef_pela_sigla(
        self,
        tipo_escola_emef,
    ):
        """Deve retornar o tipo de escola correspondente à sigla."""
        resultado = Command._obter_tipo_escola("EMEF")

        assert resultado == tipo_escola_emef

    def test_deve_falhar_quando_tipo_escola_emef_nao_existir(self):
        """Deve falhar quando o tipo de escola não existir."""
        from apps.escola.exceptions import DadosEscolaError

        with pytest.raises(
            DadosEscolaError,
            match="Tipo de escola com sigla 'EMEF' não encontrado",
        ):
            Command._obter_tipo_escola("EMEF")

    @patch("apps.escola.management.commands.sincronizar_escolas.requests.get")
    def test_deve_obter_subprefeitura_da_escola(
        self,
        mock_get,
        resposta_api_subprefeituras,
        subprefeitura_se,
        configurar_api_eol,
    ):
        """Deve retornar a Subprefeitura vinculada à escola."""
        mock_get.return_value = resposta_api_subprefeituras

        resultado = Command._obter_subprefeitura(
            base_url="https://api-eol-teste",
            headers={
                "accept": "application/json",
                "x-api-eol-key": "token-teste",
            },
            codigo_escola="100001",
        )

        assert resultado == subprefeitura_se

    @patch("apps.escola.management.commands.sincronizar_escolas.requests.get")
    def test_deve_falhar_quando_api_de_subprefeitura_retornar_json_invalido(
        self,
        mock_get,
    ):
        """Deve falhar quando a API de Subprefeitura retornar JSON inválido."""
        resposta = Mock()
        resposta.raise_for_status.return_value = None
        resposta.json.side_effect = ValueError
        mock_get.return_value = resposta

        with pytest.raises(
            CommandError,
            match="A API de Subprefeitura retornou um JSON inválido",
        ):
            Command._obter_subprefeitura(
                base_url="https://api-eol-teste",
                headers={},
                codigo_escola="100001",
            )

    @patch("apps.escola.management.commands.sincronizar_escolas.requests.get")
    def test_deve_falhar_quando_api_de_subprefeitura_nao_retornar_lista(
        self,
        mock_get,
    ):
        """Deve falhar quando a API não retornar uma lista."""
        resposta = Mock()
        resposta.raise_for_status.return_value = None
        resposta.json.return_value = {
            "codigoSubprefeitura": "SP01",
        }
        mock_get.return_value = resposta

        with pytest.raises(
            CommandError,
            match="A API de Subprefeitura deveria retornar uma lista",
        ):
            Command._obter_subprefeitura(
                base_url="https://api-eol-teste",
                headers={},
                codigo_escola="100001",
            )

    @patch("apps.escola.management.commands.sincronizar_escolas.requests.get")
    def test_deve_retornar_none_quando_nao_houver_subprefeitura(
        self,
        mock_get,
    ):
        """Deve retornar None quando nenhuma Subprefeitura for retornada."""
        resposta = Mock()
        resposta.raise_for_status.return_value = None
        resposta.json.return_value = []
        mock_get.return_value = resposta

        resultado = Command._obter_subprefeitura(
            base_url="https://api-eol-teste",
            headers={},
            codigo_escola="100001",
        )

        assert resultado is None

    @patch("apps.escola.management.commands.sincronizar_escolas.requests.get")
    def test_deve_retornar_none_quando_subprefeitura_nao_existir_no_banco(
        self,
        mock_get,
    ):
        """Deve retornar None quando a Subprefeitura não existir no banco."""
        resposta = Mock()
        resposta.raise_for_status.return_value = None
        resposta.json.return_value = [
            {
                "codigoSubprefeitura": "SP99",
                "nomeSubprefeitura": "Subprefeitura Inexistente",
            },
        ]
        mock_get.return_value = resposta

        resultado = Command._obter_subprefeitura(
            base_url="https://api-eol-teste",
            headers={},
            codigo_escola="100001",
        )

        assert resultado is None

    @patch("apps.escola.management.commands.sincronizar_escolas.requests.get")
    def test_deve_falhar_quando_api_principal_retornar_erro(
        self,
        mock_get,
        configurar_api_eol,
    ):
        """Deve falhar quando a API principal retornar erro."""
        mock_get.side_effect = requests.RequestException(
            "Erro de conexão",
        )

        with pytest.raises(
            CommandError,
            match="Erro ao consultar a API EOL de escolas",
        ):
            call_command("sincronizar_escolas")

    @patch("apps.escola.management.commands.sincronizar_escolas.requests.get")
    def test_deve_falhar_quando_api_principal_retornar_json_invalido(
        self,
        mock_get,
        configurar_api_eol,
    ):
        """Deve falhar quando a API principal retornar JSON inválido."""
        resposta = Mock()
        resposta.raise_for_status.return_value = None
        resposta.json.side_effect = ValueError
        mock_get.return_value = resposta

        with pytest.raises(
            CommandError,
            match="A API EOL de escolas retornou um JSON inválido",
        ):
            call_command("sincronizar_escolas")

    @patch("apps.escola.management.commands.sincronizar_escolas.requests.get")
    def test_deve_falhar_quando_api_principal_nao_retornar_lista(
        self,
        mock_get,
        configurar_api_eol,
    ):
        """Deve falhar quando a API principal não retornar uma lista."""
        resposta = Mock()
        resposta.raise_for_status.return_value = None
        resposta.json.return_value = {
            "codigoEscola": "100001",
        }
        mock_get.return_value = resposta

        with pytest.raises(
            CommandError,
            match="A API EOL de escolas deveria retornar uma lista",
        ):
            call_command("sincronizar_escolas")

    @patch("apps.escola.management.commands.sincronizar_escolas.requests.get")
    def test_deve_falhar_quando_api_de_subprefeitura_retornar_erro(
        self,
        mock_get,
        resposta_api_escolas,
        diretoria_regional_centro,
        tipo_escola_emef,
        configurar_api_eol,
    ):
        """Deve falhar quando a API de Subprefeitura retornar erro."""
        mock_get.side_effect = [
            resposta_api_escolas,
            requests.RequestException("Erro de conexão"),
        ]

        with pytest.raises(
            CommandError,
            match="Erro ao consultar a Subprefeitura da escola",
        ):
            call_command("sincronizar_escolas")

    @patch("apps.escola.management.commands.sincronizar_escolas.requests.get")
    def test_deve_continuar_importacao_quando_dre_nao_existir(
        self,
        mock_get,
        resposta_api_subprefeituras,
        tipo_escola_emef,
        subprefeitura_se,
        configurar_api_eol,
        diretoria_regional_centro,
    ):
        """Deve continuar quando uma escola tiver DRE inexistente."""
        resposta = Mock()
        resposta.raise_for_status.return_value = None
        resposta.json.return_value = [
            {
                "codigoEscola": "100001",
                "nomeEscola": "Escola Com Erro",
                "nomeDRE": "DRE Inexistente",
                "siglaDRE": "DRE",
                "codigoDRE": "DRE99",
                "tipoEscola": "Escola Municipal",
                "siglaTipoEscola": "EMEF",
            },
            {
                "codigoEscola": "100002",
                "nomeEscola": "Escola Válida",
                "nomeDRE": "Diretoria Regional Centro",
                "siglaDRE": "DRE",
                "codigoDRE": "DRE01",
                "tipoEscola": "Escola Municipal",
                "siglaTipoEscola": "EMEF",
            },
        ]

        resposta_subprefeitura = resposta_api_subprefeituras

        mock_get.side_effect = [
            resposta,
            resposta_subprefeitura,
        ]

        call_command("sincronizar_escolas")

        assert Unidadeeducacional.objects.count() == 1

        escola = Unidadeeducacional.objects.get(
            codigo_eol="100002",
        )

        assert escola.nome == "EMEF Escola Válida"
        assert escola.diretoria_regional == diretoria_regional_centro
        assert escola.tipo_escola == tipo_escola_emef
        assert escola.subprefeitura == subprefeitura_se

    @patch("apps.escola.management.commands.sincronizar_escolas.requests.get")
    def test_deve_falhar_quando_registro_subprefeitura_nao_for_um_dicionario(
        self,
        mock_get,
    ):
        """Deve rejeitar registro de Subprefeitura que não seja um objeto."""
        resposta = Mock()
        resposta.raise_for_status.return_value = None
        resposta.json.return_value = [
            "registro inválido",
        ]

        mock_get.return_value = resposta

        with pytest.raises(
            CommandError,
            match="O registro de Subprefeitura retornado pela API é inválido",
        ):
            Command._obter_subprefeitura(
                base_url="https://api-eol-teste",
                headers={
                    "accept": "application/json",
                    "x-api-eol-key": "token-teste",
                },
                codigo_escola="100001",
            )

    @pytest.mark.parametrize(
        "codigo",
        [
            123,
            "",
            "   ",
        ],
    )
    @patch("apps.escola.management.commands.sincronizar_escolas.requests.get")
    def test_deve_falhar_quando_codigo_subprefeitura_for_invalido(
        self,
        mock_get,
        codigo,
    ):
        """Deve rejeitar código de Subprefeitura inválido."""
        resposta = Mock()
        resposta.raise_for_status.return_value = None
        resposta.json.return_value = [
            {
                "codigoSubprefeitura": codigo,
                "nomeSubprefeitura": "Subprefeitura Sé",
            },
        ]

        mock_get.return_value = resposta

        with pytest.raises(
            CommandError,
            match="Campo 'codigoSubprefeitura' inválido",
        ):
            Command._obter_subprefeitura(
                base_url="https://api-eol-teste",
                headers={
                    "accept": "application/json",
                    "x-api-eol-key": "token-teste",
                },
                codigo_escola="100001",
            )

    @pytest.mark.parametrize(
        "nome",
        [
            123,
            "",
            "   ",
        ],
    )
    @patch("apps.escola.management.commands.sincronizar_escolas.requests.get")
    def test_deve_falhar_quando_nome_subprefeitura_for_invalido(
        self,
        mock_get,
        nome,
    ):
        """Deve rejeitar nome de Subprefeitura inválido."""
        resposta = Mock()
        resposta.raise_for_status.return_value = None
        resposta.json.return_value = [
            {
                "codigoSubprefeitura": "SP01",
                "nomeSubprefeitura": nome,
            },
        ]

        mock_get.return_value = resposta

        with pytest.raises(
            CommandError,
            match="Campo 'nomeSubprefeitura' inválido",
        ):
            Command._obter_subprefeitura(
                base_url="https://api-eol-teste",
                headers={
                    "accept": "application/json",
                    "x-api-eol-key": "token-teste",
                },
                codigo_escola="100001",
            )

    @pytest.mark.parametrize(
        "registro,campo_ausente",
        [
            (
                {
                    "nomeSubprefeitura": "Subprefeitura Sé",
                },
                "codigoSubprefeitura",
            ),
            (
                {
                    "codigoSubprefeitura": "SP01",
                },
                "nomeSubprefeitura",
            ),
        ],
    )
    @patch("apps.escola.management.commands.sincronizar_escolas.requests.get")
    def test_deve_falhar_quando_campo_obrigatorio_subpref_estiver_ausente(
        self,
        mock_get,
        registro,
        campo_ausente,
    ):
        """Deve rejeitar registro de Subprefeitura com campo ausente."""
        resposta = Mock()
        resposta.raise_for_status.return_value = None
        resposta.json.return_value = [registro]
        mock_get.return_value = resposta

        with pytest.raises(
            CommandError,
            match=f"Campos ausentes: {campo_ausente}",
        ):
            Command._obter_subprefeitura(
                base_url="https://api-eol-teste",
                headers={
                    "accept": "application/json",
                    "x-api-eol-key": "token-teste",
                },
                codigo_escola="100001",
            )

    @patch("apps.escola.management.commands.sincronizar_escolas.requests.get")
    def test_deve_exibir_progresso_a_cada_500_escolas(
        self,
        mock_get,
        diretoria_regional_centro,
        tipo_escola_emef,
        subprefeitura_se,
        configurar_api_eol,
    ):
        """Deve atualizar o progresso ao processar 500 escolas."""
        escolas = [
            {
                "codigoEscola": str(numero),
                "nomeEscola": f"Escola {numero}",
                "nomeDRE": diretoria_regional_centro.nome,
                "siglaDRE": "DRE",
                "codigoDRE": diretoria_regional_centro.codigo,
                "tipoEscola": "Escola Municipal",
                "siglaTipoEscola": tipo_escola_emef.sigla,
            }
            for numero in range(1, 501)
        ]

        resposta_escolas = Mock()
        resposta_escolas.raise_for_status.return_value = None
        resposta_escolas.json.return_value = escolas

        resposta_subprefeitura = Mock()
        resposta_subprefeitura.raise_for_status.return_value = None
        resposta_subprefeitura.json.return_value = [
            {
                "codigoSubprefeitura": subprefeitura_se.codigo_eol,
                "nomeSubprefeitura": subprefeitura_se.nome,
            }
        ]

        mock_get.side_effect = [
            resposta_escolas,
            *([resposta_subprefeitura] * 500),
        ]

        call_command("sincronizar_escolas")

        assert Unidadeeducacional.objects.count() == 500
