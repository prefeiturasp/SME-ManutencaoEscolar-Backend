"""Rotas da API do domínio Empresa."""

from rest_framework.routers import DefaultRouter

from apps.empresa.api.views.empresa_views import EmpresaViewSet

router = DefaultRouter()
router.trailing_slash = "/?"
router.register(r"empresas", EmpresaViewSet)

urlpatterns = router.urls
