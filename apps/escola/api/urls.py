"""Url do app escola."""

from rest_framework.routers import DefaultRouter

from apps.escola.api.views import (
    DiretoriaRegionalViewSet,
    SubprefeituraViewSet,
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
    r"diretorias-regionais",
    DiretoriaRegionalViewSet,
    basename="diretorias-regionais",
)

router.register(
    r"unidades-educacionais",
    UnidadeEducacionalViewSet,
    basename="unidades-educacionais",
)

router.register(
    r"subprefeituras",
    SubprefeituraViewSet,
    basename="subprefeituras",
)


urlpatterns = router.urls
