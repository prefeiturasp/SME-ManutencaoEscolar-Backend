"""Views da API da aplicação Core."""

from drf_spectacular.utils import (
    extend_schema,
)
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.schemas import LOGIN
from apps.core.serializers import AutenticacaoSerializer
from apps.core.services.autenticacao_eol_service import AutenticacaoEOLService


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
class LoginView(APIView):
    """View responsavel por autenticação."""

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = AutenticacaoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        dados_autenticacao = AutenticacaoEOLService.autentica(
            login=serializer.validated_data["login"],
            senha=serializer.validated_data["senha"],
        )

        return Response(dados_autenticacao, status=status.HTTP_200_OK)
