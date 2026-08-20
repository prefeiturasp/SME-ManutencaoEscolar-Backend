"""Rotas da API do domínio Empresa."""

from rest_framework.routers import DefaultRouter

from apps.empresa.api.views.empresa_views import EmpresaViewSet
from apps.empresa.api.views.responsavel_views import ResponsavelTecnicoViewSet

router = DefaultRouter()
router.trailing_slash = "/?"
router.register(r"empresas", EmpresaViewSet)
router.register(r"responsaveis-tecnicos", ResponsavelTecnicoViewSet)

urlpatterns = router.urls
