"""Permissões de acesso para serviços."""

from typing import Any

from rest_framework.permissions import BasePermission
from rest_framework.request import Request

from apps.usuarios.permissions import PermissaoCadastros, PermissaoPerfilDRE


class PermissaoLeituraUnidadeEscolar(BasePermission):
    """Permite acesso a leitura de unidades escolares."""

    message = PermissaoCadastros.message

    def has_permission(self, request: Request, view: Any) -> bool:
        """Verifica se o usuário pode listar unidades escolares."""
        return PermissaoCadastros().has_permission(
            request, view
        ) or PermissaoPerfilDRE().has_permission(request, view)
