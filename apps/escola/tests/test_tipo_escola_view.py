import pytest
from rest_framework import status

from apps.escola.models import TipoEscola

pytestmark = pytest.mark.django_db


class TestTipoEscolaViewSet:
    """Testes do ViewSet de tipos de escola."""

    url = "/api/v1/tipos-escola/"

    def test_deve_listar_tipos_de_escola(
        self,
        cliente_api,
        tipos_escola,
    ):
        """Deve retornar os tipos de escola cadastrados."""
        resposta = cliente_api.get(self.url)

        assert resposta.status_code == status.HTTP_200_OK

        resultados = resposta.data["results"]

        assert len(resultados) == 2
        assert {resultado["codigo_eol"] for resultado in resultados} == {
            1,
            2,
        }

    def test_deve_buscar_tipo_de_escola_por_uuid(
        self,
        cliente_api,
        tipos_escola,
    ):
        """Deve retornar um tipo de escola pelo UUID."""
        tipo_escola = tipos_escola[0]

        resposta = cliente_api.get(f"{self.url}{tipo_escola.uuid}/")

        assert resposta.status_code == status.HTTP_200_OK
        assert resposta.data == {
            "id": tipo_escola.id,
            "uuid": str(tipo_escola.uuid),
            "codigo_eol": tipo_escola.codigo_eol,
            "sigla": tipo_escola.sigla,
        }

    def test_deve_retornar_404_para_uuid_inexistente(
        self,
        cliente_api,
    ):
        """Deve retornar 404 quando o UUID não existir."""
        import uuid

        resposta = cliente_api.get(f"{self.url}{uuid.uuid4()}/")

        assert resposta.status_code == status.HTTP_404_NOT_FOUND

    def test_nao_deve_permitir_criacao(
        self,
        cliente_api,
    ):
        """Não deve permitir criação de tipos de escola."""
        resposta = cliente_api.post(
            self.url,
            data={
                "codigo_eol": 10,
                "sigla": "EMEF",
            },
            format="json",
        )

        assert resposta.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_nao_deve_permitir_atualizacao(
        self,
        cliente_api,
        tipos_escola,
    ):
        """Não deve permitir atualização de tipos de escola."""
        tipo_escola = tipos_escola[0]

        resposta = cliente_api.put(
            f"{self.url}{tipo_escola.uuid}/",
            data={
                "codigo_eol": 10,
                "sigla": "EMEI",
            },
            format="json",
        )

        assert resposta.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_nao_deve_permitir_atualizacao_parcial(
        self,
        cliente_api,
        tipos_escola,
    ):
        """Não deve permitir atualização parcial de tipos de escola."""
        tipo_escola = tipos_escola[0]

        resposta = cliente_api.patch(
            f"{self.url}{tipo_escola.uuid}/",
            data={
                "sigla": "EMEI",
            },
            format="json",
        )

        assert resposta.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_nao_deve_permitir_exclusao(
        self,
        cliente_api,
        tipos_escola,
    ):
        """Não deve permitir exclusão de tipos de escola."""
        tipo_escola = tipos_escola[0]

        resposta = cliente_api.delete(f"{self.url}{tipo_escola.uuid}/")

        assert resposta.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

        assert TipoEscola.objects.filter(uuid=tipo_escola.uuid).exists()
