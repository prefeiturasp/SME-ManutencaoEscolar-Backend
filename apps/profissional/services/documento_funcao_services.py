"""Serviços de documentos das funções profissionais."""

from typing import Any

from apps.profissional.repository.documento_funcao_repository import (
    DocumentoFuncaoProfissionalRepository,
)
from apps.usuarios.models import Usuario


class DocumentoFuncaoProfissionalService:
    """Sincroniza documentos vinculados a uma função profissional."""

    def __init__(
        self, repository: DocumentoFuncaoProfissionalRepository | None = None
    ) -> None:
        """
        Inicializa o repositório de documentos das funções profissionais.

        Args:
            repository: Repositório de documentos das funções profissionais
                a ser utilizado. Quando não informado, uma instância padrão de
                `DocumentoFuncaoProfissionalRepository` é criada.
        """
        self.repository = repository or DocumentoFuncaoProfissionalRepository()

    def sincronizar(
        self,
        funcao_id: int,
        documentos_lista: list[dict[str, Any]],
        usuario: Usuario | None = None,
    ) -> list[dict[str, Any]]:
        """
        Cria documentos conforme a lista informada.

        Args:
            funcao_id: ID da função à qual os documentos pertencem.
            documentos_lista: Lista contendo os dados dos documentos.
            usuario: Usuário que está realizando a operação.

        returns:
            Lista de documentos criados.
        """
        documentos = []
        for documento in documentos_lista:
            dados = {**documento}
            documento = self.repository.criar(
                {
                    **dados,
                    "funcao_profissional_id": funcao_id,
                    "criado_por": usuario,
                }
            )
            documentos.append(documento)
        return documentos
