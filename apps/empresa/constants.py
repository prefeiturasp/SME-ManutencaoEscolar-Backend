"""Constantes e mensagens de erro para o domínio de empresas."""


class EmpresaErrorMessages:
    """Mensagens de erro padronizadas para o domínio."""

    CNPJ_INVALIDO = "CNPJ inválido."
    CNPJ_JA_CADASTRADO = "Já existe uma empresa cadastrada com este CNPJ."
    CEP_INVALIDO = "CEP inválido. Deve conter 8 dígitos numéricos."
    LINK_RASTREIO_INVALIDO = "Link inválido. Deve ser uma URL válida."
    EMPRESA_INATIVO = "Empresa está inativa."
    EMPRESA_NAO_ENCONTRADO = "Empresa não encontrada."
