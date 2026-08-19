"""Constantes relacionadas ao cadastro de lotes."""


class LoteErrorMessages:
    """Armazena as mensagens de erro relacionadas aos lotes."""

    DRE_JA_VINCULADA_TITULO = (
        "Uma ou mais DREs já estão associadas a um lote"
    )
    DRE_JA_VINCULADA = (
        "Revise abaixo as DREs indisponíveis para vínculo e os "
        "respectivos lotes aos quais elas pertencem."
    )

    INSTABILIDADE = (
        "Não conseguimos cadastrar o lote. Por favor, tente novamente."
    )
