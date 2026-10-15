"""Constantes do domínio Profissional."""


class ProfissionalErrorMessages:
    """Mensagens de erro padronizadas para o domínio Profissional."""

    PROFISSIONAL_INATIVO = "Profissional está inativo."
    PROFISSIONAL_NAO_ENCONTRADO = "Profissional não encontrado."
    PROFISSIONAL_INVALIDO = (
        "Profissional inválido. Certifique-se de que o profissional existe."
    )
    PROFISSIONAL_DUPLICADO_TITULO_CRIAR = (
        "Não é possível cadastrar o profissional"
    )
    PROFISSIONAL_DUPLICADO_TITULO_EDITAR = (
        "Não é possível editar o profissional"
    )
    PROFISSIONAL_CPF_JA_CADASTRADO = (
        "Já existe um profissional cadastrado com este CPF. "
        "Verifique os dados informados ou consulte o cadastro existente "
        "antes de continuar."
    )
    PROFISSIONAL_RG_JA_CADASTRADO = (
        "Já existe um profissional cadastrado com este RG. "
        "Verifique os dados informados ou consulte o cadastro existente "
        "antes de continuar."
    )
    PROFISSIONAL_CPF_E_RG_JA_CADASTRADOS = (
        "Já existe um profissional cadastrado com o CPF e o RG informados. "
        "Verifique os dados ou consulte o cadastro existente antes de "
        "continuar."
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
