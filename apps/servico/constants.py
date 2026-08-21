"""Constantes e mensagens de erro para o domínio de serviços."""


class ServicoErrorMessages:
    """Mensagens de erros padronizadas para o domínio."""

    INSTABILIDADE = (
        "Não conseguimos cadastrar o serviço. Por favor, tente novamente."
    )
    NOME_OBRIGATORIO = "O nome do serviço é obrigatório."
    NOME_JA_CADASTRADO_TITULO = "Não é possível criar o serviço"
    NOME_JA_CADASTRADO = (
        "Já existe um serviço com este nome cadastrado no sistema."
    )

    ERRO_AO_ATUALIZAR = (
        "Não conseguimos salvar as alterações. Por favor, tente novamente."
    )

    ERRO_AO_EXCLUIR = (
        "Não conseguimos excluir o serviço. Por favor, tente novamente."
    )
