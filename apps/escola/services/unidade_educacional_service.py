"""Service de unidades educacionais."""

from typing import Any

from apps.escola.models.unidade_educacional import Unidadeeducacional
from apps.escola.repository.unidade_educacional_repository import (
    UnidadeEducacionalRepository,
)
from apps.escola.services.responsavel_unidade_service import (
    ResponsavelUnidadeService,
)
from apps.usuarios.models.usuario import Usuario


class UnidadeEducacionalService:
    """Contém as regras de negócio da unidade educacional."""

    def __init__(
        self,
        repository: UnidadeEducacionalRepository | None = None,
        responsavel_service: ResponsavelUnidadeService | None = None,
    ) -> None:
        """Inicializa o service com suas dependências."""
        self.repository = repository or UnidadeEducacionalRepository()
        self.responsavel_service = (
            responsavel_service or ResponsavelUnidadeService()
        )

    def atualizar(
        self,
        unidade: Unidadeeducacional,
        dados: dict[str, Any],
        usuario: Usuario | None,
    ) -> dict[str, Any]:
        """Atualiza uma unidade educacional.

        Args:
            unidade: Unidade educacional que será atualizada.
            dados: Dados validados para atualização.
            usuario: Usuário responsável pela operação.

        Returns:
            Dados da unidade educacional atualizada.
        """
        dados_atualizacao = dados.copy()

        responsaveis = dados_atualizacao.pop(
            "responsaveis",
            [],
        )

        self.responsavel_service.validar_registros_funcionais(
            responsaveis=responsaveis,
        )

        self.responsavel_service.validar_responsaveis_da_unidade(
            unidade=unidade,
            responsaveis=responsaveis,
        )

        return self.repository.atualizar(
            unidade=unidade,
            dados=dados_atualizacao,
            responsaveis=responsaveis,
            usuario=usuario,
        )
