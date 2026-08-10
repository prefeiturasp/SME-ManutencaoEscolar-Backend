"""Serviços de Empresa."""

from typing import Any

from apps.empresa.repository.empresa_repository import (
    EmpresaRepository,
)


class EmpresaService:
    """Orquestra as regras de negócio relacionadas a Empresa."""

    def __init__(self, repository: EmpresaRepository | None = None):
        """Inicializa o serviço com o repositório informado ou o padrão."""
        self.repository = repository or EmpresaRepository()

    def criar(self, dados: dict[str, Any]) -> dict[str, Any]:
        """Cria uma empresa e retorna seus dados serializados."""
        return self.repository.criar(dados)
