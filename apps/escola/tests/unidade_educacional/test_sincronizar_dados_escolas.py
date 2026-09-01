"""Testes do comando de sincronização dos dados das unidades educacionais."""

from unittest.mock import Mock, patch

import pytest
import requests
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.escola.management.commands.sincronizar_dados_escolas import (
    Command,
)
from apps.escola.models import (
    DadosUnidadeEducacional,
    Unidadeeducacional,
)

pytestmark = pytest.mark.django_db


class TestSincronizarDadosUnidadesEducacionais:
    """Testes do comando de sincronização dos dados das unidades."""

    BASE_URL = "https://api-teste"
    HEADERS = {
        "accept": "application/json",
        "x-api-eol-key": "token-teste",
    }

    DADOS_API = {
        "nomeDRE": "DIRETORIA REGIONAL DE EDUCACAO SAO MIGUEL",
        "siglaDRE": "DRE - MP",
        "codigoDRE": "109300",
        "codigoINEP": "35055256",
        "siglaTipoEscola": "EMEF        ",
        "nome": "FERNANDO DE AZEVEDO, PROF.",
        "nomeExibicao": "FERNANDO DE AZEVEDO, PROF.",
        "codigo": "093777",
        "tipoUnidade": "ESCOLA",
        "email": "escolaemef@mail.com",
        "telefone": "12345678",
        "tipoLogradouro": "Rua",
        "logradouro": "LOGRADOURO",
        "numero": "001",
        "bairro": "BAIRRO TESTE",
        "cep": 8032450,
        "municipio": "SAO PAULO",
        "uf": "SP",
        "tipoUnidadeAdm": 24,
        "descTipoUnidadeAdm": "DIRETORIA REGIONAL DE EDUCACAO",
    }

    def test_deve_falhar_sem_url_da_api(self):
        """Deve falhar quando a URL da API não estiver configurada."""
        with (
            patch(
                "apps.escola.management.commands."
                "sincronizar_dados_escolas."
                "SME_API_EOL_URL",
                "",
            ),
            pytest.raises(
                CommandError,
                match="SME_API_EOL_URL",
            ),
        ):
            call_command(
                "sincronizar_dados_escolas",
            )

    def test_deve_falhar_sem_token_da_api(self):
        """Deve falhar quando o token da API não estiver configurado."""
        with (
            patch(
                "apps.escola.management.commands."
                "sincronizar_dados_escolas."
                "SME_API_EOL_TOKEN",
                "",
            ),
            pytest.raises(
                CommandError,
                match="SME_API_EOL_TOKEN",
            ),
        ):
            call_command(
                "sincronizar_dados_escolas",
            )

    def test_deve_finalizar_sem_unidades(
        self,
        configurar_api_eol,
    ):
        """Deve finalizar quando não houver unidades cadastradas."""
        with pytest.raises(
            CommandError,
            match="Nenhuma unidade educacional cadastrada",
        ):
            call_command(
                "sincronizar_dados_escolas",
            )

        assert DadosUnidadeEducacional.objects.count() == 0

    @patch(
        "apps.escola.management.commands."
        "sincronizar_dados_escolas.requests.get"
    )
    def test_deve_criar_dados_da_unidade(
        self,
        mock_get,
        resposta_dados_unidade,
        unidade_educacional_emef,
        configurar_api_eol,
    ):
        """Deve criar os dados da unidade retornados pela API."""
        mock_get.return_value = resposta_dados_unidade

        call_command(
            "sincronizar_dados_escolas",
        )

        assert DadosUnidadeEducacional.objects.count() == 1

        dados = DadosUnidadeEducacional.objects.get(
            unidade_educacional=unidade_educacional_emef,
        )

        assert dados.email == "escolaemef@mail.com"
        assert dados.telefone == "12345678"
        assert dados.logradouro == "RUA LOGRADOURO"
        assert dados.numero == "001"
        assert dados.bairro == "BAIRRO TESTE"
        assert dados.cep == "08032450"
        assert dados.municipio == "SAO PAULO"
        assert dados.uf == "SP"

    @patch(
        "apps.escola.management.commands."
        "sincronizar_dados_escolas.requests.get"
    )
    def test_deve_atualizar_dados_da_unidade_existente(
        self,
        mock_get,
        resposta_dados_unidade,
        unidade_educacional_emef,
        configurar_api_eol,
    ):
        """Deve atualizar os dados existentes da unidade."""
        dados_existentes = DadosUnidadeEducacional.objects.create(
            unidade_educacional=unidade_educacional_emef,
            email="antigo@email.com",
            telefone="11111111",
            logradouro="Avenida ANTIGA",
            numero="100",
            bairro="BAIRRO ANTIGO",
            cep="01000000",
            municipio="SAO PAULO",
            uf="SP",
        )

        mock_get.return_value = resposta_dados_unidade

        call_command(
            "sincronizar_dados_escolas",
        )

        dados_existentes.refresh_from_db()

        assert dados_existentes.email == ("escolaemef@mail.com")
        assert dados_existentes.telefone == "12345678"
        assert dados_existentes.logradouro == "RUA LOGRADOURO"
        assert dados_existentes.numero == "001"
        assert dados_existentes.bairro == "BAIRRO TESTE"
        assert dados_existentes.cep == "08032450"
        assert dados_existentes.municipio == "SAO PAULO"
        assert dados_existentes.uf == "SP"

        assert DadosUnidadeEducacional.objects.count() == 1

    @patch(
        "apps.escola.management.commands."
        "sincronizar_dados_escolas.requests.get"
    )
    def test_deve_consultar_endpoint_com_codigo_eol(
        self,
        mock_get,
        resposta_dados_unidade,
        unidade_educacional_emef,
        configurar_api_eol,
    ):
        """Deve consultar o endpoint utilizando o código EOL."""
        mock_get.return_value = resposta_dados_unidade

        call_command(
            "sincronizar_dados_escolas",
        )

        mock_get.assert_called_once()

        url = mock_get.call_args.args[0]

        assert f"/escolas/dados/{unidade_educacional_emef.codigo_eol}" in url

    @patch(
        "apps.escola.management.commands."
        "sincronizar_dados_escolas.requests.get"
    )
    def test_deve_consultar_api_com_token(
        self,
        mock_get,
        resposta_dados_unidade,
        unidade_educacional_emef,
        configurar_api_eol,
    ):
        """Deve consultar a API EOL com o token configurado."""
        mock_get.return_value = resposta_dados_unidade

        call_command(
            "sincronizar_dados_escolas",
        )

        argumentos = mock_get.call_args

        assert argumentos.kwargs["headers"]["x-api-eol-key"] == "token-teste"
        assert argumentos.kwargs["headers"]["accept"] == "application/json"

    def test_deve_extrair_somente_campos_necessarios(self):
        """Deve extrair somente os campos que serão persistidos."""
        resultado = Command()._extrair_dados(
            self.DADOS_API,
        )

        assert set(resultado.keys()) == {
            "email",
            "telefone",
            "logradouro",
            "numero",
            "bairro",
            "cep",
            "municipio",
            "uf",
        }

    def test_deve_extrair_dados_corretamente(self):
        """Deve extrair e normalizar os dados da API."""
        resultado = Command()._extrair_dados(
            {
                **self.DADOS_API,
                "email": "  escola@email.com  ",
                "telefone": " 11999999999 ",
                "tipoLogradouro": " Rua ",
                "logradouro": " LOGRADOURO ",
                "numero": " 001 ",
                "bairro": " BAIRRO TESTE ",
                "municipio": " SAO PAULO ",
                "uf": " sp ",
            }
        )

        assert resultado == {
            "email": "escola@email.com",
            "telefone": "11999999999",
            "logradouro": "RUA LOGRADOURO",
            "numero": "001",
            "bairro": "BAIRRO TESTE",
            "cep": "08032450",
            "municipio": "SAO PAULO",
            "uf": "SP",
        }

    @pytest.mark.parametrize(
        "valor",
        [
            None,
            123,
            0,
            False,
            [],
            {},
        ],
    )
    def test_deve_normalizar_valor_nao_string_para_vazio(
        self,
        valor,
    ):
        """Deve converter valores não textuais para string vazia."""
        assert Command._normalizar_string(valor) == ""

    @pytest.mark.parametrize(
        "valor,resultado",
        [
            ("texto", "texto"),
            (" texto ", "texto"),
            ("   texto   ", "texto"),
            ("", ""),
            ("   ", ""),
        ],
    )
    def test_deve_normalizar_string(
        self,
        valor,
        resultado,
    ):
        """Deve remover espaços externos das strings."""
        assert Command._normalizar_string(valor) == resultado

    @pytest.mark.parametrize(
        "valor,resultado",
        [
            (8032450, "08032450"),
            (12345678, "12345678"),
            ("8032450", "8032450"),
            ("08032450", "08032450"),
            (" 08032450 ", "08032450"),
            (None, ""),
            (12.5, ""),
            ([], ""),
            ({}, ""),
        ],
    )
    def test_deve_normalizar_cep(
        self,
        valor,
        resultado,
    ):
        """Deve normalizar o CEP para armazenamento como string."""
        assert Command._normalizar_cep(valor) == resultado

    def test_deve_falhar_quando_registro_nao_for_um_dicionario(self):
        """Deve rejeitar registro que não seja um objeto."""
        with pytest.raises(
            CommandError,
            match="esperado um objeto",
        ):
            Command._validar_registro(
                "registro inválido",
                "100001",
            )

    def test_deve_falhar_quando_campo_obrigatorio_estiver_ausente(
        self,
    ):
        """Deve rejeitar registro com campo obrigatório ausente."""
        dados = self.DADOS_API.copy()
        del dados["email"]

        with pytest.raises(
            CommandError,
            match="Campos ausentes: email",
        ):
            Command._validar_registro(
                dados,
                "100001",
            )

    @pytest.mark.parametrize(
        "campo",
        [
            "email",
            "telefone",
            "tipoLogradouro",
            "logradouro",
            "numero",
            "bairro",
            "municipio",
            "uf",
        ],
    )
    def test_deve_falhar_quando_campo_string_tiver_tipo_invalido(
        self,
        campo,
    ):
        """Deve rejeitar campo textual com tipo inválido."""
        dados = self.DADOS_API.copy()
        dados[campo] = 123

        with pytest.raises(
            CommandError,
            match=f"Campo '{campo}' inválido",
        ):
            Command._validar_registro(
                dados,
                "100001",
            )

    @pytest.mark.parametrize(
        "valor",
        [
            None,
            "",
            "   ",
        ],
    )
    def test_deve_aceitar_campos_string_vazios(
        self,
        valor,
    ):
        """Deve aceitar campos textuais vazios ou nulos."""
        dados = self.DADOS_API.copy()

        for campo in (
            "email",
            "telefone",
            "tipoLogradouro",
            "logradouro",
            "numero",
            "bairro",
            "municipio",
            "uf",
        ):
            dados[campo] = valor

        Command._validar_registro(
            dados,
            "100001",
        )

    @pytest.mark.parametrize(
        "valor",
        [
            None,
            8032450,
            "8032450",
        ],
    )
    def test_deve_aceitar_cep_valido(
        self,
        valor,
    ):
        """Deve aceitar CEP numérico, textual ou nulo."""
        dados = self.DADOS_API.copy()
        dados["cep"] = valor

        Command._validar_registro(
            dados,
            "100001",
        )

    def test_deve_falhar_quando_cep_tiver_tipo_invalido(self):
        """Deve rejeitar CEP com tipo inválido."""
        dados = self.DADOS_API.copy()
        dados["cep"] = []

        with pytest.raises(
            CommandError,
            match="Campo 'cep' inválido",
        ):
            Command._validar_registro(
                dados,
                "100001",
            )

    def test_deve_aceitar_registro_valido(self):
        """Deve aceitar um registro válido."""
        Command._validar_registro(
            self.DADOS_API,
            "100001",
        )

    @patch(
        "apps.escola.management.commands."
        "sincronizar_dados_escolas.requests.get"
    )
    def test_deve_obter_dados_da_escola(
        self,
        mock_get,
    ):
        """Deve retornar os dados da escola obtidos da API."""
        resposta = Mock()
        resposta.status_code = 200
        resposta.json.return_value = self.DADOS_API
        mock_get.return_value = resposta

        resultado = Command._obter_dados_escola(
            base_url=self.BASE_URL,
            headers=self.HEADERS,
            codigo_eol="100001",
        )

        assert resultado == self.DADOS_API

        mock_get.assert_called_once()

        assert "/escolas/dados/100001" in mock_get.call_args.args[0]

    def test_deve_falhar_quando_api_retornar_erro(
        self,
    ):
        """Deve falhar quando a API retornar erro."""
        with (
            patch(
                "apps.escola.management.commands."
                "sincronizar_dados_escolas.requests.get",
                side_effect=requests.RequestException(
                    "Erro de conexão",
                ),
            ),
            pytest.raises(
                CommandError,
                match="Erro ao consultar a unidade 100001",
            ),
        ):
            Command._obter_dados_escola(
                base_url=self.BASE_URL,
                headers=self.HEADERS,
                codigo_eol="100001",
            )

    @pytest.mark.parametrize(
        "status_code",
        [
            400,
            401,
            403,
            404,
            500,
        ],
    )
    def test_deve_falhar_quando_api_retornar_status_invalido(
        self,
        status_code,
    ):
        """Deve falhar quando a API retornar status diferente de 200."""
        resposta = Mock()
        resposta.status_code = status_code
        resposta.raise_for_status.return_value = None

        with (
            patch(
                "apps.escola.management.commands."
                "sincronizar_dados_escolas.requests.get",
                return_value=resposta,
            ),
            pytest.raises(
                CommandError,
                match=f"HTTP {status_code}",
            ),
        ):
            Command._obter_dados_escola(
                base_url=self.BASE_URL,
                headers=self.HEADERS,
                codigo_eol="100001",
            )

    def test_deve_falhar_quando_api_retornar_json_invalido(
        self,
    ):
        """Deve falhar quando a API retornar JSON inválido."""
        resposta = Mock()
        resposta.status_code = 200
        resposta.json.side_effect = ValueError

        with (
            patch(
                "apps.escola.management.commands."
                "sincronizar_dados_escolas.requests.get",
                return_value=resposta,
            ),
            pytest.raises(
                CommandError,
                match="JSON inválido",
            ),
        ):
            Command._obter_dados_escola(
                base_url=self.BASE_URL,
                headers=self.HEADERS,
                codigo_eol="100001",
            )

    @pytest.mark.parametrize(
        "payload",
        [
            [],
            [],
            "texto",
            123,
            None,
        ],
    )
    def test_deve_falhar_quando_api_nao_retornar_objeto(
        self,
        payload,
    ):
        """Deve falhar quando a API não retornar um objeto."""
        resposta = Mock()
        resposta.status_code = 200
        resposta.json.return_value = payload

        with (
            patch(
                "apps.escola.management.commands."
                "sincronizar_dados_escolas.requests.get",
                return_value=resposta,
            ),
            pytest.raises(
                CommandError,
                match="deveria retornar um objeto",
            ),
        ):
            Command._obter_dados_escola(
                base_url=self.BASE_URL,
                headers=self.HEADERS,
                codigo_eol="100001",
            )

    @patch(
        "apps.escola.management.commands."
        "sincronizar_dados_escolas.requests.get"
    )
    def test_deve_nao_criar_dados_quando_api_falhar(
        self,
        mock_get,
        unidade_educacional_emef,
        configurar_api_eol,
    ):
        """Deve continuar a importação quando uma unidade falhar."""
        mock_get.side_effect = requests.RequestException(
            "Erro de conexão",
        )

        call_command(
            "sincronizar_dados_escolas",
        )

        assert not DadosUnidadeEducacional.objects.exists()

    @patch(
        "apps.escola.management.commands."
        "sincronizar_dados_escolas.requests.get"
    )
    def test_deve_processar_todas_as_unidades(
        self,
        mock_get,
        unidade_educacional_emef,
        diretoria_regional_centro,
        tipo_escola_emef,
        subprefeitura_se,
        configurar_api_eol,
    ):
        """Deve consultar todas as unidades educacionais cadastradas."""
        segunda_unidade = Unidadeeducacional.objects.create(
            codigo_eol="100002",
            nome="EMEF Segunda Escola",
            diretoria_regional=diretoria_regional_centro,
            tipo_escola=tipo_escola_emef,
            subprefeitura=subprefeitura_se,
        )

        primeira_resposta = Mock()
        primeira_resposta.status_code = 200
        primeira_resposta.json.return_value = self.DADOS_API

        segunda_resposta = Mock()
        segunda_resposta.status_code = 200
        segunda_resposta.json.return_value = {
            **self.DADOS_API,
            "codigo": "100002",
            "email": "segunda@email.com",
        }

        mock_get.side_effect = [
            primeira_resposta,
            segunda_resposta,
        ]

        call_command(
            "sincronizar_dados_escolas",
        )

        assert DadosUnidadeEducacional.objects.count() == 2

        primeira = DadosUnidadeEducacional.objects.get(
            unidade_educacional=unidade_educacional_emef,
        )

        segunda = DadosUnidadeEducacional.objects.get(
            unidade_educacional=segunda_unidade,
        )

        assert primeira.email == ("escolaemef@mail.com")
        assert segunda.email == "segunda@email.com"

    @patch(
        "apps.escola.management.commands."
        "sincronizar_dados_escolas.requests.get"
    )
    def test_deve_ser_idempotente(
        self,
        mock_get,
        resposta_dados_unidade,
        unidade_educacional_emef,
        configurar_api_eol,
    ):
        """Deve manter somente um registro para cada unidade."""
        mock_get.return_value = resposta_dados_unidade

        call_command(
            "sincronizar_dados_escolas",
        )

        call_command(
            "sincronizar_dados_escolas",
        )

        assert DadosUnidadeEducacional.objects.count() == 1

        dados = DadosUnidadeEducacional.objects.get(
            unidade_educacional=unidade_educacional_emef,
        )

        assert dados.email == ("escolaemef@mail.com")

    def test_deve_ignorar_campos_que_nao_serao_persistidos(self):
        """Deve remover campos adicionais da resposta da API."""
        resultado = Command()._extrair_dados(
            self.DADOS_API,
        )

        assert "nomeDRE" not in resultado
        assert "siglaDRE" not in resultado
        assert "codigoDRE" not in resultado
        assert "codigoINEP" not in resultado
        assert "siglaTipoEscola" not in resultado
        assert "nome" not in resultado
        assert "nomeExibicao" not in resultado
        assert "codigo" not in resultado
        assert "tipoUnidade" not in resultado
        assert "tipoUnidadeAdm" not in resultado
        assert "descTipoUnidadeAdm" not in resultado

    def test_deve_manter_unidade_educacional_no_relacionamento(
        self,
        unidade_educacional_emef,
    ):
        """Deve acessar a unidade pelo relacionamento."""
        dados = DadosUnidadeEducacional.objects.create(
            unidade_educacional=unidade_educacional_emef,
            email="escola@email.com",
            telefone="1122223333",
            logradouro="RUA LOGRADOURO",
            numero="001",
            bairro="BAIRRO TESTE",
            cep="08032450",
            municipio="SAO PAULO",
            uf="SP",
        )

        assert dados.unidade_educacional == unidade_educacional_emef
        assert unidade_educacional_emef.dados == dados

    def test_deve_remover_espacos_de_string(self):
        """Deve remover espaços das extremidades de uma string."""
        resultado = Command()._normalizar_string("  texto de teste  ")

        assert resultado == "texto de teste"
