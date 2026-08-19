"""Serviços relacionados ao cadastro de lotes."""

from typing import Any, NoReturn, cast
from typing import NoReturn

from apps.escola.models import DiretoriaRegional
from apps.lote.constants import LoteErrorMessages
from apps.lote.exceptions import (
    DREJaVinculadaError
)
from apps.lote.models import Lote
from apps.lote.repository.lote_repository import LoteRepository
from apps.usuarios.models.usuario import Usuario


class LoteService:
    """Orquestra as regras de negócio relacionadas aos lotes."""

    def __init__(
        self,
        repository: LoteRepository | None = None,
    ) -> None:
        """Inicializa o serviço com o repositório informado ou o padrão."""
        self.repository = repository or LoteRepository()

    def criar(
        self,
        dados: dict[str, Any],
        usuario: Usuario,
    ) -> Lote:
        """Valida e cria um lote com suas DREs."""
        dados_normalizados = dados.copy()

        nome = dados_normalizados["nome"].strip()
        codigo_cadastro = dados_normalizados[
            "codigo_cadastro"
        ].strip()
        dres = cast(
            list[DiretoriaRegional],
            dados_normalizados.get("dres", []),
        )

        dres_vinculadas = self.repository._obter_dres_vinculadas(
            dres,
        )

        if dres_vinculadas:
            raise DREJaVinculadaError(
                title=LoteErrorMessages.DRE_JA_VINCULADA_TITULO,
                detail={
                    "mesage": LoteErrorMessages.DRE_JA_VINCULADA,
                    "vinculados": dres_vinculadas
                    }
            )
        dados_normalizados["nome"] = nome
        dados_normalizados["codigo_cadastro"] = codigo_cadastro

        return self.repository.criar(
            dados_normalizados,
            usuario=usuario,
        )
