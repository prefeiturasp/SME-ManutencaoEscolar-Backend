"""Permissões de acesso para serviços."""

from typing import Any

from rest_framework.permissions import BasePermission
from rest_framework.request import Request

from apps.usuarios.permissions import PermissaoCadastros, PermissaoPerfilUE


class PermissaoLeituraServico(BasePermission):
    """Permite acesso a leitura de serviços."""

    def has_permission(self, request: Request, view: Any) -> bool:
        """Verifica se o usuário pode listar serviços."""
        return PermissaoCadastros().has_permission(
            request, view
        ) or PermissaoPerfilUE().has_permission(request, view)
