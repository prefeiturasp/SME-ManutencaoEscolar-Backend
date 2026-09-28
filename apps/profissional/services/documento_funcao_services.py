"""Serviços de documentos das funções profissionais."""

from typing import Any

from django.core.exceptions import ValidationError

from apps.core.services.anexo_service import AnexoService
from apps.profissional.constants import ProfissionalErrorMessages
from apps.profissional.repository.documento_funcao_repository import (
    DocumentoFuncaoProfissionalRepository,
)
from apps.usuarios.models import Usuario


class DocumentoFuncaoProfissionalService:
    """Sincroniza documentos vinculados a uma função profissional."""

    def __init__(
        self,
        repository: DocumentoFuncaoProfissionalRepository | None = None,
        anexo_service: AnexoService | None = None,
    ) -> None:
        """
        Inicializa o repositório de documentos das funções profissionais.

        Args:
            repository: Repositório de documentos das funções profissionais
                a ser utilizado. Quando não informado, uma instância padrão de
                `DocumentoFuncaoProfissionalRepository` é criada.
            anexo_service: Serviço de anexos a ser utilizado. Quando
                não informado, uma instância padrão de `AnexoService` é criada.
        """
        self.repository = repository or DocumentoFuncaoProfissionalRepository()
        self.anexo_service = anexo_service or AnexoService()

    def sincronizar(
        self,
        funcao_id: int,
        documentos_lista: list[dict[str, Any]],
        usuario: Usuario | None = None,
    ) -> list[dict[str, Any]]:
        """
        Sincroniza os documentos informados com os documentos da função.

        Args:
            funcao_id: ID da função à qual os documentos pertencem.
            documentos_lista: Lista contendo os dados dos documentos.
            usuario: Usuário que está realizando a operação.

        returns:
            Lista dos novos documentos criados.

        Raises:
            ValidationError: Se um UUID informado não pertencer à função.
        """
        existentes = self.repository.listar_por_funcao(funcao_id)
        existentes_uuids = {str(documento.uuid) for documento in existentes}
        documentos_uuids_preservados = [
            str(dados["uuid"])
            for dados in documentos_lista
            if dados.get("uuid") is not None
        ]

        if set(documentos_uuids_preservados) - existentes_uuids:
            raise ValidationError(
                {
                    "documentos": (
                        ProfissionalErrorMessages.DOCUMENTO_FUNCAO_NAO_ENCONTRADO
                    )
                }
            )

        documentos_criados = []
        for documento in documentos_lista:
            if documento.get("uuid") is None:
                arquivo = documento["arquivo"]
                dados = self.anexo_service.validar_e_preparar_anexo(
                    arquivo=arquivo,
                    id_usuario=usuario.id if usuario is not None else None,
                )
                dados.pop("usuario_id", None)

                documento = self.repository.criar(
                    {
                        **dados,
                        "funcao_profissional_id": funcao_id,
                        "criado_por": usuario,
                    }
                )
                documentos_criados.append(documento)

        documentos_uuids_preservados.extend(
            anexo["uuid"] for anexo in documentos_criados
        )

        self.repository.excluir_nao_preservados(
            funcao_id=funcao_id,
            uuids_preservados=documentos_uuids_preservados,
        )
        return documentos_criados
