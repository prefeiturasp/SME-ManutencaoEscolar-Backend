"""Rotas da API do domínio Fornecedor."""

from rest_framework.routers import DefaultRouter

from apps.fornecedor.api.views import FornecedorViewSet

router = DefaultRouter()
router.trailing_slash = "/?"
router.register(r"fornecedores", FornecedorViewSet)

urlpatterns = router.urls
