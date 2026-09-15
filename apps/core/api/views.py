"""Views responsáveis pelos endpoints da aplicação Core.

Disponibiliza endpoints para verificação de saúde da aplicação, autenticação,
gerenciamento de tokens, recuperação de senha e gerenciamento de anexos.
"""

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
    """Disponibiliza o endpoint público de verificação da aplicação.

    Permite que orquestradores e mecanismos de monitoramento verifiquem
    se a aplicação está respondendo corretamente.
    """

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
    """Disponibiliza o endpoint de autenticação do usuário.

    Recebe as credenciais informadas pelo cliente, delega a autenticação
    ao serviço de integração com o EOL/CoreSSO e retorna os tokens JWT
    juntamente com os dados do usuário autenticado.
    """

    # TokenObtainPairView herda de TokenViewBase, que define permission_classes
    # como uma tupla
    permission_classes: tuple = (AllowAny,)

    @LOGIN
    def post(self, request: Request) -> Response:
        """Autentica o usuário e retorna os dados da sessão.

        Valida os dados de entrada, realiza a autenticação no EOL/CoreSSO
        e serializa a resposta contendo os tokens JWT e os dados do usuário.

        Args:
            request (Request): Requisição HTTP contendo login e senha.

        Returns:
            Response: Resposta HTTP com os tokens e dados do usuário em caso
                de sucesso.
        """
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
    """Disponibiliza o endpoint de atualização do access token.

    Antes de delegar a atualização ao fluxo padrão do Simple JWT, valida
    o refresh token e verifica se o usuário associado ainda está autorizado
    no CoreSSO.
    """

    @ATUALIZA_TOKEN
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Valida o refresh token e solicita a renovação da autenticação.

        O refresh token é validado e o usuário associado é consultado.
        Em seguida, verifica-se se o usuário continua autorizado no CoreSSO.
        Caso esteja válido, a implementação herdada de
        :class:`TokenRefreshView` gera o novo access token.

        Args:
            request (Request): Requisição HTTP contendo o refresh token.
            *args (Any): Argumentos posicionais recebidos pela view base.
            **kwargs (Any): Argumentos nomeados recebidos pela view base.

        Returns:
            Response: Resposta HTTP contendo o novo access token ou um erro
                de autenticação.
        """
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
    """Disponibiliza o endpoint de logout do usuário autenticado.

    O logout revoga o refresh token informado, impedindo sua reutilização
    para obtenção de novos tokens de acesso.
    """

    @LOGOUT
    def post(self, request: Request) -> Response:
        """Revoga o refresh token e encerra a sessão do usuário.

        Valida o refresh token recebido e verifica sua associação com o
        usuário autenticado antes de solicitar sua revogação.

        Args:
            request (Request): Requisição HTTP contendo o refresh token.

        Returns:
            Response: HTTP indicando o resultado da operação.
        """
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
    """Disponibiliza o endpoint para iniciar a recuperação de senha.

    Identifica o usuário pelo registro funcional ou CPF, solicita o envio
    do e-mail de recuperação e retorna o endereço de e-mail mascarado.
    """

    permission_classes = [AllowAny]

    @REDEFINIR_SENHA
    def post(self, request: Request) -> Response:
        """Solicita o envio de instruções para recuperação de senha.

        Após identificar o usuário e solicitar o envio do e-mail, mascara
        parte do endereço eletrônico antes de retorná-lo ao cliente.

        Args:
            request (Request): Requisição HTTP contendo o registro funcional
                ou CPF do usuário

        Returns:
            Response: Resposta HTTP contendo o e-mail mascarado.
        """
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
    """Disponibiliza o endpoint para alteração da senha do usuário.

    Valida o token de recuperação e, caso seja válido, solicita a alteração
    da senha do usuário no CoreSSO.
    """

    permission_classes = [AllowAny]

    @ALTERAR_SENHA
    def post(self, request: Request) -> Response:
        """Valida o token e altera a senha do usuário.

        Valida os dados da requisição, verifica o token de recuperação
        e solicita ao serviço de autenticação a alteração da senha no
        CoreSSO.

        Args:
            request (Request): Requisição HTTP contendo identificador,
                token e nova senha.

        Returns:
            Response: Resposta HTTP indicando o resultado da alteração.
        """
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
    """
    Disponibiliza os endpoints relacionados ao gerenciamento de anexos.

    Suporta o recebimento de arquivos por requisições multipart e delega
    a validação, preparação e persistência dos arquivos ao serviço
    especializado.
    """

    parser_classes = (MultiPartParser, FormParser, JSONParser)
    lookup_field = "uuid"

    @UPLOAD_ARQUIVO
    def post(self, request: Request) -> Response:
        """Recebe, valida e armazena um arquivo enviado pelo usuário.

        Valida o arquivo recebido pelo serializer, identifica o usuário
        autenticado e delega o processamento ao :class:`AnexoService`.

        Args:
            request (Request): Requisição HTTP contendo o arquivo no campo
                ``arquivo``.

        Returns:
            Response: Resposta HTTP com os dados do arquivo criado.
        """
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
