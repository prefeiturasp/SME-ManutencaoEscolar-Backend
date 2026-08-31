"""Teste da view de Unidade Educacional."""

import uuid

import pytest
from rest_framework import status

from apps.escola.models import (
    Unidadeeducacional,
)

pytestmark = pytest.mark.django_db


class TestUnidadeEducacionalViewSet:
    """Testes do ViewSet de unidades educacionais."""

    url = "/api/v1/unidades-educacionais/"

    def test_deve_listar_unidades_educacionais(
        self,
        cliente_api,
        unidade_educacional_emef,
        unidade_educacional_inativa_emef,
        unidade_educacional_cemei,
    ):
        """Deve retornar as unidades educacionais cadastradas."""
        resposta = cliente_api.get(self.url)

        assert resposta.status_code == status.HTTP_200_OK

        resultados = resposta.data["results"]

        assert len(resultados) == 3
        assert {resultado["codigo_eol"] for resultado in resultados} == {
            unidade_educacional_emef.codigo_eol,
            unidade_educacional_inativa_emef.codigo_eol,
            unidade_educacional_cemei.codigo_eol,
        }

    def test_deve_buscar_unidade_educacional_por_uuid(
        self,
        cliente_api,
        unidade_educacional_emef,
    ):
        """Deve retornar uma unidade educacional pelo UUID."""
        resposta = cliente_api.get(
            f"{self.url}{unidade_educacional_emef.uuid}/",
        )

        assert resposta.status_code == status.HTTP_200_OK

        resultado = resposta.data

        assert resultado["id"] == unidade_educacional_emef.id
        assert resultado["uuid"] == str(
            unidade_educacional_emef.uuid,
        )
        assert resultado["codigo_eol"] == (unidade_educacional_emef.codigo_eol)
        assert resultado["nome"] == unidade_educacional_emef.nome
        assert resultado["status"] == unidade_educacional_emef.status

    def test_deve_filtrar_por_codigo_eol(
        self,
        cliente_api,
        unidade_educacional_emef,
    ):
        """Deve filtrar unidades pelo código EOL."""
        resposta = cliente_api.get(
            self.url,
            {"codigo_eol": unidade_educacional_emef.codigo_eol},
        )

        assert resposta.status_code == status.HTTP_200_OK

        resultados = resposta.data["results"]

        assert len(resultados) == 1
        assert resultados[0]["uuid"] == str(
            unidade_educacional_emef.uuid,
        )

    def test_deve_filtrar_por_status_ativo(
        self,
        cliente_api,
        unidade_educacional_emef,
        unidade_educacional_inativa_emef,
        unidade_educacional_cemei,
    ):
        """Deve retornar somente unidades ativas."""
        resposta = cliente_api.get(
            self.url,
            {"status": "true"},
        )

        assert resposta.status_code == status.HTTP_200_OK

        resultados = resposta.data["results"]

        assert len(resultados) == 2
        assert {resultado["uuid"] for resultado in resultados} == {
            str(unidade_educacional_emef.uuid),
            str(unidade_educacional_cemei.uuid),
        }

    def test_deve_filtrar_por_status_inativo(
        self,
        cliente_api,
        unidade_educacional_inativa_emef,
        unidade_educacional_emef,
        unidade_educacional_cemei,
    ):
        """Deve retornar somente unidades inativas."""
        resposta = cliente_api.get(
            self.url,
            {"status": "false"},
        )

        assert resposta.status_code == status.HTTP_200_OK

        resultados = resposta.data["results"]

        assert len(resultados) == 1
        assert resultados[0]["uuid"] == str(
            unidade_educacional_inativa_emef.uuid,
        )
        assert resultados[0]["status"] is False

    def test_deve_filtrar_por_tipo_escola(
        self,
        cliente_api,
        unidade_educacional_emef,
        unidade_educacional_inativa_emef,
        tipo_escola_emef,
    ):
        """Deve filtrar unidades pelo tipo de escola."""
        resposta = cliente_api.get(
            self.url,
            {"tipo_escola": str(tipo_escola_emef.uuid)},
        )

        assert resposta.status_code == status.HTTP_200_OK

        resultados = resposta.data["results"]

        assert len(resultados) == 2
        assert {resultado["uuid"] for resultado in resultados} == {
            str(unidade_educacional_emef.uuid),
            str(unidade_educacional_inativa_emef.uuid),
        }

    def test_deve_filtrar_por_diretoria_regional(
        self,
        cliente_api,
        unidade_educacional_emef,
        unidade_educacional_inativa_emef,
        diretoria_regional_centro,
    ):
        """Deve filtrar unidades pela diretoria regional."""
        resposta = cliente_api.get(
            self.url,
            {"diretoria_regional": diretoria_regional_centro.id},
        )

        assert resposta.status_code == status.HTTP_200_OK

        resultados = resposta.data["results"]

        assert len(resultados) == 2
        assert {resultado["uuid"] for resultado in resultados} == {
            str(unidade_educacional_emef.uuid),
            str(unidade_educacional_inativa_emef.uuid),
        }

    def test_deve_filtrar_por_subprefeitura(
        self,
        cliente_api,
        unidade_educacional_emef,
        unidade_educacional_inativa_emef,
        subprefeitura_se,
    ):
        """Deve filtrar unidades pela subprefeitura."""
        resposta = cliente_api.get(
            self.url,
            {"subprefeitura": str(subprefeitura_se.uuid)},
        )

        assert resposta.status_code == status.HTTP_200_OK

        resultados = resposta.data["results"]

        assert len(resultados) == 2
        assert {resultado["uuid"] for resultado in resultados} == {
            str(unidade_educacional_emef.uuid),
            str(unidade_educacional_inativa_emef.uuid),
        }

    def test_deve_filtrar_por_multiplos_campos(
        self,
        cliente_api,
        unidade_educacional_emef,
        tipo_escola_emef,
        diretoria_regional_centro,
        subprefeitura_se,
    ):
        """Deve filtrar por múltiplos campos."""
        resposta = cliente_api.get(
            self.url,
            {
                "tipo_escola": str(tipo_escola_emef.uuid),
                "diretoria_regional": diretoria_regional_centro.id,
                "subprefeitura": str(subprefeitura_se.uuid),
                "status": "true",
            },
        )

        assert resposta.status_code == status.HTTP_200_OK

        resultados = resposta.data["results"]

        assert len(resultados) == 1
        assert resultados[0]["uuid"] == str(
            unidade_educacional_emef.uuid,
        )

    def test_deve_retornar_404_para_uuid_inexistente(
        self,
        cliente_api,
    ):
        """Deve retornar 404 quando o UUID não existir."""
        resposta = cliente_api.get(
            f"{self.url}{uuid.uuid4()}/",
        )

        assert resposta.status_code == status.HTTP_404_NOT_FOUND

    def test_nao_deve_permitir_criacao(
        self,
        cliente_api,
    ):
        """Não deve permitir criação de unidades educacionais."""
        resposta = cliente_api.post(
            self.url,
            data={
                "codigo_eol": "999999",
                "nome": "Unidade Teste",
            },
            format="json",
        )

        assert resposta.status_code == (status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_nao_deve_permitir_atualizacao(
        self,
        cliente_api,
        unidade_educacional_emef,
    ):
        """Não deve permitir atualização de unidades educacionais."""
        resposta = cliente_api.put(
            f"{self.url}{unidade_educacional_emef.uuid}/",
            data={
                "codigo_eol": "999999",
                "nome": "Unidade Alterada",
            },
            format="json",
        )

        assert resposta.status_code == (status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_nao_deve_permitir_atualizacao_parcial(
        self,
        cliente_api,
        unidade_educacional_emef,
    ):
        """Não deve permitir atualização parcial."""
        resposta = cliente_api.patch(
            f"{self.url}{unidade_educacional_emef.uuid}/",
            data={"nome": "Unidade Alterada"},
            format="json",
        )

        assert resposta.status_code == (status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_nao_deve_permitir_exclusao(
        self,
        cliente_api,
        unidade_educacional_emef,
    ):
        """Não deve permitir exclusão de unidades educacionais."""
        resposta = cliente_api.delete(
            f"{self.url}{unidade_educacional_emef.uuid}/",
        )

        assert resposta.status_code == (status.HTTP_405_METHOD_NOT_ALLOWED)

        assert Unidadeeducacional.objects.filter(
            uuid=unidade_educacional_emef.uuid,
        ).exists()
