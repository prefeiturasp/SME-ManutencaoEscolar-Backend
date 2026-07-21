"""Views da API da aplicação Core."""

from drf_spectacular.utils import (
    extend_schema,
)
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.core.exceptions import (
    FalhaAutenticacaoError,
    InternalError,
    SmeIntegracaoError,
)
from apps.core.schemas import LOGIN
from apps.core.serializers import AutenticacaoSerializer
from apps.core.services.autenticacao_eol_service import AutenticacaoEOLService
from apps.core.services.token_service import TokenService
from apps.usuarios.services.usuario_service import UsuarioService

DADO_NAO_INFORMADO = "Não informado"


class HealthCheckView(APIView):
    """View para verificação de integridade do sistema."""

    permission_classes = [AllowAny]

    @extend_schema(
        summary="Endpoint de Health Check 2",
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


@LOGIN
class LoginView(TokenObtainPairView):
    """View responsavel por autenticação."""

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = AutenticacaoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        login = serializer.validated_data["login"]
        senha = serializer.validated_data["senha"]
        try:
            dados_autenticacao = AutenticacaoEOLService.autentica(
                login=login,
                senha=senha,
            )
            informaoes_cargo = AutenticacaoEOLService.buscar_cargos(
                registro_funcional=dados_autenticacao["codigoRf"]
            )
            dados_usuario = AutenticacaoEOLService.dados_usuario(
                dados_autenticacao["codigoRf"]
            )
            usuario = UsuarioService.sincronizar_usuario(
                nome=dados_usuario["nome"],
                email=dados_usuario["email"],
                registro_funcional=dados_usuario["codigo_rf"],
                cpf=dados_usuario["cpf"],
                codigo_cargo=informaoes_cargo["codigo_cargo"],
                nome_cargo=informaoes_cargo["nome_cargo"],
            )
            token = TokenService.gerar_tokens(usuario["id"])
            response = {
                "refresh": token["refresh"],
                "access": token["access"],
                "dados_usuario": {
                    "nome": dados_usuario.get("nome", DADO_NAO_INFORMADO),
                    "codigo_rf_ou_cpf": dados_usuario.get(
                        "codigoRf", DADO_NAO_INFORMADO
                    ),
                    "diretoria_regional": dados_usuario.get(
                        "dre", DADO_NAO_INFORMADO
                    ),
                    "unidade_educacional": dados_usuario.get(
                        "nomeUe", DADO_NAO_INFORMADO
                    ),
                    "permissao": dados_usuario["cargo"],
                },
            }

            return Response(response, status=status.HTTP_200_OK)
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
