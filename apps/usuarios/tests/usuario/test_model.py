import pytest

from apps.usuarios.constants import PerfilAcesso
from apps.usuarios.models import CargoEOL, Usuario


@pytest.mark.django_db
class TestUsuarioModel:
    def test_str_retorna_nome_usuario(self):
        cargo = CargoEOL.objects.create(
            codigo="9999",
            nome="Diretor",
            perfil=PerfilAcesso.UE,
        )

        usuario = Usuario.objects.create(
            username="1234567",
            nome="João da Silva",
            registro_funcional="1234567",
            cpf="12345678901",
            cargo=cargo,
        )

        assert str(usuario) == "João da Silva"
