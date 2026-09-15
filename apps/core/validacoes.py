"""Utilitários para validação e normalização de campos.

Centraliza expressões regulares, validadores do Django e funções utilizadas
para validar formatos de CNPJ, CEP, links de rastreamento, telefones e
endereços de e-mail.
"""

import re

from django.core.validators import RegexValidator

from apps.core.exceptions import (
    CepInvalidoError,
    CnpjInvalidoError,
    EmailInvalidoError,
    LinkRastreioInvalidoError,
    TelefoneInvalidoError,
)

CNPJ_FORMATO_REGEX = re.compile(r"^[A-Z0-9]{12}\d{2}$")

cnpj_formato_validacao = RegexValidator(
    regex=CNPJ_FORMATO_REGEX,
    message=(
        "CNPJ inválido: deve ter 14 posições, sendo as 12 primeiras "
        "alfanuméricas (0-9, A-Z) e as 2 últimas numéricas."
    ),
)

LINK_FORMATO_REGEX = re.compile(r"^https?://[^\s]+$")

link_formato_validacao = RegexValidator(
    regex=LINK_FORMATO_REGEX,
    message="Link inválido: deve ser uma URL válida.",
)

apenas_digitos_validator = RegexValidator(
    regex=r"^\d+$",
    message="Este campo deve conter apenas dígitos numéricos.",
)

EMAIL_FORMATO_REGEX = re.compile(
    r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
)


def formata_cnpj(valor: str) -> str:
    """Normaliza a representação de um CNPJ.

    Remove pontos, barras, hífens e espaços e converte as letras para
    maiúsculas. A função não verifica se o valor possui um formato de CNPJ
    válido.

    Args:
        valor (str): CNPJ que será normalizado.

    Returns:
        str: CNPJ sem máscara e com caracteres alfabéticos em maiúsculas.
            Retorna uma string vazia quando ``valor`` for vazio.
    """
    if not valor:
        return ""
    return re.sub(r"[.\-/\s]", "", valor).upper()


def validar_formato_cnpj(cnpj: str) -> None:
    """Valida o formato estrutural de um CNPJ.

    Verifica se o valor possui 14 posições, sendo as 12 primeiras
    alfanuméricas e as duas últimas exclusivamente numéricas.

    Args:
        cnpj (str): CNPJ que será validado.

    Raises:
        CnpjInvalidoError: Se o CNPJ não atender ao formato esperado.
    """
    if not CNPJ_FORMATO_REGEX.match(cnpj or ""):
        raise CnpjInvalidoError(
            "CNPJ deve ter 14 posições: as 12 primeiras alfanuméricas "
            "(0-9, A-Z) e as 2 últimas numéricas."
        )


def validar_formato_cep(cep: str) -> None:
    """Valida o formato estrutural de um CEP.

    O valor deve conter exatamente oito dígitos numéricos.

    Args:
        cep (str): CEP que será validado.

    Raises:
        CepInvalidoError: Se o CEP não possuir exatamente oito dígitos
            numéricos.
    """
    if not re.match(r"^\d{8}$", cep or ""):
        raise CepInvalidoError(
            "CEP inválido. Deve conter 8 dígitos numéricos."
        )


def validar_formato_link_rastreio(link: str) -> None:
    """Valida o formato de um link de rastreamento.

    Verifica se o valor inicia com ``http://`` ou ``https://`` e não
    contém espaços em branco.

    Args:
        link (str): URL de rastreamento que será validada.

    Raises:
        LinkRastreioInvalidoError: Se o link não atender ao formato esperado.
    """
    if not LINK_FORMATO_REGEX.match(link or ""):
        raise LinkRastreioInvalidoError(
            "Link inválido. Deve ser uma URL válida."
        )


def validar_telefone(telefone: str) -> None:
    """Valida o formato de um número de telefone.

    O valor deve conter exclusivamente dígitos e possuir 10 ou 11 posições.

    Args:
        telefone (str): Número de telefone que será validado.

    Raises:
        TelefoneInvalidoError: Se o telefone não possuir 10 ou 11 dígitos
            numéricos.
    """
    if not re.match(r"^\d{10,11}$", telefone or ""):
        raise TelefoneInvalidoError(
            "Telefone inválido. Deve conter 10 ou 11 dígitos numéricos."
        )


def validar_email(email: str) -> None:
    """Valida o formato básico de um endereço de e-mail.

    A validação verifica se o valor corresponde ao padrão de e-mail definido
    pela expressão regular da aplicação. Não realiza validação da existência
    ou acessibilidade do endereço.

    Args:
        email (str): Endereço de e-mail que será validado.

    Raises:
        EmailInvalidoError: Se o endereço não atender ao formato esperado.
    """
    if not EMAIL_FORMATO_REGEX.match(email or ""):
        raise EmailInvalidoError(
            "E-mail inválido. Deve possuir um endereço de e-mail válido."
        )
