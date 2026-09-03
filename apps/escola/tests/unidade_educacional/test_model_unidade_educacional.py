"""Testes do model Unidadeeducacional."""

import uuid

import pytest
from django.db import IntegrityError

from apps.escola.models import (
    Unidadeeducacional,
)

pytestmark = pytest.mark.django_db


class TestUnidadeeducacional:
    """Testes do model Unidadeeducacional."""

    def test_deve_criar_unidade_educacional_com_dados_validos(
        self,
        diretoria_regional_centro,
        tipo_escola_emef,
        subprefeitura_se,
    ):
        """Deve criar uma unidade educacional com os dados informados."""
        escola = Unidadeeducacional.objects.create(
            codigo_eol="100001",
            nome="EMEF Escola Teste",
            diretoria_regional=diretoria_regional_centro,
            tipo_escola=tipo_escola_emef,
            subprefeitura=subprefeitura_se,
        )

        assert escola.codigo_eol == "100001"
        assert escola.nome == "EMEF Escola Teste"
        assert escola.diretoria_regional == diretoria_regional_centro
        assert escola.tipo_escola == tipo_escola_emef
        assert escola.subprefeitura == subprefeitura_se
        assert escola.status is True

    def test_deve_gerar_uuid_automaticamente(
        self,
        diretoria_regional_centro,
        tipo_escola_emef,
        subprefeitura_se,
    ):
        """Deve gerar um UUID automaticamente para o registro."""
        escola = Unidadeeducacional.objects.create(
            codigo_eol="100001",
            nome="EMEF Escola Teste",
            diretoria_regional=diretoria_regional_centro,
            tipo_escola=tipo_escola_emef,
            subprefeitura=subprefeitura_se,
        )

        assert escola.uuid is not None
        assert isinstance(escola.uuid, uuid.UUID)

    def test_deve_representar_unidade_educacional_com_str(
        self,
        diretoria_regional_centro,
        tipo_escola_emef,
        subprefeitura_se,
    ):
        """Deve retornar código e nome na representação textual."""
        escola = Unidadeeducacional(
            codigo_eol="100001",
            nome="EMEF Escola Teste",
            diretoria_regional=diretoria_regional_centro,
            tipo_escola=tipo_escola_emef,
            subprefeitura=subprefeitura_se,
        )

        assert str(escola) == "100001 - EMEF Escola Teste"

    def test_nao_deve_permitir_codigo_eol_duplicado(
        self,
        diretoria_regional_centro,
        tipo_escola_emef,
        subprefeitura_se,
    ):
        """Não deve permitir duas escolas com o mesmo código EOL."""
        Unidadeeducacional.objects.create(
            codigo_eol="100001",
            nome="EMEF Escola Teste",
            diretoria_regional=diretoria_regional_centro,
            tipo_escola=tipo_escola_emef,
            subprefeitura=subprefeitura_se,
        )

        with pytest.raises(IntegrityError):
            Unidadeeducacional.objects.create(
                codigo_eol="100001",
                nome="EMEF Outra Escola",
                diretoria_regional=diretoria_regional_centro,
                tipo_escola=tipo_escola_emef,
                subprefeitura=subprefeitura_se,
            )

    def test_deve_ordenar_por_nome(
        self,
        diretoria_regional_centro,
        tipo_escola_emef,
        subprefeitura_se,
    ):
        """Deve retornar as escolas ordenadas pelo nome."""
        escola_ze = Unidadeeducacional.objects.create(
            codigo_eol="100001",
            nome="EMEF Zeta",
            diretoria_regional=diretoria_regional_centro,
            tipo_escola=tipo_escola_emef,
            subprefeitura=subprefeitura_se,
        )
        escola_alpha = Unidadeeducacional.objects.create(
            codigo_eol="100002",
            nome="EMEF Alpha",
            diretoria_regional=diretoria_regional_centro,
            tipo_escola=tipo_escola_emef,
            subprefeitura=subprefeitura_se,
        )
        escola_beta = Unidadeeducacional.objects.create(
            codigo_eol="100003",
            nome="EMEF Beta",
            diretoria_regional=diretoria_regional_centro,
            tipo_escola=tipo_escola_emef,
            subprefeitura=subprefeitura_se,
        )

        escolas = list(Unidadeeducacional.objects.all())

        assert escolas == [
            escola_alpha,
            escola_beta,
            escola_ze,
        ]

    def test_deve_permitir_alterar_status(
        self,
        diretoria_regional_centro,
        tipo_escola_emef,
        subprefeitura_se,
    ):
        """Deve permitir desativar uma unidade educacional."""
        escola = Unidadeeducacional.objects.create(
            codigo_eol="100001",
            nome="EMEF Escola Teste",
            diretoria_regional=diretoria_regional_centro,
            tipo_escola=tipo_escola_emef,
            subprefeitura=subprefeitura_se,
            status=False,
        )

        assert escola.status is False
