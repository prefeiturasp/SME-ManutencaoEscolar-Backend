"""Classes de paginação compartilhadas pelos endpoints da API."""

from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request


class PaginacaoPadrao(PageNumberPagination):
    """Define a configuração padrão de paginação das listagens.

    As respostas utilizam 10 registros por página por padrão, permitem
    que o cliente solicite outro tamanho e limitam a página a 100 registros.

    O valor ``all`` no parâmetro ``page_size`` desabilita a paginação
    para a requisição atual.
    """

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_page_size(self, request: Request) -> int | None:
        """Obtém a quantidade de registros que deverá compor a página.

        Quando o parâmetro ``page_size`` possui o valor ``all``, a paginação
        é desabilitada para a requisição. Para os demais valores, o método
        utiliza a implementação padrão do Django REST Framework, incluindo
        as regras de limite configuradas na classe.

        Args:
            request (Request): Requisição HTTP recebida pela API.

        Returns:
            int | None: Quantidade de registros por página ou ``None`` para
            desabilitar a paginação.
        """
        page_size = request.query_params.get(
            self.page_size_query_param,
        )

        if page_size == "all":
            return None

        return super().get_page_size(request)
