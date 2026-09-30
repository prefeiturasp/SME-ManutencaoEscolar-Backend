"""View responsável pelos endpoints relacionados aos cargos EOL.

Disponibiliza endpoints para consulta dos cargos EOL cadastrados no sistema,
com suporte a filtragem e paginação dos resultados.

"""

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from apps.core.pagination import PaginacaoPadrao
from apps.usuarios.filters import CargoEOLFilter
from apps.usuarios.models import CargoEOL
from apps.usuarios.schemas import CARGO_EOL
from apps.usuarios.serializers.cargo_eol_serializer import CargoEOLSerializer


@CARGO_EOL
class CargoEOLViewSet(viewsets.ReadOnlyModelViewSet):
    """Disponibiliza endpoints de consulta dos cargos EOL.

    Permite listar os cargos EOL cadastrados e consultar um cargo específico.
    Os resultados podem ser filtrados conforme os critérios definidos em
    ``CargoEOLFilter`` e são paginados utilizando ``PaginacaoPadrao``.

    Operações de criação, atualização e exclusão não estão disponíveis.
    """

    http_method_names = ["get", "options"]
    queryset = CargoEOL.objects.all()
    serializer_class = CargoEOLSerializer
    lookup_field = "id"

    filter_backends = [DjangoFilterBackend]
    filterset_class = CargoEOLFilter
    pagination_class = PaginacaoPadrao
