"""Constantes e mensagens de erro para o domínio de fornecedores."""


class FornecedorErrorMessages:
    """Mensagens de erro padronizadas para o domínio."""

    CNPJ_INVALIDO = "CNPJ inválido."
    CNPJ_JA_CADASTRADO = "Já existe um fornecedor cadastrado com este CNPJ."
    CEP_INVALIDO = "CEP inválido. Deve conter 8 dígitos numéricos."
    LINK_RASTREIO_INVALIDO = "Link inválido. Deve ser uma URL válida."
    FORNECEDOR_INATIVO = "Fornecedor está inativo."
    FORNECEDOR_NAO_ENCONTRADO = "Fornecedor não encontrado."
