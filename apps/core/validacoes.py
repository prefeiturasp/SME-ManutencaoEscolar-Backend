"""Utilitários de validação/normalização de campos."""

import re

from django.core.validators import RegexValidator

from apps.core.exceptions import (
    CepInvalidoError,
    CnpjInvalidoError,
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


def formata_cnpj(valor: str) -> str:
    """
    Remove máscara (pontos, barra, hífen, espaços) e uppercase nas letras.

    Não valida aqui — apenas formata a representação para uma forma
    canônica de armazenamento/comparação.
    """
    if not valor:
        return ""
    return re.sub(r"[.\-/\s]", "", valor).upper()


def validar_formato_cnpj(cnpj: str) -> None:
    """Valida apenas o formato (14 posições, 12 alfanuméricas + 2 dígitos)."""
    if not CNPJ_FORMATO_REGEX.match(cnpj or ""):
        raise CnpjInvalidoError(
            "CNPJ deve ter 14 posições: as 12 primeiras alfanuméricas "
            "(0-9, A-Z) e as 2 últimas numéricas."
        )


def validar_formato_cep(cep: str) -> None:
    """Valida apenas o formato (8 dígitos numéricos)."""
    if not re.match(r"^\d{8}$", cep or ""):
        raise CepInvalidoError(
            "CEP inválido. Deve conter 8 dígitos numéricos."
        )


def validar_formato_link_rastreio(link: str) -> None:
    """Valida apenas o formato do link de rastreio (URL)."""
    if not LINK_FORMATO_REGEX.match(link or ""):
        raise LinkRastreioInvalidoError(
            "Link inválido. Deve ser uma URL válida."
        )


def validar_telefone(telefone: str) -> None:
    """Valida apenas o número de caracteres (10 ou 11 dígitos numéricos)."""
    if not re.match(r"^\d{10,11}$", telefone or ""):
        raise TelefoneInvalidoError(
            "Telefone inválido. Deve conter 10 ou 11 dígitos numéricos."
        )
