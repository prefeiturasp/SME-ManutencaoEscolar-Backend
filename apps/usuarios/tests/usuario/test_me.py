"""Testes dos dados de unidade e DRE no endpoint /usuarios/me."""

import pytest
from rest_framework import status
from rest_framework.test import force_authenticate

from apps.usuarios.api.views.usuario_views import UsuarioViewSet
from apps.usuarios.constants import PerfilAcesso
from apps.usuarios.models.cargo_eol import CargoEOL
from apps.usuarios.models.usuario import Usuario
from apps.usuarios.services.usuario_service import UsuarioService

pytestmark = pytest.mark.django_db

SEM_VINCULO = {"unidade_educacional": None, "diretoria_regional": None}


def _criar_usuario(username: str, perfil: str | None) -> Usuario:
    cargo = None
    if perfil is not None:
        cargo = CargoEOL.objects.create(
            codigo=f"cargo-{username}", nome=f"Cargo {perfil}", perfil=perfil
        )
    return Usuario.objects.create(
        username=username,
        nome=f"Usuário {perfil}",
        email=f"{username}@teste.com",
        cargo=cargo,
    )


class TestObterUsuarioAutenticado:
    def test_ue_retorna_unidade_e_dre(
        self, historico_responsavel, unidade_educacional_emef
    ):
        rf = historico_responsavel.responsavel.registro_funcional
        _criar_usuario(rf, PerfilAcesso.UE)

        resultado = UsuarioService.obter_usuario_autenticado(rf)

        assert (
            resultado["unidade_educacional"] == unidade_educacional_emef.nome
        )
        assert (
            resultado["diretoria_regional"]
            == unidade_educacional_emef.diretoria_regional.nome
        )
        assert resultado["username"] == rf

    def test_ue_sem_vinculo_ativo_retorna_nulos(self):
        _criar_usuario("0000099", PerfilAcesso.UE)

        resultado = UsuarioService.obter_usuario_autenticado("0000099")

        assert {
            chave: resultado[chave] for chave in SEM_VINCULO
        } == SEM_VINCULO

    def test_dre_nao_retorna_unidade_educacional(self):
        _criar_usuario("0000098", PerfilAcesso.DRE)

        resultado = UsuarioService.obter_usuario_autenticado("0000098")

        assert resultado["unidade_educacional"] is None
        assert resultado["diretoria_regional"] is None

    def test_dre_usa_a_dre_do_usuario(self, monkeypatch):
        _criar_usuario("0000097", PerfilAcesso.DRE)
        monkeypatch.setattr(
            UsuarioService,
            "_obter_dre_do_usuario",
            staticmethod(lambda username: "DRE CENTRO"),
        )

        resultado = UsuarioService.obter_usuario_autenticado("0000097")

        assert resultado["diretoria_regional"] == "DRE CENTRO"
        assert resultado["unidade_educacional"] is None

    @pytest.mark.parametrize(
        "perfil", [PerfilAcesso.SME, PerfilAcesso.EMPRESA, None]
    )
    def test_sme_empresa_e_sem_cargo_nao_retornam_vinculo(
        self, perfil, historico_responsavel
    ):
        # mesmo com RF vinculado a uma unidade, só o perfil UE recebe dados
        rf = historico_responsavel.responsavel.registro_funcional
        _criar_usuario(rf, perfil)

        resultado = UsuarioService.obter_usuario_autenticado(rf)

        assert {
            chave: resultado[chave] for chave in SEM_VINCULO
        } == SEM_VINCULO


class TestMeView:
    def test_me_ue_retorna_nomes(
        self, api_factory, historico_responsavel, unidade_educacional_emef
    ):
        rf = historico_responsavel.responsavel.registro_funcional
        usuario = _criar_usuario(rf, PerfilAcesso.UE)
        request = api_factory.get("/usuarios/me/")
        force_authenticate(request, user=usuario)

        response = UsuarioViewSet.as_view({"get": "me"})(request)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["unidade_educacional"] == (
            unidade_educacional_emef.nome
        )
        assert response.data["diretoria_regional"] == (
            unidade_educacional_emef.diretoria_regional.nome
        )

    @pytest.mark.parametrize(
        "perfil", [PerfilAcesso.SME, PerfilAcesso.EMPRESA]
    )
    def test_me_sme_e_empresa_retornam_nulos(self, api_factory, perfil):
        usuario = _criar_usuario("0000096", perfil)
        request = api_factory.get("/usuarios/me/")
        force_authenticate(request, user=usuario)

        response = UsuarioViewSet.as_view({"get": "me"})(request)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["unidade_educacional"] is None
        assert response.data["diretoria_regional"] is None
