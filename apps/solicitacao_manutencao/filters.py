"""Filtros da API de solicitações de manutenção."""

import django_filters

from apps.solicitacao_manutencao.models import SolicitacaoManutencao


class SolicitacaoManutencaoFilter(django_filters.FilterSet):
    """Filtra solicitações pelos dados exibidos na listagem."""

    codigo = django_filters.CharFilter(lookup_expr="icontains")
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
