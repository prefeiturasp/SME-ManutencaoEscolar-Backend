"""Filtros da API de solicitações de manutenção."""

import django_filters

from apps.solicitacao_manutencao.models import SolicitacaoManutencao


class CharInFilter(django_filters.BaseInFilter, django_filters.CharFilter):
    """Filtra um campo textual por múltiplos valores."""

    pass


class SolicitacaoManutencaoFilter(django_filters.FilterSet):
    """Filtra solicitações pelos dados exibidos na listagem."""

    codigo = django_filters.CharFilter(lookup_expr="icontains")
    tipo_atendimento = CharInFilter(lookup_expr="in")
    situacao = CharInFilter(lookup_expr="in")
    fase = CharInFilter(lookup_expr="in")
    data_envio = django_filters.DateFromToRangeFilter()

    class Meta:
        """Configura os filtros de solicitação de manutenção."""

        model = SolicitacaoManutencao
        fields = (
            "codigo",
            "tipo_atendimento",
            "situacao",
            "fase",
            "data_envio",
        )
