"""Url do app escola."""

from rest_framework.routers import DefaultRouter

from apps.escola.api.views import TipoEscolaViewSet

router = DefaultRouter()
router.register(
    r"tipos-unidade",
    TipoEscolaViewSet,
    basename="tipo-unidade",
)

urlpatterns = router.urls
