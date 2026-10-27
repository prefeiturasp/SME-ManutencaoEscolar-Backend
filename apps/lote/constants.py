"""Constantes relacionadas ao cadastro de lotes."""


class LoteErrorMessages:
    """Armazena as mensagens de erro relacionadas aos lotes."""

    DIRETORIA_REGIONAL_VINCULADA_TITULO = (
        "Uma ou mais DREs já estão associadas a um lote"
    )
    DIRETORIA_REGIONAL_VINCULADA = (
        "Revise abaixo as DREs indisponíveis para vínculo e os "
        "respectivos lotes aos quais elas pertencem."
    )

    LOTE_VINCULADO_EQUIPE_TITULO = "Excluir Lote"
    LOTE_VINCULADO_EQUIPE = (
        "Não é possível excluir este registro. O Lote {codigo_lote} - "
        "{nome_lote} está vinculado as equipes a baixo. Remova o vinculo do "
        "lote com as equipes caso queira prosseguir com a exclusão."
    )

    INSTABILIDADE = (
        "Não conseguimos cadastrar o lote. Por favor, tente novamente."
    )
