"""Testes do model ResponsavelUnidade."""

import uuid

import pytest
from django.db import IntegrityError

from apps.escola.models import (
    HistoricoResponsavel,
    ResponsavelUnidade,
)

pytestmark = pytest.mark.django_db


class TestResponsavelUnidade:
    """Testes do model ResponsavelUnidade."""

    def test_deve_criar_responsavel_com_dados_validos(self):
        """Deve criar um responsável com os dados informados."""
        responsavel = ResponsavelUnidade.objects.create(
            registro_funcional="0000011",
            nome="Diretor Um",
            email="diretor.um@email.com",
            telefone="1122223333",
            celular="11999999999",
            esta_afastado=False,
        )

        assert responsavel.registro_funcional == "0000011"
        assert responsavel.nome == "Diretor Um"
        assert responsavel.email == "diretor.um@email.com"
        assert responsavel.telefone == "1122223333"
        assert responsavel.celular == "11999999999"
        assert responsavel.esta_afastado is False

    def test_deve_gerar_uuid_automaticamente(self):
        """Deve gerar um UUID automaticamente."""
        responsavel = ResponsavelUnidade.objects.create(
            registro_funcional="0000011",
            nome="Diretor Um",
        )

        assert responsavel.uuid is not None
        assert isinstance(responsavel.uuid, uuid.UUID)

    def test_deve_representar_responsavel_com_str(self):
        """Deve retornar registro funcional e nome na representação textual."""
        responsavel = ResponsavelUnidade(
            registro_funcional="0000011",
            nome="Diretor Um",
        )

        assert str(responsavel) == "0000011 - Diretor Um"

    def test_deve_permitir_email_vazio(self):
        """Deve permitir e-mail vazio."""
        responsavel = ResponsavelUnidade.objects.create(
            registro_funcional="0000011",
            nome="Diretor Um",
            email="",
        )

        assert responsavel.email == ""

    def test_deve_permitir_telefone_vazio(self):
        """Deve permitir telefone vazio."""
        responsavel = ResponsavelUnidade.objects.create(
            registro_funcional="0000011",
            nome="Diretor Um",
            telefone="",
        )

        assert responsavel.telefone == ""

    def test_nao_deve_permitir_registro_funcional_duplicado(self):
        """Não deve permitir responsáveis com o mesmo registro funcional."""
        ResponsavelUnidade.objects.create(
            registro_funcional="0000011",
            nome="Diretor Um",
        )

        with pytest.raises(IntegrityError):
            ResponsavelUnidade.objects.create(
                registro_funcional="0000011",
                nome="OUTRO SERVIDOR",
            )

    def test_deve_ordenar_por_nome(self):
        """Deve retornar os responsáveis ordenados pelo nome."""
        responsavel_um = ResponsavelUnidade.objects.create(
            registro_funcional="0000011",
            nome="Diretor Um",
        )
        responsavel_dois = ResponsavelUnidade.objects.create(
            registro_funcional="0000012",
            nome="Diretor Dois",
        )
        responsavel_tres = ResponsavelUnidade.objects.create(
            registro_funcional="0000013",
            nome="Diretor Três",
        )

        responsaveis = list(ResponsavelUnidade.objects.all())

        assert responsaveis == [
            responsavel_dois,
            responsavel_tres,
            responsavel_um,
        ]

    def test_deve_retornar_escolas_atuais(
        self,
        unidade_educacional_emef,
        unidade_educacional_cemei,
        cargo_perfil_diretor,
    ):
        """Deve retornar somente os vínculos ativos."""
        responsavel = ResponsavelUnidade.objects.create(
            registro_funcional="0000011",
            nome="Diretor Um",
        )

        HistoricoResponsavel.objects.create(
            responsavel=responsavel,
            unidade_educacional=unidade_educacional_emef,
            cargo=cargo_perfil_diretor,
            ativo=True,
        )

        HistoricoResponsavel.objects.create(
            responsavel=responsavel,
            unidade_educacional=unidade_educacional_cemei,
            cargo=cargo_perfil_diretor,
            ativo=False,
        )

        escolas = list(responsavel.escolas_atuais)

        assert escolas == [
            responsavel.historicos_unidade.get(
                unidade_educacional=unidade_educacional_emef,
            ),
        ]
