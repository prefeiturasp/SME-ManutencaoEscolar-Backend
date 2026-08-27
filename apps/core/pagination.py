"""Classes de paginação compartilhadas pela API."""

from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request


class PaginacaoPadrao(PageNumberPagination):
    """Define a paginação padrão das listagens."""

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_page_size(self, request: Request) -> int | None:
        """Obtém a quantidade de registros da página.

        Args:
            request: Requisição HTTP recebida pela API.

        Returns:
            Quantidade de registros por página ou ``None`` para
            desabilitar a paginação.
        """
        page_size = request.query_params.get(
            self.page_size_query_param,
        )

        if page_size == "all":
            return None

        return super().get_page_size(request)
