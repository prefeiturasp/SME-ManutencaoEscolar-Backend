"""Testes dos serializers de unidades educacionais."""

import pytest

from apps.escola.models.responsavel_unidade import (
    HistoricoResponsavel,
    ResponsavelUnidade,
)
from apps.escola.serializers.unidade_educacional_serializers import (
    UnidadeEducacionalListSerializer,
    UnidadeEducacionalSerializer,
)

pytestmark = pytest.mark.django_db


class TestUnidadeEducacionalSerializer:
    """Testa o serializer de unidades educacionais."""

    def test_deve_retornar_none_quando_dre_nao_possuir_vinculo_lote(
        self,
        unidade_educacional_emef,
    ):
        """Deve retornar None quando a DRE não possui lote associado."""
        serializer = UnidadeEducacionalSerializer(unidade_educacional_emef)

        assert serializer.data["lote"] is None

    def test_deve_retornar_lote_quando_dre_possuir_vinculo_lote(
        self,
        unidade_educacional_emef,
        lote_centro,
    ):
        """Deve retornar os dados do lote associado à DRE."""
        serializer = UnidadeEducacionalSerializer(unidade_educacional_emef)

        assert serializer.data["lote"] == {
            "uuid": str(lote_centro.uuid),
            "nome": lote_centro.nome,
        }

    def test_deve_retornar_dados_da_unidade_educacional(
        self,
        unidade_educacional_emef,
        lote_centro,
    ):
        """Deve serializar os dados e relacionamentos da unidade."""
        serializer = UnidadeEducacionalSerializer(
            unidade_educacional_emef,
        )

        resultado = serializer.data

        assert resultado["id"] == unidade_educacional_emef.id
        assert resultado["uuid"] == str(unidade_educacional_emef.uuid)
        assert resultado["codigo_eol"] == unidade_educacional_emef.codigo_eol
        assert resultado["nome"] == unidade_educacional_emef.nome
        assert resultado["status"] == unidade_educacional_emef.status

        assert resultado["tipo_escola"] == {
            "uuid": str(unidade_educacional_emef.tipo_escola.uuid),
            "sigla": unidade_educacional_emef.tipo_escola.sigla,
        }

        assert resultado["diretoria_regional"] == {
            "id": unidade_educacional_emef.diretoria_regional.id,
            "nome_curto": (
                unidade_educacional_emef.diretoria_regional.nome_curto
            ),
        }

        assert resultado["subprefeitura"] == {
            "uuid": str(unidade_educacional_emef.subprefeitura.uuid),
            "nome": unidade_educacional_emef.subprefeitura.nome,
        }

        assert resultado["lote"] == {
            "uuid": str(lote_centro.uuid),
            "nome": lote_centro.nome,
        }

    def test_deve_retornar_dados_complementares(
        self, unidade_educacional_emef, dados_unidade_emef
    ):
        """Deve serializar os dados complementares da unidade."""
        serializer = UnidadeEducacionalSerializer(
            unidade_educacional_emef,
        )

        resultado = serializer.data

        assert resultado["dados"] == {
            "email": unidade_educacional_emef.dados.email,
            "telefone": unidade_educacional_emef.dados.telefone,
            "logradouro": unidade_educacional_emef.dados.logradouro,
            "numero": unidade_educacional_emef.dados.numero,
            "bairro": unidade_educacional_emef.dados.bairro,
            "cep": unidade_educacional_emef.dados.cep,
            "municipio": unidade_educacional_emef.dados.municipio,
            "uf": unidade_educacional_emef.dados.uf,
        }

    def test_deve_retornar_lista_vazia_quando_unidade_nao_possuir_responsaveis(
        self,
        unidade_educacional_emef,
    ):
        """Deve retornar lista vazia quando não houver responsáveis atuais."""
        serializer = UnidadeEducacionalSerializer(
            unidade_educacional_emef,
        )

        assert serializer.data["responsaveis"] == []

    def test_deve_retornar_responsavel_atual_da_unidade(
        self,
        unidade_educacional_emef,
        responsavel_unidade,
        obter_cargo_diretor,
        historico_responsavel,
    ):
        """Deve serializar o responsável atualmente vinculado à unidade."""
        serializer = UnidadeEducacionalSerializer(
            unidade_educacional_emef,
        )
        responsavel = serializer.data["responsaveis"][0]

        assert responsavel["responsavel"]["registro_funcional"] == (
            responsavel_unidade.registro_funcional
        )
        assert responsavel["responsavel"]["nome"] == responsavel_unidade.nome
        assert responsavel["responsavel"]["email"] == responsavel_unidade.email
        assert (
            responsavel["responsavel"]["telefone"]
            == responsavel_unidade.telefone
        )
        assert (
            responsavel["responsavel"]["celular"]
            == responsavel_unidade.celular
        )

        assert responsavel["cargo"]["codigo"] == obter_cargo_diretor.codigo
        assert responsavel["cargo"]["nome"] == obter_cargo_diretor.nome

        assert responsavel["ativo"] is True

    def test_deve_retornar_apenas_responsaveis_atuais(
        self,
        unidade_educacional_emef,
        responsavel_unidade,
        obter_cargo_diretor,
        usuario_sincronizacao,
        historico_responsavel,
    ):
        """Deve ignorar históricos de responsáveis inativos."""
        responsavel_inativo = ResponsavelUnidade.objects.create(
            registro_funcional="000000012",
            nome="RESPONSAVEL INATIVO",
            email="inativo@email.com",
            telefone="11988888888",
            esta_afastado=False,
        )

        HistoricoResponsavel.objects.create(
            responsavel=responsavel_inativo,
            unidade_educacional=unidade_educacional_emef,
            cargo=obter_cargo_diretor,
            ativo=False,
        )

        serializer = UnidadeEducacionalSerializer(
            unidade_educacional_emef,
        )

        responsaveis = serializer.data["responsaveis"]

        assert len(responsaveis) == 1
        assert (
            responsaveis[0]["responsavel"]["registro_funcional"]
            == responsavel_unidade.registro_funcional
        )

    def test_deve_retornar_multiplos_responsaveis_atuais(
        self,
        unidade_educacional_emef,
        responsavel_unidade,
        obter_cargo_diretor,
        historico_responsavel,
    ):
        """Deve serializar todos os responsáveis atuais da unidade."""
        segundo_responsavel = ResponsavelUnidade.objects.create(
            registro_funcional="000000012",
            nome="SEGUNDO RESPONSAVEL",
            email="segundo@email.com",
            telefone="11988888888",
            esta_afastado=False,
        )

        HistoricoResponsavel.objects.create(
            responsavel=segundo_responsavel,
            unidade_educacional=unidade_educacional_emef,
            cargo=obter_cargo_diretor,
            ativo=True,
        )

        serializer = UnidadeEducacionalSerializer(
            unidade_educacional_emef,
        )

        responsaveis = serializer.data["responsaveis"]

        assert len(responsaveis) == 2

        registros_funcionais = {
            item["responsavel"]["registro_funcional"] for item in responsaveis
        }

        assert registros_funcionais == {
            responsavel_unidade.registro_funcional,
            segundo_responsavel.registro_funcional,
        }


class TestUnidadeEducacionalListSerializer:
    """Testa o serializer de listagem de unidades educacionais."""

    def test_deve_retornar_campos_da_listagem(
        self,
        unidade_educacional_emef,
        lote_centro,
    ):
        """Deve retornar apenas os campos previstos para a listagem."""
        serializer = UnidadeEducacionalListSerializer(
            unidade_educacional_emef,
        )

        resultado = serializer.data

        assert set(resultado.keys()) == {
            "uuid",
            "codigo_eol",
            "nome",
            "tipo_escola",
            "diretoria_regional",
            "subprefeitura",
            "lote",
            "status",
        }

        assert resultado["uuid"] == str(unidade_educacional_emef.uuid)
        assert resultado["status"] == unidade_educacional_emef.status
        assert resultado["nome"] == unidade_educacional_emef.nome
        assert resultado["codigo_eol"] == unidade_educacional_emef.codigo_eol

        assert resultado["lote"] == {
            "uuid": str(lote_centro.uuid),
            "nome": lote_centro.nome,
        }

        assert resultado["subprefeitura"] == {
            "uuid": str(unidade_educacional_emef.subprefeitura.uuid),
            "nome": unidade_educacional_emef.subprefeitura.nome,
        }

        assert resultado["diretoria_regional"] == {
            "id": unidade_educacional_emef.diretoria_regional.id,
            "nome_curto": (
                unidade_educacional_emef.diretoria_regional.nome_curto
            ),
        }

        assert resultado["tipo_escola"] == {
            "uuid": str(unidade_educacional_emef.tipo_escola.uuid),
            "sigla": unidade_educacional_emef.tipo_escola.sigla,
        }

    def test_nao_deve_retornar_dados_complementares(
        self,
        unidade_educacional_emef,
    ):
        """Não deve retornar dados complementares na listagem."""
        serializer = UnidadeEducacionalListSerializer(
            unidade_educacional_emef,
        )

        assert "dados" not in serializer.data
