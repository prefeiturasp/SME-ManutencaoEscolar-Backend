"""Serviços de Empresa."""

from typing import Any

from apps.empresa.models import Empresa
from apps.empresa.repository.empresa_repository import (
    EmpresaRepository,
)
from apps.usuarios.models import Usuario


class EmpresaService:
    """Orquestra as regras de negócio relacionadas a Empresa."""

    def __init__(self, repository: EmpresaRepository | None = None):
        """Inicializa o serviço com o repositório informado ou o padrão.

        Args:
            repository: Repositório de empresas a ser utilizado. Quando não
                informado, uma instância padrão de `EmpresaRepository` é
                criada.
        """
        self.repository = repository or EmpresaRepository()

    def criar(
        self, dados: dict[str, Any], usuario: Usuario | None = None
    ) -> dict[str, Any]:
        """Cria uma empresa e retorna seus dados serializados.

        Registra o usuário logado como responsável pela criação.

        Args:
            dados: Dados da empresa a ser criada.
            usuario: Usuário logado responsável pela criação.

        Returns:
            Dados serializados da empresa criada.
        """
        return self.repository.criar({**dados, "criado_por": usuario})

    def atualizar(
        self,
        empresa: Empresa,
        dados: dict[str, Any],
        usuario: Usuario | None = None,
    ) -> dict[str, Any]:
        """Atualiza uma empresa existente e retorna seus dados serializados.

        Registra o usuário logado como responsável pela atualização.

        Args:
            empresa: Instância da empresa a ser atualizada.
            dados: Dados a serem aplicados na atualização.
            usuario: Usuário logado responsável pela atualização.

        Returns:
            Dados serializados da empresa atualizada.
        """
        return self.repository.atualizar(
            empresa, {**dados, "atualizado_por": usuario}
        )

    def deletar(
        self, empresa: Empresa, usuario: Usuario | None = None
    ) -> None:
        """Realiza a exclusão lógica de uma empresa.

        Registra o usuário logado como responsável pela exclusão.

        Args:
            empresa: Instância da empresa a ser deletada.
            usuario: Usuário logado responsável pela exclusão.
        """
        self.repository.deletar(empresa, usuario)
