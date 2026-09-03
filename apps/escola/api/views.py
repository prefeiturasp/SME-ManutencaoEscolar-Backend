"""View do app escola."""

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from apps.core.pagination import PaginacaoPadrao
from apps.escola.filters import (
    DiretoriaRegionalFilter,
    SubprefeituraFilter,
    TipoEscolaFilter,
    UnidadeEducacionalFilter,
)
from apps.escola.models import (
    DiretoriaRegional,
    Subprefeitura,
    TipoEscola,
    Unidadeeducacional,
)
from apps.escola.schemas import (
    DIRETORIA_REGIONAL,
    SUBPREFEITURA,
    TIPO_ESCOLA,
    UNIDADE_EDUCACIONAL,
)
from apps.escola.serializers import (
    DiretoriaRegionalSerializer,
    SubprefeituraSerializer,
    TipoEscolaSerializer,
    UnidadeEducacionalSerializer,
)


@TIPO_ESCOLA
class TipoEscolaViewSet(viewsets.ReadOnlyModelViewSet):
    """Disponibiliza somente operações de leitura para tipos de escola.

    O endpoint permite consultar a lista de tipos de escola e obter os dados
    de um tipo específico. Operações de criação, atualização e exclusão não
    estão disponíveis.
    """

    http_method_names = ["get", "options"]
    queryset = TipoEscola.objects.aceitos()
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

    filter_backends = [DjangoFilterBackend]
    filterset_class = DiretoriaRegionalFilter
    pagination_class = PaginacaoPadrao


@SUBPREFEITURA
class SubprefeituraViewSet(viewsets.ReadOnlyModelViewSet):
    """Disponibiliza operações de leitura para subprefeituras."""

    http_method_names = ["get", "options"]
    queryset = Subprefeitura.objects.all()
    serializer_class = SubprefeituraSerializer
    lookup_field = "uuid"

    filter_backends = [DjangoFilterBackend]
    filterset_class = SubprefeituraFilter
    pagination_class = PaginacaoPadrao


@UNIDADE_EDUCACIONAL
class UnidadeEducacionalViewSet(viewsets.ReadOnlyModelViewSet):
    """Disponibiliza operações de leitura para unidades educacionais."""

    http_method_names = ["get", "options"]
    queryset = Unidadeeducacional.objects.select_related(
        "diretoria_regional",
        "tipo_escola",
        "subprefeitura",
    ).prefetch_related(
        "diretoria_regional__vinculo_lote__lote",
    )
    serializer_class = UnidadeEducacionalSerializer
    lookup_field = "uuid"

    filter_backends = [DjangoFilterBackend]
    filterset_class = UnidadeEducacionalFilter
    pagination_class = PaginacaoPadrao
