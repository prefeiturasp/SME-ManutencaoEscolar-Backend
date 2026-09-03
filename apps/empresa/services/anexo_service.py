"""Serviços para os anexos de responsáveis técnicos."""

from typing import Any
from uuid import UUID

from django.db import transaction

from apps.empresa.models import AnexoResponsavelTecnico, ResponsavelTecnico
from apps.empresa.repository.anexo_repository import (
    AnexoResponsavelTecnicoRepository,
)
from apps.usuarios.models import Usuario


class AnexoResponsavelTecnicoService:
    """Orquestra o upload e a persistência de anexos de responsáveis."""

    def __init__(
        self,
        repository: AnexoResponsavelTecnicoRepository | None = None,
    ) -> None:
        self.repository = repository or AnexoResponsavelTecnicoRepository()

    @transaction.atomic
    def sincronizar_arquivos(
        self,
        responsavel_uuid: str | UUID,
        arquivos: list[dict[str, Any]],
        usuario: Usuario | None = None,
    ) -> list[dict[str, Any]]:
        """Sincroniza os anexos informados com os anexos do responsável.

        Args:
            responsavel_uuid: UUID do responsável técnico.
            arquivos: Anexos novos ou existentes que devem ser preservados.
            usuario: Usuário responsável pela operação.

        Returns:
            Lista dos novos anexos criados.
        """
        responsavel = ResponsavelTecnico.objects.get(uuid=responsavel_uuid)
        anexos_uuids_preservados = [
            dados["uuid"]
            for dados in arquivos
            if dados.get("uuid") is not None
        ]
        novos_anexos = []

        for dados in arquivos:
            if dados.get("uuid") is None:
                arquivo = dados["arquivo"]
                anexo = AnexoResponsavelTecnico(
                    responsavel_tecnico=responsavel,
                    nome=arquivo.name,
                    criado_por=usuario,
                )
                anexo.arquivo.save(arquivo.name, arquivo, save=False)
                anexo.arquivo_url = anexo.arquivo.url
                novos_anexos.append(anexo)

        anexos_criados = (
            self.repository.bulk_criar(novos_anexos) if novos_anexos else []
        )
        anexos_uuids_preservados.extend(
            anexo["uuid"] for anexo in anexos_criados
        )

        self.repository.excluir_nao_preservados(
            responsavel_id=responsavel.id,
            uuids_preservados=anexos_uuids_preservados,
        )

        return anexos_criados
