"""Constantes e mensagens de erro para o domínio de cargos."""


class CargoErrorMessages:
    """Mensagens de erros padronizadas para o domínio."""

    INSTABILIDADE = (
        "Não conseguimos cadastrar o cargo. Por favor, tente novamente."
    )
    NOME_OBRIGATORIO = "O nome do cargo é obrigatório."
    NOME_JA_CADASTRADO_TITULO = "Não é possível criar o cargo"
    NOME_JA_CADASTRADO = (
        "Já existe um cargo com este nome cadastrado no sistema."
    )

    ERRO_AO_ATUALIZAR = (
        "Não conseguimos salvar as alterações. Por favor, tente novamente."
    )

    ERRO_AO_EXCLUIR = (
        "Não conseguimos excluir o cargo. Por favor, tente novamente."
    )
