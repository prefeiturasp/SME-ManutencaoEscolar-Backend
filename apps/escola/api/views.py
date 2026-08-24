"""View do app escola."""

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from apps.core.pagination import PaginacaoPadrao
from apps.escola.filters import TipoEscolaFilter
from apps.escola.models import TipoEscola
from apps.escola.models.diretoria_regional import DiretoriaRegional
from apps.escola.schemas import (
    DIRETORIA_REGIONAL,
    TIPO_ESCOLA,
)
from apps.escola.serializers import (
    DiretoriaRegionalSerializer,
    TipoEscolaSerializer,
)


@TIPO_ESCOLA
class TipoEscolaViewSet(viewsets.ReadOnlyModelViewSet):
    """Disponibiliza somente operações de leitura para tipos de escola.

    O endpoint permite consultar a lista de tipos de escola e obter os dados
    de um tipo específico. Operações de criação, atualização e exclusão não
    estão disponíveis.
    """

    queryset = TipoEscola.objects.all()
    serializer_class = TipoEscolaSerializer
    lookup_field = "uuid"

    filter_backends = [DjangoFilterBackend]
    filterset_class = TipoEscolaFilter
    pagination_class = PaginacaoPadrao


@DIRETORIA_REGIONAL
class DiretoriaRegionalViewSet(viewsets.ReadOnlyModelViewSet):
    """Disponibiliza operações de leitura para diretorias regionais."""

    http_method_names = ["get", "options"]
    queryset = DiretoriaRegional.objects.all()
    serializer_class = DiretoriaRegionalSerializer
    lookup_field = "id"
    pagination_class = PaginacaoPadrao
