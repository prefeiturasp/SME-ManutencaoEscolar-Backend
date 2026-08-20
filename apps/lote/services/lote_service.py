"""Serviços relacionados ao cadastro de lotes."""

from typing import Any, cast

from apps.escola.models import DiretoriaRegional
from apps.lote.constants import LoteErrorMessages
from apps.lote.exceptions import DiretoriaRegionalJaVinculadaError
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
    ) -> dict[str, Any]:
        """Valida e cria um lote com suas DREs."""
        dados_normalizados = dados.copy()

        nome = dados_normalizados["nome"].strip()
        codigo_cadastro = dados_normalizados["codigo_cadastro"].strip()
        diretorias_regionais = cast(
            list[DiretoriaRegional],
            dados_normalizados.get("diretorias_regionais", []),
        )

        diretorias_regionais_vinculadas = (
            self.repository._obter_diretorias_regionais_vinculadas(
                diretorias_regionais,
            )
        )

        if diretorias_regionais_vinculadas:
            raise DiretoriaRegionalJaVinculadaError(
                title=LoteErrorMessages.DIRETORIA_REGIONAL_VINCULADA_TITULO,
                detail={
                    "message": LoteErrorMessages.DIRETORIA_REGIONAL_VINCULADA,
                    "vinculados": diretorias_regionais_vinculadas,
                },
            )
        dados_normalizados["nome"] = nome
        dados_normalizados["codigo_cadastro"] = codigo_cadastro

        return self.repository.criar(
            dados_normalizados,
            usuario=usuario,
        )
