"""Testes para as classes de paginação compartilhadas pela API."""

from typing import Any

import pytest
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from apps.core.pagination import PaginacaoPadrao


def criar_requisicao(
    parametros: dict[str, Any] | None = None,
) -> Request:
    """Cria uma requisição HTTP para os testes de paginação.

    Args:
        parametros: Parâmetros enviados na query string.

    Returns:
        Requisição HTTP compatível com o Django REST Framework.
    """
    factory = APIRequestFactory()
    requisicao = factory.get("/api/teste/", data=parametros)

    return Request(requisicao)


class TestPaginacaoPadrao:
    """Testa o comportamento da paginação padrão da API."""

    def test_deve_retornar_tamanho_padrao_quando_parametro_ausente(
        self,
    ) -> None:
        """Retorna dez registros quando ``page_size`` não é informado."""
        paginacao = PaginacaoPadrao()
        requisicao = criar_requisicao()

        resultado = paginacao.get_page_size(requisicao)

        assert resultado == 10

    def test_deve_retornar_tamanho_informado_na_requisicao(
        self,
    ) -> None:
        """Retorna a quantidade informada no parâmetro ``page_size``."""
        paginacao = PaginacaoPadrao()
        requisicao = criar_requisicao({"page_size": "25"})

        resultado = paginacao.get_page_size(requisicao)

        assert resultado == 25

    def test_deve_desabilitar_paginacao_quando_page_size_for_all(
        self,
    ) -> None:
        """Retorna ``None`` quando ``page_size`` possuir o valor ``all``."""
        paginacao = PaginacaoPadrao()
        requisicao = criar_requisicao({"page_size": "all"})

        resultado = paginacao.get_page_size(requisicao)

        assert resultado is None

    def test_deve_limitar_tamanho_ao_maximo_permitido(
        self,
    ) -> None:
        """Limita a quantidade de registros ao máximo configurado."""
        paginacao = PaginacaoPadrao()
        requisicao = criar_requisicao({"page_size": "150"})

        resultado = paginacao.get_page_size(requisicao)

        assert resultado == 100

    @pytest.mark.parametrize(
        "page_size",
        [
            "",
            "invalido",
            "0",
            "-10",
        ],
    )
    def test_deve_retornar_tamanho_padrao_para_valor_invalido(
        self,
        page_size: str,
    ) -> None:
        """Retorna o tamanho padrão para valores inválidos.

        Args:
            page_size: Valor inválido enviado na query string.
        """
        paginacao = PaginacaoPadrao()
        requisicao = criar_requisicao({"page_size": page_size})

        resultado = paginacao.get_page_size(requisicao)

        assert resultado == 10
