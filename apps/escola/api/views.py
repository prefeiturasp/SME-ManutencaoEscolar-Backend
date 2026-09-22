"""View do app escola."""

from typing import Any

from django.core.exceptions import ValidationError as DjangoValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.serializers import BaseSerializer
from rest_framework.serializers import ValidationError as DRFValidationError

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
from apps.escola.serializers.diretoria_regional_serializers import (
    DiretoriaRegionalSerializer,
)
from apps.escola.serializers.subprefeitura_serializers import (
    SubprefeituraSerializer,
)
from apps.escola.serializers.tipo_unidade_serializers import (
    TipoEscolaSerializer,
)
from apps.escola.serializers.unidade_educacional_serializers import (
    UnidadeEducacionalAtualizarSerializer,
    UnidadeEducacionalListSerializer,
    UnidadeEducacionalSerializer,
)
from apps.escola.services import UnidadeEducacionalService
from apps.usuarios.models.usuario import Usuario


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
class UnidadeEducacionalViewSet(viewsets.ModelViewSet):
    """Disponibiliza operações de leitura para unidades educacionais."""

    http_method_names = ["get", "put", "options"]
    queryset = Unidadeeducacional.objects.select_related(
        "diretoria_regional",
        "tipo_escola",
        "subprefeitura",
    ).prefetch_related(
        "diretoria_regional__vinculo_lote__lote",
    )

    lookup_field = "uuid"

    filter_backends = [DjangoFilterBackend]
    filterset_class = UnidadeEducacionalFilter
    pagination_class = PaginacaoPadrao

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.service = UnidadeEducacionalService()

    def get_serializer_class(self) -> type[BaseSerializer]:
        """Retorna o serializer adequado para cada operação."""
        if self.action == "list":
            return UnidadeEducacionalListSerializer
        if self.action == "update":
            return UnidadeEducacionalAtualizarSerializer
        return UnidadeEducacionalSerializer

    def _usuario_logado(self) -> Usuario | None:
        """Retorna o usuário autenticado da requisição, se houver."""
        usuario = self.request.user
        return usuario if usuario.is_authenticated else None

    def perform_update(self, serializer: BaseSerializer) -> None:
        """
        Atualiza uma unidade educacional existente usando o serviço.

        Args:
            serializer (BaseSerializer): Serializer contendo os dados da
                unidade educacional.

        Raises:
            DRFValidationError: Se ocorrer algum erro de validação.
        """
        try:
            unidade = self.service.atualizar(
                unidade=self.get_object(),
                dados=serializer.validated_data,
                usuario=self._usuario_logado(),
            )
        except DjangoValidationError as exc:
            raise DRFValidationError(exc.message_dict) from exc

        serializer.instance = unidade
