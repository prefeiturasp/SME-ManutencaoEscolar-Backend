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
        """Pagina o conjunto ou o retorna integralmente com ``page_size=all``.

        Nesse caso, preserva o queryset recebido e sinaliza que a resposta
        deve incluir os metadados de paginação sem links de navegação.

        Args:
            queryset: Conjunto de registros a ser paginado.
            request: Requisição HTTP recebida pela API.
            view: View que solicitou a paginação, quando disponível.

        Returns:
            Any: Página de registros, queryset integral ou ``None`` quando a
                paginação estiver desabilitada pela configuração da view.
        """
        if request.query_params.get(self.page_size_query_param) == "all":
            self._all_requested = True
            return queryset

        self._all_requested = False
        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data: Any) -> Response:
        """Monta a resposta com registros e metadados de paginação.

        Com ``page_size=all``, informa o total de registros serializados e
        define ``next`` e ``previous`` como ``None``. Nos demais casos,
        utiliza a resposta padrão do DRF.

        Args:
            data: Dados serializados da página ou do queryset integral.

        Returns:
            Response: Resposta com ``count``, ``next``, ``previous`` e
                ``results``.
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
