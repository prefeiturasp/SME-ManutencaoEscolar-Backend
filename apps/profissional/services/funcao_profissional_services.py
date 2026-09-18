"""Serviços das funções dos profissionais."""

from typing import Any

from django.core.exceptions import ValidationError

from apps.profissional.constants import ProfissionalErrorMessages
from apps.profissional.repository.funcao_profissional_repository import (
    FuncaoProfissionalRepository,
)
from apps.profissional.services.documento_funcao_services import (
    DocumentoFuncaoProfissionalService,
)
from apps.usuarios.models import Usuario


class FuncaoProfissionalService:
    """Sincroniza as funções e seus documentos."""

    def __init__(
        self,
        repository: FuncaoProfissionalRepository | None = None,
        documento_service: DocumentoFuncaoProfissionalService | None = None,
    ) -> None:
        """
        Inicializa o serviço e repositório necessários.

        Args:
            repository: Repositório de funções profissionais a ser utilizado.
                Quando não informado, uma instância padrão de
                `FuncaoProfissionalRepository` é criada.
            documento_service: Serviço de documentos das funções profissionais
                a ser utilizado. Quando não informado, uma instância padrão de
                `DocumentoFuncaoProfissionalService` é criada.
        """
        self.repository = repository or FuncaoProfissionalRepository()
        self.documento_service = (
            documento_service or DocumentoFuncaoProfissionalService()
        )

    def sincronizar(
        self,
        profissional_id: int,
        funcoes_lista: list[dict[str, Any]],
        usuario: Usuario | None = None,
    ) -> list[dict[str, Any]]:
        """
        Cria funções conforme a lista informada.

        Args:
            profissional_id: ID do profissional ao qual as funções pertencem.
            funcoes_lista: Lista de dicionários contendo os dados das funções.
            usuario: Usuário que está realizando a operação.

        Returns:
            Lista de funções criadas.

        Raises:
            ValidationError: Se uma função exigir documentos e não houver
                documentos informados.
        """
        funcoes: list[dict[str, Any]] = []
        for funcao_dados in funcoes_lista:
            dados = {**funcao_dados}
            documentos = dados.pop("documentos", [])
            if dados["cargo"].exige_documento and not documentos:
                raise ValidationError(
                    {
                        "documentos": (
                            ProfissionalErrorMessages.DOCUMENTOS_FUNCAO_PROFISSIONAL_OBRIGATORIOS
                        )
                    }
                )
            funcao = self.repository.criar(
                {
                    **dados,
                    "profissional_id": profissional_id,
                    "criado_por": usuario,
                }
            )
            documentos_criados = self.documento_service.sincronizar(
                funcao["id"], documentos, usuario
            )
            funcao["documentos"] = documentos_criados
            funcoes.append(funcao)
        return funcoes
