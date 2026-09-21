"""Serviços do domínio Profissional."""

from typing import Any

from django.db import transaction

from apps.profissional.repository.profissional_repository import (
    ProfissionalRepository,
)
from apps.profissional.services.funcao_profissional_services import (
    FuncaoProfissionalService,
)
from apps.usuarios.models import Usuario


class ProfissionalService:
    """Orquestra as regras de negócio relacionadas a profissionais."""

    def __init__(
        self,
        profissional_repository: ProfissionalRepository | None = None,
        funcao_profissional_service: FuncaoProfissionalService | None = None,
    ) -> None:
        """
        Inicializa o serviço e repositório necessários.

        Args:
            profissional_repository: Repositório de profissionais
                a ser utilizado. Quando não informado, uma instância padrão
                de `ProfissionalRepository` é criada.
            funcao_profissional_service: Serviço de funções profissionais
                a ser utilizado. Quando não informado, uma instância padrão
                de `FuncaoProfissionalService` é criada.
        """
        self.profissional_repository = (
            profissional_repository or ProfissionalRepository()
        )
        self.funcao_profissional_service = (
            funcao_profissional_service or FuncaoProfissionalService()
        )

    @transaction.atomic
    def criar(
        self, profissionais: dict[str, Any], usuario: Usuario | None = None
    ) -> dict[str, Any]:
        """
        Cria um profissional com suas funções e documentos.

        Args:
            profissionais: Dados do profissional e suas funções.
            usuario (Usuario | None): Usuário que está realizando a operação.

        Returns:
            Dados do profissional criado, incluindo funções e documentos.
        """
        dados = {**profissionais}
        funcoes = dados.pop("funcoes")
        profissional = self.profissional_repository.criar(
            {**dados, "criado_por": usuario}
        )
        funcoes_criadas = self.funcao_profissional_service.sincronizar(
            profissional["id"], funcoes, usuario
        )
        profissional["funcoes"] = funcoes_criadas
        return profissional
