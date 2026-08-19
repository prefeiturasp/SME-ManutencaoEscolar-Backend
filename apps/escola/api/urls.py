"""Url do app escola."""

from rest_framework.routers import DefaultRouter

from apps.escola.api.views import TipoEscolaViewSet

router = DefaultRouter()
router.register(
    r"tipos-escola",
    TipoEscolaViewSet,
    basename="tipos-escola",
)

urlpatterns = router.urls
