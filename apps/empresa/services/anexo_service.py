"""Serviços para os anexos de responsáveis técnicos."""

from typing import Any
from uuid import UUID

from django.db import transaction

from apps.core.services.anexo_service import AnexoService
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
        anexo_service: AnexoService | None = None,
    ) -> None:
        self.repository = repository or AnexoResponsavelTecnicoRepository()
        self.anexo_service = anexo_service or AnexoService()

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
        anexos_criados = []

        for dados in arquivos:
            if dados.get("uuid") is None:
                arquivo = dados["arquivo"]
                dados_anexo = self.anexo_service.validar_e_preparar_anexo(
                    arquivo=arquivo,
                    id_usuario=usuario.id if usuario is not None else None,
                )
                anexo = AnexoResponsavelTecnico(
                    responsavel_tecnico=responsavel,
                    nome_original=dados_anexo["nome_original"],
                    tipo=dados_anexo["tipo"],
                    tipo_mime=dados_anexo["tipo_mime"],
                    tamanho_bytes=dados_anexo["tamanho_bytes"],
                    arquivo=dados_anexo["arquivo"],
                    criado_por=usuario,
                )
                anexos_criados.append(self.repository.criar(anexo))

        anexos_uuids_preservados.extend(
            anexo["uuid"] for anexo in anexos_criados
        )

        self.repository.excluir_nao_preservados(
            responsavel_id=responsavel.id,
            uuids_preservados=anexos_uuids_preservados,
        )

        return anexos_criados
