"""Testes do comando de sincronização de diretores."""

from unittest.mock import Mock, patch

import pytest
import requests
from django.core.management import CommandError, call_command

from apps.escola.management.commands.sincronizar_diretores import Command
from apps.escola.models import HistoricoResponsavel, ResponsavelUnidade
from apps.escola.models.unidade_educacional import Unidadeeducacional
from apps.usuarios.models.cargo_eol import CargoEOL

pytestmark = pytest.mark.django_db


class TestSincronizarDiretores:
    """Testes do comando de sincronização de diretores."""

    BASE_URL = "https://api-teste"
    HEADERS = {"x-api-eol-key": "token"}
    REGISTRO = {
        "codigoRF": "0000016",
        "nomeServidor": "DIRETOR TESTE",
        "dataInicio": "02/15/2024 00:00:00",
        "dataFim": None,
        "cargo": "DIRETOR DE ESCOLA",
        "cdTipoFuncaoAtividade": 0,
        "estaAfastado": False,
        "funcaoExterno": 0,
        "tipoFuncaoExterno": 0,
    }

    def test_deve_falhar_sem_url_da_api(self):
        """Deve falhar quando a URL da API não estiver configurada."""
        with (
            patch(
                "apps.escola.management.commands.sincronizar_diretores."
                "SME_API_EOL_URL",
                "",
            ),
            pytest.raises(
                CommandError,
                match="SME_API_EOL_URL",
            ),
        ):
            call_command("sincronizar_diretores")

    def test_deve_falhar_sem_token_da_api(self):
        """Deve falhar quando o token da API não estiver configurado."""
        with (
            patch(
                "apps.escola.management.commands.sincronizar_diretores."
                "SME_API_EOL_TOKEN",
                "",
            ),
            pytest.raises(
                CommandError,
                match="SME_API_EOL_TOKEN",
            ),
        ):
            call_command("sincronizar_diretores")

    def test_deve_finalizar_sem_unidades(
        self,
        configurar_api_eol,
    ):
        """Deve finalizar quando não houver unidades cadastradas."""
        call_command("sincronizar_diretores")

        assert ResponsavelUnidade.objects.count() == 0
        assert HistoricoResponsavel.objects.count() == 0

    @patch(
        "apps.escola.management.commands.sincronizar_diretores.requests.get"
    )
    def test_deve_criar_diretor(
        self,
        mock_get,
        resposta_api_diretor,
        resposta_dados_complementares,
        unidade_educacional_emef,
        obter_cargo_diretor,
        usuario_sincronizacao,
        configurar_api_eol,
    ):
        """Deve criar o responsável e seu vínculo com a unidade."""
        mock_get.side_effect = [
            resposta_api_diretor,
            resposta_dados_complementares,
        ]

        call_command("sincronizar_diretores")

        assert ResponsavelUnidade.objects.count() == 1
        assert HistoricoResponsavel.objects.count() == 1

        responsavel = ResponsavelUnidade.objects.get(
            registro_funcional="0000011",
        )

        assert responsavel.nome == "Diretor Escola"
        assert responsavel.email == "diretor.um@email.com"
        assert responsavel.telefone == "1122223333"
        assert responsavel.esta_afastado is False
        assert responsavel.criado_por == usuario_sincronizacao
        assert responsavel.atualizado_por == usuario_sincronizacao

        historico = HistoricoResponsavel.objects.get(
            responsavel=responsavel,
        )

        assert historico.unidade_educacional == unidade_educacional_emef
        assert historico.cargo == obter_cargo_diretor
        assert historico.ativo is True
        assert historico.criado_por == usuario_sincronizacao
        assert historico.atualizado_por == usuario_sincronizacao

    @patch(
        "apps.escola.management.commands.sincronizar_diretores.requests.get"
    )
    def test_deve_selecionar_diretor_com_data_inicio_mais_recente(
        self,
        mock_get,
        resposta_dados_complementares,
        unidade_educacional_emef,
        obter_cargo_diretor,
        usuario_sincronizacao,
        configurar_api_eol,
    ):
        """Deve selecionar o diretor com a data de início mais recente."""
        resposta_diretores = Mock()
        resposta_diretores.status_code = 200
        resposta_diretores.json.return_value = [
            {
                "codigoRF": "0000014",
                "nomeServidor": "DIRETOR A",
                "dataInicio": "02/15/2008 00:00:00",
                "dataFim": None,
                "cargo": "DIRETOR DE ESCOLA",
                "cdTipoFuncaoAtividade": 0,
                "estaAfastado": False,
                "funcaoExterno": 0,
                "tipoFuncaoExterno": 0,
            },
            {
                "codigoRF": "0000034",
                "nomeServidor": "DIRETOR B",
                "dataInicio": "10/18/2021 00:00:00",
                "dataFim": None,
                "cargo": "DIRETOR DE ESCOLA",
                "cdTipoFuncaoAtividade": 0,
                "estaAfastado": False,
                "funcaoExterno": 0,
                "tipoFuncaoExterno": 0,
            },
        ]

        mock_get.side_effect = [
            resposta_diretores,
            resposta_dados_complementares,
        ]

        call_command("sincronizar_diretores")

        assert ResponsavelUnidade.objects.count() == 1

        responsavel = ResponsavelUnidade.objects.get()

        assert responsavel.registro_funcional == "0000034"
        assert responsavel.nome == "DIRETOR B"

    @patch(
        "apps.escola.management.commands.sincronizar_diretores.requests.get"
    )
    def test_deve_salvar_campos_vazios_quando_api_retornar_none(
        self,
        mock_get,
        resposta_api_diretor,
        resposta_dados_complementares,
        unidade_educacional_emef,
        usuario_sincronizacao,
        configurar_api_eol,
    ):
        """Deve salvar email e telefone vazios quando a API retornar None."""
        resposta_dados_complementares.json.return_value = {
            **resposta_dados_complementares.json.return_value,
            "email": None,
            "telefoneUe": None,
        }

        mock_get.side_effect = [
            resposta_api_diretor,
            resposta_dados_complementares,
        ]

        call_command("sincronizar_diretores")

        responsavel = ResponsavelUnidade.objects.get()

        assert responsavel.email == ""
        assert responsavel.telefone == ""

    @patch(
        "apps.escola.management.commands.sincronizar_diretores.requests.get"
    )
    def test_deve_manter_campos_vazios_quando_api_retornar_string_vazia(
        self,
        mock_get,
        resposta_api_diretor,
        resposta_dados_complementares,
        unidade_educacional_emef,
        usuario_sincronizacao,
        configurar_api_eol,
    ):
        """Deve salvar email e telefone vazios quando a API retornar vazio."""
        resposta_dados_complementares.json.return_value = {
            **resposta_dados_complementares.json.return_value,
            "email": "",
            "telefoneUe": "",
        }

        mock_get.side_effect = [
            resposta_api_diretor,
            resposta_dados_complementares,
        ]

        call_command("sincronizar_diretores")

        responsavel = ResponsavelUnidade.objects.get()

        assert responsavel.email == ""
        assert responsavel.telefone == ""

    def test_deve_falhar_quando_api_de_diretores_retornar_erro(
        self,
        configurar_api_eol,
        unidade_educacional_emef,
    ):
        """Deve retornar erro quando a API de diretores falhar."""
        response = Mock()
        response.status_code = 500

        with patch(
            "apps.escola.management.commands.sincronizar_diretores.requests."
            "get",
            return_value=response,
        ):
            command = Command()
            with pytest.raises(CommandError, match="HTTP 500"):
                command._obter_dados_diretor(
                    base_url=self.BASE_URL,
                    headers=self.HEADERS,
                    codigo_escola=unidade_educacional_emef.codigo_eol,
                    codigo_diretor="3360",
                )

    def test_deve_falhar_quando_ocorrer_erro_na_consulta_do_diretor(
        self,
        configurar_api_eol,
        unidade_educacional_emef,
    ):
        """Deve retornar erro quando ocorrer falha na requisição."""
        with patch(
            "apps.escola.management.commands.sincronizar_diretores.requests."
            "get",
            side_effect=requests.RequestException("Erro de conexão"),
        ):
            command = Command()

            with pytest.raises(
                CommandError,
                match="Erro ao consultar o diretor",
            ):
                command._obter_dados_diretor(
                    base_url=self.BASE_URL,
                    headers=self.HEADERS,
                    codigo_escola=unidade_educacional_emef.codigo_eol,
                    codigo_diretor="3360",
                )

    def test_deve_falhar_com_json_invalido(
        self,
        configurar_api_eol,
        unidade_educacional_emef,
    ):
        """Deve retornar erro quando a API retornar JSON inválido."""
        response = Mock()
        response.status_code = 200
        response.json.side_effect = ValueError

        with patch(
            "apps.escola.management.commands.sincronizar_diretores.requests."
            "get",
            return_value=response,
        ):
            command = Command()

            with pytest.raises(
                CommandError,
                match="JSON inválido",
            ):
                command._obter_dados_diretor(
                    base_url=self.BASE_URL,
                    headers=self.HEADERS,
                    codigo_escola=unidade_educacional_emef.codigo_eol,
                    codigo_diretor="3360",
                )

    def test_deve_falhar_quando_api_nao_retornar_lista(
        self,
        configurar_api_eol,
        unidade_educacional_emef,
    ):
        """Deve retornar erro quando a API não retornar uma lista."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = {}

        with patch(
            "apps.escola.management.commands.sincronizar_diretores.requests."
            "get",
            return_value=response,
        ):
            command = Command()

            with pytest.raises(
                CommandError,
                match="deveria retornar uma lista",
            ):
                command._obter_dados_diretor(
                    base_url=self.BASE_URL,
                    headers=self.HEADERS,
                    codigo_escola=unidade_educacional_emef.codigo_eol,
                    codigo_diretor="3360",
                )

    def test_deve_retornar_none_quando_api_retornar_204(
        self,
        configurar_api_eol,
        unidade_educacional_emef,
    ):
        """Deve retornar None quando a escola não possuir diretor."""
        response = Mock()
        response.status_code = 204

        with patch(
            "apps.escola.management.commands.sincronizar_diretores.requests."
            "get",
            return_value=response,
        ):
            command = Command()

            resultado = command._obter_dados_diretor(
                base_url=self.BASE_URL,
                headers=self.HEADERS,
                codigo_escola=unidade_educacional_emef.codigo_eol,
                codigo_diretor="3360",
            )

        assert resultado is None

    @pytest.mark.parametrize(
        "campo",
        [
            "codigoRF",
            "nomeServidor",
            "cargo",
        ],
    )
    def test_deve_falhar_quando_campo_obrigatorio_for_vazio(
        self,
        unidade_educacional_emef,
        campo,
    ):
        """Deve rejeitar campo obrigatório vazio."""
        registro = self.REGISTRO.copy()
        registro[campo] = "   "

        with pytest.raises(
            CommandError,
            match=f"Campo '{campo}' não pode ser vazio",
        ):
            Command._validar_registro_diretor(
                registro, unidade_educacional_emef.codigo_eol
            )

    @pytest.mark.parametrize(
        "valor",
        [None, ""],
    )
    def test_deve_aceitar_data_inicio_vazia(
        self, valor, unidade_educacional_emef
    ):
        """Deve aceitar dataInicio nula ou vazia."""
        registro = self.REGISTRO.copy()
        registro["dataInicio"] = valor

        Command._validar_registro_diretor(
            registro, unidade_educacional_emef.codigo_eol
        )

    @pytest.mark.parametrize(
        "campo",
        ["email", "telefoneUe"],
    )
    def test_deve_aceitar_campo_adicional_vazio(
        self, campo, unidade_educacional_emef
    ):
        """Deve aceitar campos adicionais nulos ou vazios."""
        dados = {
            "email": "diretor@email.com",
            "telefoneUe": "11999999999",
        }

        dados[campo] = None

        Command._validar_dados_adicionais(
            dados, unidade_educacional_emef.codigo_eol, "0000012"
        )

    def test_deve_retornar_none_quando_todos_diretores_estiverem_encerrados(
        self,
        resposta_api_diretor,
        unidade_educacional_emef,
        configurar_api_eol,
    ):
        """Deve retornar None quando todos os vínculos estiverem encerrados."""
        registros = resposta_api_diretor.json()

        for registro in registros:
            registro["dataFim"] = "12/31/2024 00:00:00"

        resposta_api_diretor.json.return_value = registros

        with patch(
            "apps.escola.management.commands.sincronizar_diretores.requests."
            "get",
            return_value=resposta_api_diretor,
        ):
            resultado = Command()._obter_dados_diretor(
                base_url=self.BASE_URL,
                headers=self.HEADERS,
                codigo_escola=unidade_educacional_emef.codigo_eol,
                codigo_diretor="3360",
            )

        assert resultado is None

    @pytest.mark.parametrize(
        "registro",
        [
            None,
            [],
            "diretor",
            123,
        ],
    )
    def test_deve_falhar_quando_registro_nao_for_um_objeto(
        self,
        registro,
        resposta_api_diretor,
        unidade_educacional_emef,
        configurar_api_eol,
    ):
        """Deve falhar quando um registro de diretor não for um objeto."""
        resposta_api_diretor.json.return_value = [registro]

        with (
            patch(
                "apps.escola.management.commands.sincronizar_diretores."
                "requests."
                "get",
                return_value=resposta_api_diretor,
            ),
            pytest.raises(
                CommandError,
                match="esperado um objeto",
            ),
        ):
            Command()._obter_dados_diretor(
                base_url=self.BASE_URL,
                headers=self.HEADERS,
                codigo_escola=unidade_educacional_emef.codigo_eol,
                codigo_diretor="3360",
            )

    def test_deve_retornar_none_quando_api_retornar_lista_vazia(
        self,
        resposta_api_diretor,
        unidade_educacional_emef,
        obter_cargo_diretor,
    ):
        """Deve retornar None quando a API retornar uma lista vazia."""
        resposta_api_diretor.json.return_value = []

        with patch(
            "apps.escola.management.commands.sincronizar_diretores.requests."
            "get",
            return_value=resposta_api_diretor,
        ):
            resultado = Command()._obter_dados_diretor(
                base_url=self.BASE_URL,
                headers=self.HEADERS,
                codigo_escola=unidade_educacional_emef.codigo_eol,
                codigo_diretor=obter_cargo_diretor.codigo,
            )

        assert resultado is None

    @patch(
        "apps.escola.management.commands.sincronizar_diretores.requests.get"
    )
    def test_deve_falhar_quando_consulta_dados_complementares_der_erro(
        self,
        mock_get,
    ):
        """Deve transformar erro HTTP em CommandError."""
        mock_get.side_effect = requests.RequestException("Erro de conexão")

        with pytest.raises(
            CommandError,
            match="Erro ao consultar os dados adicionais",
        ):
            Command()._obter_dados_complementares(
                base_url=self.BASE_URL,
                headers=self.HEADERS,
                registro_funcional="0000014",
                codigo_escola="100001",
            )

    @patch(
        "apps.escola.management.commands.sincronizar_diretores.requests.get"
    )
    def test_deve_falhar_quando_api_de_dados_complementares_retornar_erro(
        self, mock_get
    ):
        """Deve lançar erro quando a API complementar retornar erro HTTP."""
        response = Mock()
        response.status_code = 500
        mock_get.return_value = response

        with pytest.raises(
            CommandError,
            match="API de autenticação retornou HTTP 500",
        ):
            Command()._obter_dados_complementares(
                base_url=self.BASE_URL,
                headers=self.HEADERS,
                registro_funcional="0000014",
                codigo_escola="100001",
            )

    @patch(
        "apps.escola.management.commands.sincronizar_diretores.requests.get"
    )
    def test_deve_falhar_com_json_invalido_nos_dados_complementares(
        self, mock_get
    ):
        """Deve lançar erro quando a API retornar JSON inválido."""
        response = Mock()
        response.status_code = 200
        response.json.side_effect = ValueError("JSON inválido")
        mock_get.return_value = response

        with pytest.raises(
            CommandError,
            match="A API de autenticação retornou JSON inválido",
        ):
            Command()._obter_dados_complementares(
                base_url=self.BASE_URL,
                headers=self.HEADERS,
                registro_funcional="0000014",
                codigo_escola="100001",
            )

    @pytest.mark.parametrize(
        "campo",
        [
            "codigoRF",
            "nomeServidor",
            "dataInicio",
            "dataFim",
            "cargo",
            "estaAfastado",
        ],
    )
    def test_deve_falhar_quando_campo_obrigatorio_estiver_ausente(
        self,
        campo,
    ):
        """Deve rejeitar campo obrigatório ausente."""
        registro = self.REGISTRO.copy()

        del registro[campo]

        with pytest.raises(
            CommandError,
            match=f"Campos ausentes: .*{campo}",
        ):
            Command._validar_registro_diretor(
                registro,
                "100001",
            )

    @pytest.mark.parametrize(
        "campo",
        ["codigoRF", "nomeServidor", "cargo"],
    )
    def test_deve_falhar_quando_campo_textual_tiver_tipo_invalido(
        self,
        campo,
    ):
        """Deve rejeitar campo textual com tipo inválido."""
        registro = self.REGISTRO.copy()
        registro[campo] = {}

        with pytest.raises(
            CommandError,
            match=(f"Campo '{campo}' inválido para a escola 100001"),
        ):
            Command._validar_registro_diretor(
                registro,
                "100001",
            )

    @pytest.mark.parametrize("campo", ["dataInicio", "dataFim"])
    def test_deve_falhar_quando_data_tiver_tipo_invalido(
        self,
        campo,
    ):
        """Deve rejeitar data com tipo diferente de string ou None."""
        registro = self.REGISTRO.copy()
        registro[campo] = 123

        with pytest.raises(
            CommandError,
            match=(f"Campo '{campo}' inválido para a escola 100001"),
        ):
            Command._validar_registro_diretor(
                registro,
                "100001",
            )

    @pytest.mark.parametrize(
        "valor",
        ["false", 0, 1, None, "true"],
    )
    def test_deve_falhar_quando_esta_afastado_nao_for_booleano(
        self,
        valor,
    ):
        """Deve rejeitar estaAfastado quando não for booleano."""
        registro = self.REGISTRO.copy()
        registro["estaAfastado"] = valor

        with pytest.raises(
            CommandError,
            match="Campo 'estaAfastado' inválido para a escola 100001",
        ):
            Command._validar_registro_diretor(
                registro,
                "100001",
            )

    def test_deve_contabilizar_unidade_sem_diretor(
        self,
        unidade_educacional_emef,
        obter_cargo_diretor,
    ):
        """Deve contabilizar unidades que não possuem diretor atual."""
        unidades = Mock()
        unidades.count.return_value = 1
        unidades.__iter__ = Mock(return_value=iter([unidade_educacional_emef]))

        with patch.object(
            Command,
            "_obter_dados_diretor",
            return_value=None,
        ):
            resultado = Command()._coletar_registros(
                base_url=self.BASE_URL,
                headers=self.HEADERS,
                unidades=unidades,
            )

        assert resultado == []

    def test_deve_ignorar_unidade_com_erro(
        self,
        unidade_educacional_emef,
        obter_cargo_diretor,
    ):
        """Deve continuar quando uma unidade gerar CommandError."""
        unidades = Mock()
        unidades.count.return_value = 1
        unidades.__iter__ = Mock(return_value=iter([unidade_educacional_emef]))

        with patch.object(
            Command,
            "_obter_dados_diretor",
            side_effect=CommandError("Erro de consulta"),
        ):
            resultado = Command()._coletar_registros(
                base_url=self.BASE_URL,
                headers=self.HEADERS,
                unidades=unidades,
            )

        assert resultado == []

    @pytest.mark.parametrize(
        "valor",
        [123, 0, False, [], {}],
    )
    def test_deve_normalizar_tipo_nao_string_para_vazio(
        self,
        valor,
    ):
        """Deve converter valores que não sejam string para vazio."""
        assert Command._normalizar_string(valor) == ""

    @patch(
        "apps.escola.management.commands.sincronizar_diretores.requests.get"
    )
    @pytest.mark.parametrize(
        "payload",
        [
            [],
            ["registro"],
            "texto",
            123,
            None,
        ],
    )
    def test_deve_falhar_quando_dados_complementares_nao_for_objeto(
        self,
        mock_get,
        payload,
    ):
        """Deve rejeitar payload que não seja um objeto."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = payload
        mock_get.return_value = response

        with pytest.raises(
            CommandError,
            match="A API de autenticação deveria retornar um objeto",
        ):
            Command()._obter_dados_complementares(
                base_url=self.BASE_URL,
                headers=self.HEADERS,
                registro_funcional="0000014",
                codigo_escola="100001",
            )

    @pytest.mark.parametrize(
        "campo",
        ["email", "telefoneUe"],
    )
    def test_deve_falhar_quando_campo_adicional_estiver_ausente(
        self,
        campo,
    ):
        """Deve rejeitar campo adicional ausente."""
        dados = {
            "email": "diretor@email.com",
            "telefoneUe": "20418371",
        }
        del dados[campo]

        with pytest.raises(
            CommandError,
            match=f"Campo '{campo}' ausente",
        ):
            Command._validar_dados_adicionais(
                dados=dados,
                codigo_escola="100001",
                registro_funcional="0000014",
            )

    @pytest.mark.parametrize(
        "campo",
        ["email", "telefoneUe"],
    )
    def test_deve_falhar_quando_campo_adicional_tiver_tipo_invalido(
        self,
        campo,
    ):
        """Deve rejeitar campo adicional com tipo inválido."""
        dados = {
            "email": "diretor@email.com",
            "telefoneUe": "20418371",
        }
        dados[campo] = {}

        with pytest.raises(
            CommandError,
            match=f"Campo '{campo}' inválido",
        ):
            Command._validar_dados_adicionais(
                dados=dados,
                codigo_escola="100001",
                registro_funcional="0000014",
            )

    def test_deve_falhar_quando_dados_adicionais_nao_for_objeto(
        self,
    ):
        """Deve rejeitar dados complementares que não sejam um objeto."""
        with pytest.raises(
            CommandError,
            match="Dados adicionais inválidos para o RF 0000014",
        ):
            Command._validar_dados_adicionais(
                dados=[],
                codigo_escola="100001",
                registro_funcional="0000014",
            )

    def test_deve_obter_cargo_pelo_codigo(
        self,
        obter_cargo_diretor,
    ):
        """Deve retornar o cargo correspondente ao código informado."""
        cargo = Command._obter_cargo(obter_cargo_diretor.codigo)

        assert cargo.pk == obter_cargo_diretor.pk
        assert cargo.codigo == obter_cargo_diretor.codigo

    def test_deve_falhar_quando_cargo_nao_existir(self):
        """Deve rejeitar código EOL de cargo inexistente."""
        with pytest.raises(
            CommandError,
            match="Cargo EOL com código '999999' não encontrado",
        ):
            Command._obter_cargo("999999")

    def test_deve_falhar_quando_cargo_diretor_nao_existir(
        self,
        cargo_perfil_diretor,
    ):
        """Deve falhar quando não houver cargo de diretor."""
        CargoEOL.objects.filter(nome="DIRETOR DE ESCOLA").delete()

        with pytest.raises(
            CommandError,
            match="Código EOL para DIRETOR DE ESCOLA não encontrado",
        ):
            Command()._obter_cargo_diretor()

    def test_deve_falhar_quando_existirem_dois_cargos_diretor(
        self,
        cargo_perfil_diretor,
    ):
        """Deve falhar quando houver mais de um cargo de diretor."""
        CargoEOL.objects.create(
            codigo="9998",
            nome="DIRETOR DE ESCOLA",
        )

        with pytest.raises(
            CommandError,
            match="Mais de um cargo DIRETOR DE ESCOLA",
        ):
            Command()._obter_cargo_diretor()

    def test_deve_atualizar_responsavel_existente(
        self,
        usuario_sincronizacao,
    ):
        """Deve atualizar um responsável existente."""
        responsavel = ResponsavelUnidade.objects.create(
            registro_funcional="0000014",
            nome="NOME ANTIGO",
            email="antigo@email.com",
            telefone="11111111",
            esta_afastado=False,
            criado_por=usuario_sincronizacao,
            atualizado_por=usuario_sincronizacao,
        )

        registro = {
            "registro_funcional": "0000014",
            "nome": "NOME NOVO",
            "email": "novo@email.com",
            "telefone": "22222222",
            "esta_afastado": True,
        }

        resultado, foi_criado = Command()._salvar_responsavel(
            registro=registro,
            usuario=usuario_sincronizacao,
        )

        responsavel.refresh_from_db()

        assert resultado.pk == responsavel.pk
        assert foi_criado is False
        assert responsavel.nome == "NOME NOVO"
        assert responsavel.email == "novo@email.com"
        assert responsavel.telefone == "22222222"
        assert responsavel.esta_afastado is True
        assert responsavel.atualizado_por == usuario_sincronizacao

    def test_deve_atualizar_historico_existente(
        self,
        usuario_sincronizacao,
        unidade_educacional_emef,
        cargo_perfil_diretor,
    ):
        """Deve reativar e atualizar o histórico existente."""
        responsavel = ResponsavelUnidade.objects.create(
            registro_funcional="0000014",
            nome="DIRETOR TESTE",
            email="diretor@email.com",
            telefone="11111111",
            esta_afastado=False,
            criado_por=usuario_sincronizacao,
            atualizado_por=usuario_sincronizacao,
        )

        historico = HistoricoResponsavel.objects.create(
            responsavel=responsavel,
            unidade_educacional=unidade_educacional_emef,
            cargo=cargo_perfil_diretor,
            ativo=False,
            criado_por=usuario_sincronizacao,
            atualizado_por=usuario_sincronizacao,
        )

        registro = {
            "unidade_educacional": unidade_educacional_emef,
            "cargo_diretor": cargo_perfil_diretor,
        }

        resultado, foi_criado = Command()._salvar_historico(
            responsavel=responsavel,
            registro=registro,
            usuario=usuario_sincronizacao,
        )

        historico.refresh_from_db()

        assert resultado.pk == historico.pk
        assert foi_criado is False
        assert historico.ativo is True
        assert historico.atualizado_por == usuario_sincronizacao

    def test_deve_exibir_progresso_a_cada_500_e_ao_finalizar(
        self,
        usuario_sincronizacao,
        configurar_api_eol,
        unidade_educacional_emef,
        obter_cargo_diretor,
    ):
        """Deve executar o branch de processamento a cada 500 registros."""
        registros = [
            {
                "registro_funcional": str(numero),
                "nome": f"DIRETOR {numero}",
                "email": "",
                "telefone": "",
                "esta_afastado": False,
                "unidade_educacional": unidade_educacional_emef,
                "cargo_diretor": obter_cargo_diretor,
            }
            for numero in range(1, 502)
        ]

        responsavel = Mock()
        historico = Mock()

        with (
            patch.object(
                Command,
                "_coletar_registros",
                return_value=registros,
            ),
            patch.object(
                Command,
                "_salvar_responsavel",
                return_value=(responsavel, True),
            ),
            patch.object(
                Command,
                "_salvar_historico",
                return_value=(historico, True),
            ),
        ):
            call_command("sincronizar_diretores")

        assert len(registros) == 501

    def test_deve_exibir_progresso_a_cada_500_unidades(
        self,
        diretoria_regional_centro,
        tipo_escola_emef,
        subprefeitura_se,
        configurar_api_eol,
        usuario_sincronizacao,
        obter_cargo_diretor,
    ):
        """Deve executar o branch de progresso ao processar 500 unidades."""
        for numero in range(1, 502):
            Unidadeeducacional.objects.create(
                codigo_eol=str(100000 + numero),
                nome=f"EMEF ESCOLA TESTE {numero}",
                diretoria_regional=diretoria_regional_centro,
                tipo_escola=tipo_escola_emef,
                subprefeitura=subprefeitura_se,
            )

        registro_diretor = self.REGISTRO.copy()

        with (
            patch.object(
                Command,
                "_obter_dados_diretor",
                return_value=registro_diretor,
            ),
            patch.object(
                Command,
                "_montar_registro",
                side_effect=lambda **kwargs: {
                    "registro_funcional": "0000014",
                    "nome": "DIRETOR TESTE",
                    "email": "",
                    "telefone": "",
                    "esta_afastado": False,
                    "unidade_educacional": kwargs["unidade"],
                    "cargo_diretor": kwargs["cargo_diretor"],
                },
            ),
        ):
            resultado = Command()._coletar_registros(
                self.BASE_URL,
                headers=self.HEADERS,
                unidades=Unidadeeducacional.objects.all().order_by(
                    "codigo_eol"
                ),
            )

        assert len(resultado) == 501
