"""Constantes do domínio Profissional."""


class ProfissionalErrorMessages:
    """Mensagens de erro padronizadas para o domínio Profissional."""

    PROFISSIONAL_INATIVO = "Profissional está inativo."
    PROFISSIONAL_NAO_ENCONTRADO = "Profissional não encontrado."
    PROFISSIONAL_INVALIDO = (
        "Profissional inválido. Certifique-se de que o profissional existe."
    )
    PROFISSIONAL_CPF_JA_CADASTRADO = (
        "Já existe um profissional cadastrado com este CPF."
    )
    PROFISSIONAL_RG_JA_CADASTRADO = (
        "Já existe um profissional cadastrado com este RG."
    )
    FUNCAO_PROFISSIONAL_JA_CADASTRADA = (
        "Esta função já está cadastrada neste profissional."
    )
    FUNCAO_PROFISSIONAL_OBRIGATORIA = (
        "Informe ao menos uma função profissional."
    )
    FUNCAO_PROFISSIONAL_DUPLICADA = (
        "Não é permitido informar uma função profissional "
        "mais de uma vez para o mesmo profissional."
    )
    FUNCAO_PROFISSIONAL_NAO_ENCONTRADA = "Função profissional não encontrada."
    DOCUMENTOS_FUNCAO_PROFISSIONAL_OBRIGATORIOS = (
        "Documentos são obrigatórios para esta função profissional."
    )
    DOCUMENTO_FUNCAO_NAO_ENCONTRADO = (
        "Documento da função profissional não encontrado."
    )
