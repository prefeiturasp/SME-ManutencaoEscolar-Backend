"""Constantes e mensagens de erro para o domínio de empresas."""


class EmpresaErrorMessages:
    """Mensagens de erro padronizadas para o domínio."""

    CNPJ_INVALIDO = "CNPJ inválido."
    CNPJ_JA_CADASTRADO = "Já existe uma empresa cadastrada com este CNPJ."
    CEP_INVALIDO = "CEP inválido. Deve conter 8 dígitos numéricos."
    TELEFONE_INVALIDO = (
        "Telefone inválido. Deve conter 10 ou 11 dígitos numéricos."
    )
    LINK_RASTREIO_INVALIDO = "Link inválido. Deve ser uma URL válida."
    EMPRESA_INATIVA = "Empresa está inativa."
    EMPRESA_NAO_ENCONTRADA = "Empresa não encontrada."
    EMPRESA_INVALIDA = (
        "Empresa inválida. Certifique-se de que a empresa existe."
    )
    RESPONSAVEL_TECNICO_TIPO_JA_CADASTRADO = (
        "Já existe um responsável técnico deste tipo cadastrado "
        "para esta empresa."
    )
    RESPONSAVEL_TECNICO_OBRIGATORIO = (
        "Informe ao menos um responsável técnico."
    )
    RESPONSAVEL_TECNICO_TIPO_DUPLICADO = (
        "Não é permitido informar mais de um responsável técnico "
        "do mesmo tipo."
    )
    RESPONSAVEL_TECNICO_ANEXOS_OBRIGATORIOS = (
        "Anexos são obrigatórios para engenheiros civis e eletricistas."
    )
    RESPONSAVEL_TECNICO_NAO_ENCONTRADO = (
        "Responsável técnico não encontrado para esta empresa."
    )
