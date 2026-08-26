"""Url do app escola."""

from rest_framework.routers import DefaultRouter

from apps.escola.api.views import (
    DiretoriaRegionalViewSet,
    TipoEscolaViewSet,
    UnidadeEducacionalViewSet,
)

router = DefaultRouter()
router.register(
    r"tipos-escola",
    TipoEscolaViewSet,
    basename="tipos-escola",
)

router.register(
    r"diretoria-regional",
    DiretoriaRegionalViewSet,
    basename="diregorias-regionais",
)

router.register(
    r"unidades-educacionais",
    UnidadeEducacionalViewSet,
    basename="unidades-educacionais",
)


urlpatterns = router.urls
