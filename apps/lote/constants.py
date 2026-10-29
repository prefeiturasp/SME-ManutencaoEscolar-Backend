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

    LOTE_VINCULADO_EQUIPE_TITULO = "Não é possível excluir o lote"
    LOTE_VINCULADO_EQUIPE = (
        "Este lote está vinculado as equipes listadas e, por isso, não pode "
        "ser excluído. Remova os vínculos para prosseguir com a exclusão."
    )
    ALTERACAO_EMPRESA_LOTE_VINCULADO_TITULO = (
        "Não é possível realizar a alteração"
    )
    ALTERACAO_EMPRESA_LOTE_VINCULADO = (
        "Este lote está vinculado a uma ou mais equipes. Para alterar "
        "a empresa, remova os vínculos com as equipes listadas."
    )

    INSTABILIDADE = (
        "Não conseguimos cadastrar o lote. Por favor, tente novamente."
    )
