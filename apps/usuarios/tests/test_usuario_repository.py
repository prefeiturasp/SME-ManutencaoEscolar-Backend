import pytest

from apps.usuarios.models.cargo_eol import CargoEOL
from apps.usuarios.models.usuario import Usuario
from apps.usuarios.repository.usuario_repository import UsuarioRepository


class TestUsuarioRepository:
    @pytest.mark.django_db
    def test_atualizar_ou_criar_novo_usuario_rf(
        self,
    ):
        resultado = UsuarioRepository.atualizar_ou_criar(
            dados_usuario={
                "nome": "João",
                "email": "joao@email.com",
                "codigo_rf": "1234567",
                "cpf": "12345678901",
            },
            codigo_cargo="3360",
        )

        assert resultado["id"] == 1
        usuario = Usuario.objects.get(registro_funcional="1234567")
        assert usuario.nome == "João"
        assert usuario.email == "joao@email.com"

        cargo = CargoEOL.objects.get(codigo="3360")
        assert usuario.cargo == cargo

    @pytest.mark.django_db
    def test_atualizar_ou_criar_utiliza_cpf_quando_rf_invalido(self):
        cargo = CargoEOL.objects.get(codigo="3360")

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
        assert usuario.cargo == cargo

    @pytest.mark.django_db
    def test_atualizar_ou_criar_atualiza_usuario_existente(self):
        cargo = CargoEOL.objects.get(codigo="3360")

        usuario = Usuario.objects.create(
            registro_funcional="1234567",
            username="1234567",
            nome="Nome Antigo",
            email="antigo@email.com",
            cargo=cargo,
        )

        resultado = UsuarioRepository.atualizar_ou_criar(
            dados_usuario={
                "nome": "Nome Novo",
                "email": "novo@email.com",
                "codigo_rf": "1234567",
                "cpf": "12345678901",
            },
            codigo_cargo="3360",
        )

        usuario.refresh_from_db()

        assert resultado["id"] == usuario.id
        assert usuario.nome == "Nome Novo"
        assert usuario.email == "novo@email.com"

    @pytest.mark.django_db
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
