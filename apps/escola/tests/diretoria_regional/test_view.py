"""Teste da view de Diretoria Regional."""

import pytest
from rest_framework import status

from apps.escola.models import (
    DiretoriaRegional,
)

pytestmark = pytest.mark.django_db


class TestDiretoriaRegionalViewSet:
    """Testes do ViewSet de diretorias regionais."""

    url = "/api/v1/diretorias-regionais/"

    def test_deve_listar_diretorias_regionais(
        self,
        api_cliente,
        diretoria_regional_centro,
        diretoria_regional_ipiranga,
    ):
        """Deve retornar as diretorias regionais cadastradas."""
        resposta = api_cliente.get(self.url)

        assert resposta.status_code == status.HTTP_200_OK

        resultados = resposta.data["results"]

        assert len(resultados) == 2
        assert {resultado["codigo"] for resultado in resultados} == {
            diretoria_regional_centro.codigo,
            diretoria_regional_ipiranga.codigo,
        }

    def test_deve_buscar_diretoria_regional_por_id(
        self,
        api_cliente,
        diretoria_regional_centro,
    ):
        """Deve retornar uma diretoria regional pelo ID."""
        resposta = api_cliente.get(
            f"{self.url}{diretoria_regional_centro.id}/",
        )

        assert resposta.status_code == status.HTTP_200_OK

        assert resposta.data == {
            "id": diretoria_regional_centro.id,
            "codigo": diretoria_regional_centro.codigo,
            "nome": diretoria_regional_centro.nome,
            "nome_curto": diretoria_regional_centro.nome_curto,
            "abreviacao": diretoria_regional_centro.abreviacao,
        }

    def test_deve_filtrar_por_nome(
        self,
        api_cliente,
        diretoria_regional_centro,
        diretoria_regional_ipiranga,
    ):
        """Deve filtrar diretorias regionais pelo nome."""
        resposta = api_cliente.get(
            self.url,
            {"nome": "centro"},
        )

        assert resposta.status_code == status.HTTP_200_OK

        resultados = resposta.data["results"]

        assert len(resultados) == 1
        assert resultados[0]["id"] == diretoria_regional_centro.id

    def test_deve_filtrar_por_codigo(
        self,
        api_cliente,
        diretoria_regional_centro,
    ):
        """Deve filtrar diretorias regionais pelo código."""
        resposta = api_cliente.get(
            self.url,
            {"codigo": diretoria_regional_centro.codigo},
        )

        assert resposta.status_code == status.HTTP_200_OK

        resultados = resposta.data["results"]

        assert len(resultados) == 1
        assert resultados[0]["id"] == diretoria_regional_centro.id

    def test_deve_filtrar_por_abreviacao(
        self,
        api_cliente,
        diretoria_regional_centro,
    ):
        """Deve filtrar diretorias regionais pela abreviação."""
        resposta = api_cliente.get(
            self.url,
            {"abreviacao": diretoria_regional_centro.abreviacao},
        )

        assert resposta.status_code == status.HTTP_200_OK

        resultados = resposta.data["results"]

        assert len(resultados) == 1
        assert resultados[0]["id"] == diretoria_regional_centro.id

    def test_deve_retornar_404_para_id_inexistente(
        self,
        api_cliente,
    ):
        """Deve retornar 404 quando o ID não existir."""
        resposta = api_cliente.get(f"{self.url}999999/")

        assert resposta.status_code == status.HTTP_404_NOT_FOUND

    def test_nao_deve_permitir_criacao(
        self,
        api_cliente,
    ):
        """Não deve permitir criação de diretorias regionais."""
        resposta = api_cliente.post(
            self.url,
            data={
                "codigo": "DRE99",
                "nome": "DIRETORIA REGIONAL DE EDUCACAO TESTE",
                "abreviacao": "TT",
            },
            format="json",
        )

        assert resposta.status_code == (status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_nao_deve_permitir_atualizacao(
        self,
        api_cliente,
        diretoria_regional_centro,
    ):
        """Não deve permitir atualização de diretorias regionais."""
        resposta = api_cliente.put(
            f"{self.url}{diretoria_regional_centro.id}/",
            data={
                "codigo": "DRE99",
                "nome": "DIRETORIA REGIONAL DE EDUCACAO TESTE",
                "abreviacao": "TT",
            },
            format="json",
        )

        assert resposta.status_code == (status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_nao_deve_permitir_atualizacao_parcial(
        self,
        api_cliente,
        diretoria_regional_centro,
    ):
        """Não deve permitir atualização parcial."""
        resposta = api_cliente.patch(
            f"{self.url}{diretoria_regional_centro.id}/",
            data={"nome": "DIRETORIA ALTERADA"},
            format="json",
        )

        assert resposta.status_code == (status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_nao_deve_permitir_exclusao(
        self,
        api_cliente,
        diretoria_regional_centro,
    ):
        """Não deve permitir exclusão de diretorias regionais."""
        resposta = api_cliente.delete(
            f"{self.url}{diretoria_regional_centro.id}/",
        )

        assert resposta.status_code == (status.HTTP_405_METHOD_NOT_ALLOWED)

        assert DiretoriaRegional.objects.filter(
            id=diretoria_regional_centro.id,
        ).exists()
