"""Views da API da aplicação Core."""

from typing import Any

from drf_spectacular.utils import (
    extend_schema,
)
from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import (
    AllowAny,
)
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from apps.core.exceptions import (
    AnexoArquivoError,
    EnvioEmailError,
    FalhaAutenticacaoError,
    InternalError,
    SmeIntegracaoError,
    TokenInvalidoError,
)
from apps.core.schemas import (
    ALTERAR_SENHA,
    ATUALIZA_TOKEN,
    LOGIN,
    LOGOUT,
    REDEFINIR_SENHA,
    UPLOAD_ARQUIVO,
)
from apps.core.serializers.anexo import (
    ArquivoResponseSerializer,
    ArquivoUploadSerializer,
)
from apps.core.serializers.autenticacao import (
    AlterarSenhaSerializer,
    AtualizarTokenSerializer,
    AutenticacaoSerializer,
    LoginResponseSerializer,
    LogoutSerializer,
    RecuperarSenhaSerializer,
)
from apps.core.services.anexo_service import AnexoService
from apps.core.services.autenticacao_eol_service import AutenticacaoEOLService
from apps.core.services.token_service import TokenService
from apps.usuarios.exceptions import (
    EmailUsuarioNaoEncontradoError,
    UsuarioNaoEncontradoError,
)
from apps.usuarios.services.usuario_service import UsuarioService


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

    @ATUALIZA_TOKEN
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = AtualizarTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            dados_usuario = TokenService.atualizar_token(
                serializer.validated_data["refresh"]
            )
            usuario_existe = AutenticacaoEOLService.usuario_existe_no_coresso(
                dados_usuario["username"]
            )
            if usuario_existe is False:
                return Response(
                    {"detail": "Usuário não autorizado."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

        except TokenInvalidoError:
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

    @LOGOUT
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


class RedefinirSenhaView(APIView):
    """View responsável por realizar o recuperar senha do usuário."""

    permission_classes = [AllowAny]

    @REDEFINIR_SENHA
    def post(self, request: Request) -> Response:
        serializer = RecuperarSenhaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rf_ou_cpf = serializer.validated_data["registro_funcional_ou_cpf"]
        try:
            usuario = UsuarioService.obter_usuario_por_rf_cpf(rf_ou_cpf)
            UsuarioService.enviar_email_recuperacao_senha(usuario)
        except UsuarioNaoEncontradoError as exc:
            return Response(
                {"title": exc.title, "detail": exc.detail},
                status=status.HTTP_404_NOT_FOUND,
            )
        except EmailUsuarioNaoEncontradoError as exc:
            return Response(
                {"title": exc.title, "detail": exc.detail},
                status=status.HTTP_404_NOT_FOUND,
            )
        except EnvioEmailError as exc:
            return Response(
                {"title": exc.title, "detail": exc.detail},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        parte_local, dominio = usuario["email"].rsplit("@", 1)
        quantidade_letras_visiveis = 3

        email_mascarado = (
            f"{parte_local[:quantidade_letras_visiveis]}"
            f"{'*' * (len(parte_local) - quantidade_letras_visiveis)}"
            f"@{dominio}"
        )

        return Response({"email": email_mascarado}, status=status.HTTP_200_OK)


class AlterarSenhaView(APIView):
    """View responsável por alterar a senha do usuário a partir do token."""

    permission_classes = [AllowAny]

    @ALTERAR_SENHA
    def post(self, request: Request) -> Response:
        serializer = AlterarSenhaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data["registro_funcional_ou_cpf"]
        token = serializer.validated_data["token"]
        senha = serializer.validated_data["senha"]

        try:
            TokenService.validar_token_recuperar_senha(username, token)
            AutenticacaoEOLService.alterar_senha_no_coresso(username, senha)
        except UsuarioNaoEncontradoError as exc:
            return Response(
                {"title": exc.title, "detail": exc.detail},
                status=status.HTTP_404_NOT_FOUND,
            )
        except TokenInvalidoError as exc:
            return Response(
                {"title": exc.title, "detail": exc.detail},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except FalhaAutenticacaoError as exc:
            return Response(
                {"title": "Erro ao alterar senha", "detail": str(exc)},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except SmeIntegracaoError as exc:
            return Response(
                {"title": "Erro ao alterar senha", "detail": str(exc)},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(
            {"detail": "Senha alterada com sucesso."},
            status=status.HTTP_200_OK,
        )


class AnexoView(APIView):
    """View responsável pelo gerenciamento de anexos."""

    parser_classes = (MultiPartParser, FormParser, JSONParser)
    lookup_field = "uuid"

    @UPLOAD_ARQUIVO
    def post(self, request: Request) -> Response:
        """Recebe, valida e armazena um arquivo enviado pelo usuário."""
        serializer = ArquivoUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        arquivo = serializer.validated_data["arquivo"]
        id_usuario = request.user.id
        if id_usuario is None:
            return Response(
                {"detail": "Usuário não autenticado."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            anexo = AnexoService().enviar_arquivo(arquivo, id_usuario)
            response = ArquivoResponseSerializer(anexo)
        except AnexoArquivoError as erro:
            return Response(
                {
                    "title": erro.title,
                    "detail": erro.detail,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except UsuarioNaoEncontradoError as erro:
            return Response(
                {
                    "title": erro.title,
                    "detail": erro.detail,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            response.data,
            status=status.HTTP_201_CREATED,
        )
