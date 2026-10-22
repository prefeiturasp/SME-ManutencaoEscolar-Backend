"""Views da API de solicitações de manutenção."""

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import NotAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.solicitacao_manutencao.models import SolicitacaoManutencao
from apps.solicitacao_manutencao.schemas import SOLICITACAO_MANUTENCAO_SCHEMA
from apps.solicitacao_manutencao.serializers import (
    SolicitacaoManutencaoCriarSerializer,
)
from apps.solicitacao_manutencao.services.ue_services import (
    SolicitacaoManutencaoUeService,
)
from apps.usuarios.models import Usuario


@SOLICITACAO_MANUTENCAO_SCHEMA
class SolicitacaoManutencaoViewSet(GenericViewSet):
    """Disponibiliza a criação de solicitações de manutenção."""

    queryset = SolicitacaoManutencao.objects.all()
    serializer_class = SolicitacaoManutencaoCriarSerializer
    http_method_names = ["post", "options"]

    @action(detail=False, methods=["post"], url_path="solicitacao-ue")
    def solicitacao_ue(self, request: Request) -> Response:
        """Cria uma solicitação de manutenção para uma UE.

        Args:
            request: Requisição com os dados da solicitação.

        Returns:
            Resposta com os dados da solicitação criada.

        Raises:
            NotAuthenticated: Se o usuário autenticado não for identificado.
        """
        usuario = request.user
        socitacao_service = SolicitacaoManutencaoUeService()
        if not isinstance(usuario, Usuario):
            raise NotAuthenticated("Usuário não identificado.")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        enviar = request.query_params.get("enviar") == "true"
        serializer.instance = socitacao_service.criar(
            serializer.validated_data,
            usuario,
            enviar=enviar,
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)
