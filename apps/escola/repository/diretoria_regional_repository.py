"""Repository de diretorias regionais."""

from typing import Any

from apps.escola.models.diretoria_regional import DiretoriaRegional


class DiretoriaRegionalRepository:
    """Gerencia operações de leitura de diretorias regionais."""

    @staticmethod
    def serializar(
        diretoria: DiretoriaRegional | None,
    ) -> dict[str, Any] | None:
        """Serializa uma diretoria regional em um dicionário.

        Args:
            diretoria: Diretoria regional a serializar.

        Returns:
            Dados da diretoria ou ``None`` quando não houver diretoria.
        """
        if diretoria is None:
            return None
        return {
            "id": diretoria.id,
            "codigo": diretoria.codigo,
            "nome": diretoria.nome,
            "abreviacao": diretoria.abreviacao,
            "nome_curto": diretoria.nome_curto,
        }
