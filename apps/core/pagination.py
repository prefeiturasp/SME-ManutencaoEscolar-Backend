"""Classes de paginação compartilhadas pelos endpoints da API."""

from typing import Any

from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response


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

    def paginate_queryset(
        self,
        queryset: Any,
        request: Request,
        view: Any = None,
    ) -> Any:
        """Retorna todos os registros quando ``page_size=all``.

        Args:
            queryset: Conjunto de registros a ser paginado.
            request: Requisição HTTP recebida pela API.
            view: View que solicitou a paginação.

        Returns:
            Any: Registros paginados ou todos os registros.
        """
        if request.query_params.get(self.page_size_query_param) == "all":
            self._all_requested = True
            return queryset

        self._all_requested = False
        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data: Any) -> Response:
        """Monta a resposta paginada.

        Args:
            data: Dados serializados da página atual.

        Returns:
            Response: Resposta com os metadados e os registros.
        """
        if getattr(self, "_all_requested", False):
            return Response(
                {
                    "count": len(data),
                    "next": None,
                    "previous": None,
                    "results": data,
                },
            )

        return super().get_paginated_response(data)
