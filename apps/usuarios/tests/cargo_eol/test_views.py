"""Testes da view de cargos EOL."""

import pytest
from rest_framework import status

from apps.usuarios.models import CargoEOL

pytestmark = pytest.mark.django_db


class TestCargoEOLViewSet:
    """Testes do ViewSet de cargos EOL."""

    url = "/api/v1/cargos-eol/"

    def test_deve_listar_cargos_eol(
        self,
        api_cliente,
        cargo_perfil_diretor,
        cargo_eol_coordenador,
    ):
        """Deve retornar os cargos EOL cadastrados."""
        resposta = api_cliente.get(self.url)

        assert resposta.status_code == status.HTTP_200_OK

        resultados = resposta.data["results"]

        assert len(resultados) == 10
        codigos = {resultado["codigo"] for resultado in resultados}
        assert cargo_perfil_diretor.codigo in codigos
        assert cargo_eol_coordenador.codigo in codigos

    def test_deve_buscar_cargo_eol_por_id(
        self,
        api_cliente,
        cargo_perfil_diretor,
    ):
        """Deve retornar um cargo EOL pelo ID."""
        resposta = api_cliente.get(
            f"{self.url}{cargo_perfil_diretor.id}/",
        )

        assert resposta.status_code == status.HTTP_200_OK

        assert resposta.data == {
            "id": cargo_perfil_diretor.id,
            "codigo": cargo_perfil_diretor.codigo,
            "nome": cargo_perfil_diretor.nome,
            "perfil": cargo_perfil_diretor.perfil,
            "ativo": cargo_perfil_diretor.ativo,
        }

    def test_deve_filtrar_por_codigo(
        self,
        api_cliente,
        cargo_perfil_diretor,
    ):
        """Deve filtrar cargos EOL pelo código."""
        resposta = api_cliente.get(
            self.url,
            {"codigo": cargo_perfil_diretor.codigo},
        )

        assert resposta.status_code == status.HTTP_200_OK

        resultados = resposta.data["results"]

        assert len(resultados) == 1
        assert resultados[0]["id"] == cargo_perfil_diretor.id

    def test_deve_filtrar_por_nome(
        self,
        api_cliente,
        cargo_perfil_diretor,
        cargo_eol_coordenador,
    ):
        """Deve filtrar cargos EOL pelo nome."""
        resposta = api_cliente.get(
            self.url,
            {"nome": "diretor"},
        )

        assert resposta.status_code == status.HTTP_200_OK

        resultados = resposta.data["results"]
        print(resultados)

        assert len(resultados) == 3
        ids = {resultado["id"] for resultado in resultados}
        assert cargo_perfil_diretor.id in ids
        assert cargo_eol_coordenador.id not in ids

    def test_deve_filtrar_por_perfil(
        self,
        api_cliente,
        cargo_perfil_diretor,
        cargo_eol_coordenador,
    ):
        """Deve filtrar cargos EOL pelo perfil."""
        resposta = api_cliente.get(
            self.url,
            {"perfil": cargo_perfil_diretor.perfil},
        )

        assert resposta.status_code == status.HTTP_200_OK

        resultados = resposta.data["results"]

        assert len(resultados) == 3
        ids = {resultado["id"] for resultado in resultados}
        assert cargo_perfil_diretor.id in ids
        assert cargo_eol_coordenador.id in ids

    def test_deve_filtrar_por_ativo(
        self,
        api_cliente,
        cargo_perfil_diretor,
        cargo_eol_coordenador,
    ):
        """Deve filtrar cargos EOL pelo status de atividade."""
        resposta = api_cliente.get(
            self.url,
            {"ativo": True},
        )

        assert resposta.status_code == status.HTTP_200_OK

        resultados = resposta.data["results"]

        assert len(resultados) == 10

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
        """Não deve permitir criação de cargos EOL."""
        resposta = api_cliente.post(
            self.url,
            data={
                "codigo": "9999",
                "nome": "CARGO TESTE",
                "perfil": None,
                "ativo": True,
            },
            format="json",
        )

        assert resposta.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_nao_deve_permitir_atualizacao(
        self,
        api_cliente,
        cargo_perfil_diretor,
    ):
        """Não deve permitir atualização de cargos EOL."""
        resposta = api_cliente.put(
            f"{self.url}{cargo_perfil_diretor.id}/",
            data={
                "codigo": "9999",
                "nome": "CARGO ALTERADO",
                "perfil": cargo_perfil_diretor.perfil,
                "ativo": True,
            },
            format="json",
        )

        assert resposta.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_nao_deve_permitir_atualizacao_parcial(
        self,
        api_cliente,
        cargo_perfil_diretor,
    ):
        """Não deve permitir atualização parcial."""
        resposta = api_cliente.patch(
            f"{self.url}{cargo_perfil_diretor.id}/",
            data={"nome": "CARGO ALTERADO"},
            format="json",
        )

        assert resposta.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_nao_deve_permitir_exclusao(
        self,
        api_cliente,
        cargo_perfil_diretor,
    ):
        """Não deve permitir exclusão de cargos EOL."""
        resposta = api_cliente.delete(
            f"{self.url}{cargo_perfil_diretor.id}/",
        )

        assert resposta.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

        assert CargoEOL.objects.filter(
            id=cargo_perfil_diretor.id,
        ).exists()
