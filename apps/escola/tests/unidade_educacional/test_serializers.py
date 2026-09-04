"""Testes dos serializers de unidades educacionais."""

import pytest

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

    def test_nao_deve_retornar_dados_complementares(
        self,
        unidade_educacional_emef,
    ):
        """Não deve retornar dados complementares na listagem."""
        serializer = UnidadeEducacionalListSerializer(
            unidade_educacional_emef,
        )

        assert "dados" not in serializer.data
