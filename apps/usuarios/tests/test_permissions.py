"""Testes do controle de acesso por perfil."""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.usuarios.constants import (
    FUNCIONALIDADES_POR_PERFIL,
    Funcionalidade,
    PerfilAcesso,
)
from apps.usuarios.models.cargo_eol import CargoEOL
from apps.usuarios.models.usuario import Usuario
from apps.usuarios.permissions import PermissaoCadastros

pytestmark = pytest.mark.django_db

URLS_CADASTROS = [
    "/api/v1/cargos/",
    "/api/v1/empresas/",
    "/api/v1/equipes/",
    "/api/v1/lotes/",
    "/api/v1/profissionais/",
    "/api/v1/servicos/",
    "/api/v1/unidades-educacionais/",
]

URLS_DE_APOIO = [
    "/api/v1/tipos-escola/",
    "/api/v1/diretorias-regionais/",
    "/api/v1/subprefeituras/",
    "/api/v1/cargos-eol/",
]

PERFIS_SEM_CADASTROS = [
    PerfilAcesso.DRE,
    PerfilAcesso.UE,
    PerfilAcesso.EMPRESA,
    None,
]


class TestFuncionalidadesPorPerfil:
    """Testa a matriz de funcionalidades de cada perfil (CA01 a CA04)."""

    def test_sme_acessa_cadastros_solicitacao_e_relatorios(self):
        assert FUNCIONALIDADES_POR_PERFIL[PerfilAcesso.SME] == {
            Funcionalidade.CADASTROS,
            Funcionalidade.SOLICITACAO_MANUTENCAO,
            Funcionalidade.RELATORIOS,
        }

    @pytest.mark.parametrize(
        "perfil", [PerfilAcesso.DRE, PerfilAcesso.UE, PerfilAcesso.EMPRESA]
    )
    def test_demais_perfis_acessam_solicitacao_e_relatorios(self, perfil):
        assert FUNCIONALIDADES_POR_PERFIL[perfil] == {
            Funcionalidade.SOLICITACAO_MANUTENCAO,
            Funcionalidade.RELATORIOS,
        }

    def test_todos_os_perfis_possuem_regra_definida(self):
        assert set(FUNCIONALIDADES_POR_PERFIL) == set(PerfilAcesso.values)


class TestUsuarioFuncionalidades:
    """Testa as funcionalidades expostas pelo modelo de usuário."""

    def test_usuario_sme_tem_acesso_a_cadastros(self, usuario_ativo):
        assert usuario_ativo.tem_acesso(Funcionalidade.CADASTROS)
        assert usuario_ativo.funcionalidades == [
            "CADASTROS",
            "RELATORIOS",
            "SOLICITACAO_MANUTENCAO",
        ]

    def test_usuario_ue_nao_tem_acesso_a_cadastros(self, cargo_perfil_diretor):
        usuario = Usuario.objects.create(
            username="ue", nome="UE", cargo=cargo_perfil_diretor
        )
        assert not usuario.tem_acesso(Funcionalidade.CADASTROS)
        assert usuario.tem_acesso(Funcionalidade.RELATORIOS)

    def test_usuario_sem_cargo_nao_tem_funcionalidades(self):
        usuario = Usuario.objects.create(username="sem-cargo", nome="Sem")
        assert usuario.perfil is None
        assert usuario.funcionalidades == []

    def test_cargo_sem_perfil_nao_tem_funcionalidades(self):
        cargo = CargoEOL.objects.create(codigo="0001", nome="Sem perfil")
        usuario = Usuario.objects.create(
            username="cargo-sem-perfil", nome="Sem", cargo=cargo
        )
        assert usuario.perfil is None
        assert usuario.funcionalidades == []


class TestPermissaoCadastrosNasViews:
    """Testa o bloqueio dos cadastros por perfil."""

    @pytest.mark.parametrize("url", URLS_CADASTROS)
    def test_sme_acessa_cadastros(self, api_cliente_perfil, url):
        resposta = api_cliente_perfil(PerfilAcesso.SME).get(url)
        assert resposta.status_code == status.HTTP_200_OK

    @pytest.mark.parametrize("perfil", PERFIS_SEM_CADASTROS)
    @pytest.mark.parametrize("url", URLS_CADASTROS)
    def test_demais_perfis_nao_acessam_cadastros(
        self, api_cliente_perfil, url, perfil
    ):
        resposta = api_cliente_perfil(perfil).get(url)
        assert resposta.status_code == status.HTTP_403_FORBIDDEN
        assert resposta.data["detail"] == PermissaoCadastros.message

    @pytest.mark.parametrize("url", URLS_CADASTROS)
    def test_usuario_nao_autenticado_recebe_401(self, url):
        resposta = APIClient().get(url)
        assert resposta.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.parametrize("url", URLS_CADASTROS)
    def test_escrita_tambem_e_bloqueada(self, api_cliente_perfil, url):
        cliente = api_cliente_perfil(PerfilAcesso.DRE)
        resposta = cliente.post(url, data={}, format="json")
        # 403 para recursos que aceitam POST, 405 quando não aceitam (GET/PUT)
        assert resposta.status_code in (
            status.HTTP_403_FORBIDDEN,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    @pytest.mark.parametrize("perfil", PERFIS_SEM_CADASTROS)
    @pytest.mark.parametrize("url", URLS_DE_APOIO)
    def test_consultas_de_apoio_continuam_liberadas(
        self, api_cliente_perfil, url, perfil
    ):
        resposta = api_cliente_perfil(perfil).get(url)
        assert resposta.status_code == status.HTTP_200_OK


class TestPermissaoFuncionalidade:
    """Testa a permissão isoladamente."""

    def test_nega_usuario_anonimo(self, api_factory):
        request = api_factory.get("/")
        request.user = type("Anonimo", (), {"is_authenticated": False})()
        assert not PermissaoCadastros().has_permission(request, None)

    def test_nega_quando_nao_ha_usuario(self, api_factory):
        request = api_factory.get("/")
        request.user = None
        assert not PermissaoCadastros().has_permission(request, None)
