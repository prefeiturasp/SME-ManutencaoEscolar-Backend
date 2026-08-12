from unittest.mock import patch

import pytest
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.db.models import ObjectDoesNotExist

from apps.usuarios.exceptions import UsuarioNaoEncontradoError
from apps.usuarios.models.cargo_eol import CargoEOL
from apps.usuarios.models.usuario import Usuario
from apps.usuarios.repository.usuario_repository import UsuarioRepository

pytestmark = pytest.mark.django_db


class TestUsuarioRepository:
    def test_atualizar_ou_criar_novo_usuario_rf(self):
        resultado = UsuarioRepository.atualizar_ou_criar(
            dados_usuario={
                "nome": "João",
                "email": "joao@email.com",
                "codigo_rf": "1234567",
                "cpf": None,
            },
            codigo_cargo="3360",
        )

        usuario = Usuario.objects.get(registro_funcional="1234567")
        cargo = CargoEOL.objects.get(codigo="3360")

        assert resultado["id"] == usuario.id
        assert usuario.nome == "João"
        assert usuario.email == "joao@email.com"
        assert usuario.cargo == cargo

    def test_atualizar_ou_criar_utiliza_cpf_quando_rf_invalido(self):
        resultado = UsuarioRepository.atualizar_ou_criar(
            dados_usuario={
                "nome": "João",
                "email": "joao@email.com",
                "codigo_rf": None,
                "cpf": "12345678901",
            },
            codigo_cargo="3360",
        )

        usuario = Usuario.objects.get(cpf="12345678901")

        assert resultado["id"] == usuario.id
        assert usuario.cargo.codigo == "3360"

    def test_atualizar_ou_criar_atualiza_usuario_existente(
        self,
        usuario_ativo,
    ):
        usuario_ativo.registro_funcional = "1234567"
        usuario_ativo.username = "1234567"
        usuario_ativo.email = "antigo@email.com"
        usuario_ativo.nome = "Nome Antigo"
        usuario_ativo.save()

        resultado = UsuarioRepository.atualizar_ou_criar(
            dados_usuario={
                "nome": "Nome Novo",
                "email": "novo@email.com",
                "codigo_rf": usuario_ativo.registro_funcional,
                "cpf": None,
            },
            codigo_cargo=usuario_ativo.cargo.codigo,
        )

        usuario_ativo.refresh_from_db()

        assert resultado["id"] == usuario_ativo.id
        assert usuario_ativo.nome == "Nome Novo"
        assert usuario_ativo.email == "novo@email.com"

    def test_atualizar_ou_criar_sem_rf_e_sem_cpf(self):
        with pytest.raises(
            ValueError,
            match="É necessário fornecer registro_funcional ou cpf",
        ):
            UsuarioRepository.atualizar_ou_criar(
                dados_usuario={
                    "nome": "João",
                    "email": "joao@email.com",
                    "codigo_rf": None,
                    "cpf": None,
                },
                codigo_cargo="1",
            )

    def test_usuario_existe_por_id_retorna_true_para_usuario_ativo(
        self,
        usuario_ativo,
    ):
        assert UsuarioRepository.usuario_existe_por_id(usuario_ativo.id)

    def test_usuario_existe_por_id_retorna_false_para_usuario_inativo(
        self,
        usuario_inativo,
    ):
        assert not UsuarioRepository.usuario_existe_por_id(usuario_inativo.id)

    def test_usuario_existe_por_id_retorna_false_para_id_inexistente(self):
        assert not UsuarioRepository.usuario_existe_por_id(99999)

    def test_retorna_username_usuario(
        self,
        usuario_ativo,
    ):
        resultado = UsuarioRepository.retorna_username_usuario(
            usuario_ativo.id
        )

        assert resultado == {
            "username": usuario_ativo.username,
        }

    def test_retorna_username_usuario_lanca_excecao_quando_usuario_nao_existe(
        self,
    ):
        with pytest.raises(UsuarioNaoEncontradoError) as exc:
            UsuarioRepository.retorna_username_usuario(99999)

        assert exc.value.title == "Usuário não encontrado."
        assert (
            exc.value.detail
            == "Não foi encontrado um usuário ativo com o identificador "
            "informado."
        )

    def test_retorna_username_usuario_lanca_excecao_quando_usuario_inativo(
        self,
        usuario_inativo,
    ):
        with pytest.raises(UsuarioNaoEncontradoError):
            UsuarioRepository.retorna_username_usuario(usuario_inativo.id)

    def test_deve_retornar_usuario(
        self,
        usuario_ativo,
    ):
        resultado = UsuarioRepository._consulta_por_username(
            usuario_ativo.username
        )

        assert resultado == usuario_ativo

    def test_deve_lancar_exception_quando_usuario_nao_existir(self):
        with pytest.raises(ObjectDoesNotExist):
            UsuarioRepository._consulta_por_username("usuario-inexistente")

    def test_deve_retornar_dicionario(self, usuario_ativo, usuario_ativo_dict):
        resultado = UsuarioRepository._retorna_usuario_em_dicionario(
            usuario_ativo
        )

        assert resultado == usuario_ativo_dict

    @patch.object(
        UsuarioRepository,
        "_retorna_usuario_em_dicionario",
    )
    @patch.object(
        UsuarioRepository,
        "_consulta_por_username",
    )
    def test_deve_retornar_usuario_em_dicionario(
        self, consulta_mock, retorna_mock, usuario_ativo, usuario_ativo_dict
    ):
        consulta_mock.return_value = usuario_ativo
        retorna_mock.return_value = usuario_ativo_dict

        resultado = UsuarioRepository.busca_usuario_por_username(
            usuario_ativo.username
        )

        assert resultado == usuario_ativo_dict

        consulta_mock.assert_called_once_with(usuario_ativo.username)
        retorna_mock.assert_called_once_with(usuario_ativo)

    @patch.object(
        UsuarioRepository,
        "_consulta_por_username",
    )
    def test_deve_lancar_exception(
        self,
        consulta_mock,
    ):
        consulta_mock.side_effect = ObjectDoesNotExist

        with pytest.raises(ObjectDoesNotExist):
            UsuarioRepository.busca_usuario_por_username("123")

    def test_atualizar_senha_usuario_invalida_token(self, usuario_ativo):
        """Deve invalidar o token após alterar a senha."""
        token_generator = PasswordResetTokenGenerator()

        token = token_generator.make_token(usuario_ativo)
        assert token_generator.check_token(usuario_ativo, token)

        UsuarioRepository.atualizar_senha_usuario(
            usuario_ativo.username,
            "nova-senha-123",
        )

        usuario_ativo.refresh_from_db()

        assert not token_generator.check_token(usuario_ativo, token)
