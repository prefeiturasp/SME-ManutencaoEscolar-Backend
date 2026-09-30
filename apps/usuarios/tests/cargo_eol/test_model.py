import pytest

from apps.usuarios.constants import PerfilAcesso
from apps.usuarios.models import CargoEOL


@pytest.mark.django_db
class TestCargoEOLModel:
    def test_str(self):
        cargo = CargoEOL.objects.create(
            codigo="9999",
            nome="Diretor",
            perfil=PerfilAcesso.UE,
        )

        assert str(cargo) == "9999 - Diretor"

    def test_desativar_cargo(self):
        cargo = CargoEOL.objects.create(
            codigo="9999",
            nome="Diretor",
            perfil=PerfilAcesso.UE,
            ativo=True,
        )

        cargo.desativar_cargo()

        cargo.refresh_from_db()

        assert cargo.ativo is False

    def test_ativar_cargo(self):
        cargo = CargoEOL.objects.create(
            codigo="9999",
            nome="Diretor",
            perfil=PerfilAcesso.UE,
            ativo=False,
        )

        cargo.ativar_cargo()

        cargo.refresh_from_db()

        assert cargo.ativo is True

    @pytest.mark.parametrize(
        "perfil,atributo",
        [
            (PerfilAcesso.UE, "eh_perfil_ue"),
            (PerfilAcesso.DRE, "eh_perfil_dre"),
            (PerfilAcesso.SME, "eh_perfil_sme"),
            (PerfilAcesso.EMPRESA, "eh_perfil_empresa"),
        ],
    )
    def test_propriedades_de_perfil(self, perfil, atributo):
        cargo = CargoEOL.objects.create(
            codigo=str(perfil),
            nome="Cargo",
            perfil=perfil,
        )

        assert getattr(cargo, atributo) is True
