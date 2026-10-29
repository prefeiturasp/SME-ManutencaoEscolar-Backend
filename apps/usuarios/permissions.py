"""Permissões de acesso por perfil do app usuarios."""

from typing import Any

from rest_framework.permissions import BasePermission
from rest_framework.request import Request

from apps.usuarios.constants import Funcionalidade, PerfilAcesso


class PermissaoFuncionalidade(BasePermission):
    """Libera o acesso conforme a funcionalidade permitida ao perfil.

    As subclasses definem a ``funcionalidade`` exigida. Usuários não
    autenticados, sem cargo ou com perfil sem acesso recebem ``403``.
    """

    funcionalidade: str = ""
    message = "Você não tem permissão para acessar este recurso."

    def has_permission(self, request: Request, view: Any) -> bool:
        """Verifica se o usuário autenticado pode usar a funcionalidade."""
        usuario = request.user
        return bool(
            usuario
            and usuario.is_authenticated
            and usuario.tem_acesso(self.funcionalidade)
        )


class PermissaoCadastros(PermissaoFuncionalidade):
    """Libera o acesso aos cadastros (apenas perfil GME/SME)."""

    funcionalidade = Funcionalidade.CADASTROS


class PermissaoPerfilUE(BasePermission):
    """Libera o acesso exclusivamente a usuários do perfil UE."""

    message = "Acesso permitido somente para usuários do perfil UE."

    def has_permission(self, request: Request, view: Any) -> bool:
        """Verifica se o usuário autenticado pertence ao perfil UE."""
        usuario = request.user

        return bool(
            usuario
            and usuario.is_authenticated
            and usuario.perfil == PerfilAcesso.UE
        )
