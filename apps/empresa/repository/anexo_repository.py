"""Repositório para os anexos de responsáveis técnicos."""

from typing import Any
from uuid import UUID

from apps.empresa.models import AnexoResponsavelTecnico


class AnexoResponsavelTecnicoRepository:
    """Centraliza a persistência de anexos de responsáveis técnicos."""

    model = AnexoResponsavelTecnico

    def criar(self, anexo: AnexoResponsavelTecnico) -> dict[str, Any]:
        """Persistir e serializar um anexo.

        Args:
            anexo: Anexo que será persistido.

        Returns:
            Dados serializados do anexo criado.
        """
        anexo.save()
        return self._serializar(anexo)

    def excluir_nao_preservados(
        self,
        responsavel_id: int,
        uuids_preservados: list[str | UUID],
    ) -> None:
        """Exclui fisicamente os anexos que não foram preservados.

        Args:
            responsavel_id: ID do responsável técnico dono dos anexos.
            uuids_preservados: UUIDs dos anexos que devem permanecer ativos.

        """
        anexos_nao_preservados = self.model.objects.filter(
            responsavel_tecnico_id=responsavel_id
        ).exclude(uuid__in=uuids_preservados)

        for anexo in anexos_nao_preservados:
            anexo.arquivo.delete(save=False)

        anexos_nao_preservados.delete()

    @staticmethod
    def _serializar(anexo: AnexoResponsavelTecnico) -> dict[str, Any]:
        """
        Serializa um anexo em formato de dicionário.

        Args:
            anexo: Anexo a ser serializado.

        Returns:
            dict: Dicionário contendo os seguintes dados:
            - ``uuid``: UUID do anexo.
            - ``nome``: Nome original do arquivo.
            - ``arquivo_url``: URL de acesso ao arquivo.
        """
        return {
            "uuid": str(anexo.uuid),
            "nome": anexo.nome_original,
            "arquivo_url": anexo.url,
        }
