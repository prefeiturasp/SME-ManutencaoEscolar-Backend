"""Views da API da aplicação Core."""

from typing import Any

from drf_spectacular.utils import (
    extend_schema,
)
from rest_framework import status
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from apps.core.exceptions import (
    FalhaAutenticacaoError,
    InternalError,
    SmeIntegracaoError,
    TokenInvalidoError,
)
from apps.core.schemas import LOGIN
from apps.core.serializers import (
    AtualizarTokenSerializer,
    AutenticacaoSerializer,
    LoginResponseSerializer,
    LogoutSerializer,
)
from apps.core.services.autenticacao_eol_service import AutenticacaoEOLService
from apps.core.services.token_service import TokenService
from apps.usuarios.exceptions import UsuarioNaoEncontradoError


class HealthCheckView(APIView):
    """View para verificação de integridade do sistema."""

    permission_classes = [AllowAny]

    @extend_schema(
        auth=[],
        summary="Endpoint de Health Check",
        description=(
            "Retorna o status atual da aplicação para os "
            "orquestradores de cluster."
        ),
        responses={200: dict},
    )
    def get(self, request: Request) -> Response:
        """Retorna o status OK da aplicação de forma pública.

        Args:
            request: Objeto contendo os dados da requisição HTTP.

        Returns:
            Objeto Response contendo um dicionário informando o status 'ok'.
        """
        return Response({"status": "ok"})


class LoginView(TokenObtainPairView):
    """View responsavel por autenticação."""

    # TokenObtainPairView herda de TokenViewBase, que define permission_classes
    # como uma tupla
    permission_classes: tuple = (AllowAny,)

    @LOGIN
    def post(self, request: Request) -> Response:
        serializer = AutenticacaoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        login = serializer.validated_data["login"]
        senha = serializer.validated_data["senha"]
        try:
            dados_autenticacao = AutenticacaoEOLService.login(
                login=login,
                senha=senha,
            )
            response_serializer = LoginResponseSerializer(
                data=dados_autenticacao
            )
            response_serializer.is_valid(raise_exception=True)

            return Response(
                response_serializer.validated_data, status=status.HTTP_200_OK
            )
        except FalhaAutenticacaoError:
            return Response(
                {"detail": "Usuário e/ou senha inválida"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        except SmeIntegracaoError:
            return Response(
                {
                    "detail": "Parece que estamos com uma instabilidade no "
                    "momento. Tente entrar novamente daqui a pouco."
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        except InternalError:
            return Response(
                {
                    "detail": "Parece que estamos com uma instabilidade no "
                    "momento. Tente entrar novamente daqui a pouco."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class AtualizarTokenView(TokenRefreshView):
    """View responsavel por atualização de token."""

    # TokenRefreshView herda de TokenViewBase, que define permission_classes
    # como uma tupla
    permission_classes: tuple = (AllowAny,)

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = AtualizarTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            TokenService.atualizar_token(serializer.validated_data["refresh"])
        except TokenError:
            return Response(
                {"detail": "Refresh token inválido."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except UsuarioNaoEncontradoError as exc:
            return Response(
                {"detail": exc.detail},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return super().post(request, *args, **kwargs)


class LogoutView(APIView):
    """View responsável por realizar o logout do usuário autenticado."""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        id_usuario = request.user.id

        if id_usuario is None:
            return Response(
                {"detail": "Usuário autenticado inválido."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            TokenService.logout(
                id_usuario, serializer.validated_data["refresh"]
            )
        except TokenInvalidoError as exc:
            return Response(
                {"detail": exc.detail},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return Response(
            {"detail": "Logout realizado com sucesso."},
            status=status.HTTP_205_RESET_CONTENT,
        )
