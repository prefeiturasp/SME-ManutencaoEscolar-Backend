"""Repositório de documentos de função profissional."""

from collections.abc import Sequence
from functools import partial
from typing import Any
from uuid import UUID

from django.db import transaction

from apps.profissional.models import DocumentoFuncaoProfissional


class DocumentoFuncaoProfissionalRepository:
    """Encapsula o acesso aos documentos das funções."""

    model = DocumentoFuncaoProfissional

    def criar(self, dados: dict[str, Any]) -> dict[str, Any]:
        """
        Cria um documento de função.

        Args:
            dados: Dicionário contendo os dados do documento a ser criado.

        Returns:
            Instância do documento criado.
        """
        documento = self.model(**dados)
        documento.full_clean()
        documento.save()
        return self._serializar(documento)

    @transaction.atomic
    def excluir_nao_preservados(
        self,
        funcao_id: int,
        uuids_preservados: Sequence[str | UUID],
    ) -> None:
        """Exclui os registros e remove os documentos após o commit.

        Args:
            funcao_id: ID da função dona dos documentos.
            uuids_preservados: UUIDs dos documentos que devem permanecer
                ativos.

        """
        documentos_nao_preservados = self.model.objects.filter(
            funcao_profissional_id=funcao_id
        ).exclude(uuid__in=uuids_preservados)

        for documento in documentos_nao_preservados:
            transaction.on_commit(
                partial(documento.arquivo.delete, save=False)
            )

        documentos_nao_preservados.delete()

    def listar_por_funcao(
        self, funcao_id: int
    ) -> list[DocumentoFuncaoProfissional]:
        """Lista os documentos ativos vinculados a uma função.

        Args:
            funcao_id: ID da função profissional.

        Returns:
            Documentos ativos da função.
        """
        return list(
            self.model.objects.filter(funcao_profissional_id=funcao_id)
        )

    @staticmethod
    def _serializar(documento: DocumentoFuncaoProfissional) -> dict[str, Any]:
        """
        Retorna um documento persistido em formato de dicionário.

        Args:
            documento: Instância do modelo `DocumentoFuncaoProfissional`
                a ser serializada.

        Returns:
            Dicionário representando o documento persistido.
        """
        return {
            "id": documento.id,
            "uuid": str(documento.uuid),
            "nome_original": documento.nome_original,
            "arquivo": documento.arquivo,
            "tipo": documento.tipo,
            "tipo_mime": documento.tipo_mime,
            "tamanho_bytes": documento.tamanho_bytes,
            "funcao_profissional": documento.funcao_profissional,
            "criado_por": documento.criado_por,
            "criado_em": documento.criado_em,
            "atualizado_por": documento.atualizado_por,
            "atualizado_em": documento.atualizado_em,
        }
