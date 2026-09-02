"""Serviços para os anexos de responsáveis técnicos."""

from typing import Any

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
    def salvar_arquivos(
        self,
        responsavel_id: int,
        arquivos: list[dict[str, Any]],
        usuario: Usuario | None = None,
    ) -> list[dict[str, Any]]:
        """Sincroniza os anexos informados com os anexos do responsável."""
        responsavel = ResponsavelTecnico.objects.get(pk=responsavel_id)
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
            responsavel_id=responsavel_id,
            uuids_preservados=anexos_uuids_preservados,
            usuario=usuario,
        )

        return anexos_criados
