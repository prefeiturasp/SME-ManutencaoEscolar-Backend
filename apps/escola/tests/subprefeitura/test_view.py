"""Teste da view de Subprefeitura."""

import uuid

import pytest
from rest_framework import status

from apps.escola.models import (
    Subprefeitura,
)

pytestmark = pytest.mark.django_db


class TestSubprefeituraViewSet:
    """Testes do ViewSet de subprefeituras."""

    url = "/api/v1/subprefeituras/"

    def test_deve_listar_subprefeituras(
        self,
        cliente_api,
        subprefeitura_se,
        subprefeitura_pirituba,
    ):
        """Deve retornar as subprefeituras cadastradas."""
        resposta = cliente_api.get(self.url)

        assert resposta.status_code == status.HTTP_200_OK

        resultados = resposta.data["results"]

        assert len(resultados) == 2
        assert {resultado["codigo_eol"] for resultado in resultados} == {
            subprefeitura_se.codigo_eol,
            subprefeitura_pirituba.codigo_eol,
        }

    def test_deve_buscar_subprefeitura_por_uuid(
        self,
        cliente_api,
        subprefeitura_se,
    ):
        """Deve retornar uma subprefeitura pelo UUID."""
        resposta = cliente_api.get(
            f"{self.url}{subprefeitura_se.uuid}/",
        )

        assert resposta.status_code == status.HTTP_200_OK

        assert resposta.data == {
            "id": subprefeitura_se.id,
            "uuid": str(subprefeitura_se.uuid),
            "codigo_eol": subprefeitura_se.codigo_eol,
            "nome": subprefeitura_se.nome,
        }

    def test_deve_filtrar_por_nome(
        self,
        cliente_api,
        subprefeitura_se,
        subprefeitura_pirituba,
    ):
        """Deve filtrar subprefeituras pelo nome."""
        resposta = cliente_api.get(
            self.url,
            {"nome": "sé"},
        )

        assert resposta.status_code == status.HTTP_200_OK

        resultados = resposta.data["results"]

        assert len(resultados) == 1
        assert resultados[0]["uuid"] == str(
            subprefeitura_se.uuid,
        )

    def test_deve_filtrar_por_codigo_eol(
        self,
        cliente_api,
        subprefeitura_se,
    ):
        """Deve filtrar subprefeituras pelo código EOL."""
        resposta = cliente_api.get(
            self.url,
            {"codigo_eol": subprefeitura_se.codigo_eol},
        )

        assert resposta.status_code == status.HTTP_200_OK

        resultados = resposta.data["results"]

        assert len(resultados) == 1
        assert resultados[0]["uuid"] == str(
            subprefeitura_se.uuid,
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
        """Não deve permitir criação de subprefeituras."""
        resposta = cliente_api.post(
            self.url,
            data={
                "codigo_eol": "SP99",
                "nome": "Subprefeitura Teste",
            },
            format="json",
        )

        assert resposta.status_code == (status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_nao_deve_permitir_atualizacao(
        self,
        cliente_api,
        subprefeitura_se,
    ):
        """Não deve permitir atualização de subprefeituras."""
        resposta = cliente_api.put(
            f"{self.url}{subprefeitura_se.uuid}/",
            data={
                "codigo_eol": "SP99",
                "nome": "Subprefeitura Alterada",
            },
            format="json",
        )

        assert resposta.status_code == (status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_nao_deve_permitir_atualizacao_parcial(
        self,
        cliente_api,
        subprefeitura_se,
    ):
        """Não deve permitir atualização parcial."""
        resposta = cliente_api.patch(
            f"{self.url}{subprefeitura_se.uuid}/",
            data={"nome": "Subprefeitura Alterada"},
            format="json",
        )

        assert resposta.status_code == (status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_nao_deve_permitir_exclusao(
        self,
        cliente_api,
        subprefeitura_se,
    ):
        """Não deve permitir exclusão de subprefeituras."""
        resposta = cliente_api.delete(
            f"{self.url}{subprefeitura_se.uuid}/",
        )

        assert resposta.status_code == (status.HTTP_405_METHOD_NOT_ALLOWED)

        assert Subprefeitura.objects.filter(
            uuid=subprefeitura_se.uuid,
        ).exists()
