"""Repositório para os anexos de responsáveis técnicos."""

from typing import Any
from uuid import UUID

from django.utils import timezone

from apps.empresa.models import AnexoResponsavelTecnico
from apps.usuarios.models import Usuario


class AnexoResponsavelTecnicoRepository:
    """Centraliza a persistência de anexos de responsáveis técnicos."""

    model = AnexoResponsavelTecnico

    def bulk_criar(
        self, anexos: list[AnexoResponsavelTecnico]
    ) -> list[dict[str, Any]]:
        """
        Persista os metadados de arquivos já enviados ao storage.

        Args:
            anexos: Instâncias de ``AnexoResponsavelTecnico`` a persistir.

        Returns:
            Os dados dos anexos persistidos em formato de dicionário.

        """
        criados = self.model.objects.bulk_create(anexos)
        return [self._serializar(anexo) for anexo in criados]

    def excluir_nao_preservados(
        self,
        responsavel_id: int,
        uuids_preservados: list[str | UUID],
        usuario: Usuario | None = None,
    ) -> int:
        """Exclui logicamente os anexos que não foram preservados.

        Args:
            responsavel_id: ID do responsável técnico dono dos anexos.
            uuids_preservados: UUIDs dos anexos que devem permanecer ativos.
            usuario: Usuário responsável pela exclusão.

        Returns:
            Quantidade de anexos marcados como deletados.

        """
        return (
            self.model.objects.filter(responsavel_tecnico_id=responsavel_id)
            .exclude(uuid__in=uuids_preservados)
            .update(deletado_em=timezone.now(), deletado_por=usuario)
        )

    @staticmethod
    def _serializar(anexo: AnexoResponsavelTecnico) -> dict[str, Any]:
        """Serializa um anexo em formato de dicionário."""
        return {
            "uuid": str(anexo.uuid),
            "nome": anexo.nome,
            "arquivo_url": anexo.arquivo_url,
        }
