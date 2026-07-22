"""Testes para funções e validadores em apps.utils.validacoes."""

import pytest
from django.core.exceptions import ValidationError

from apps.utils.validacoes import (
    CepInvalidoError,
    CnpjInvalidoError,
    LinkRastreioInvalidoError,
    apenas_digitos_validator,
    cnpj_formato_validacao,
    formata_cnpj,
    link_formato_validacao,
    validar_formato_cep,
    validar_formato_cnpj,
    validar_formato_link_rastreio,
)


class TestFormataCnpj:
    """Testa a função formata_cnpj."""

    def test_deve_remover_pontos_barra_hifen_e_espacos(self) -> None:
        """Valida remoção de máscara comum em CNPJs."""
        resultado = formata_cnpj("12.345.678/0001-95")

        assert resultado == "12345678000195"

    def test_deve_converter_letras_para_maiusculas(self) -> None:
        """Valida conversão para uppercase."""
        resultado = formata_cnpj("12.abc.345/01de-35")

        assert resultado == "12ABC34501DE35"

    def test_deve_remover_todos_os_caracteres_especiais(self) -> None:
        """Valida remoção de todos os caracteres especiais."""
        resultado = formata_cnpj("12-abc.345/01 de-35")

        assert resultado == "12ABC34501DE35"

    def test_deve_retornar_string_vazia_para_valor_vazio(self) -> None:
        """Valida retorno vazio quando input é vazio."""
        resultado = formata_cnpj("")

        assert resultado == ""

    def test_deve_retornar_string_vazia_para_none(self) -> None:
        """Valida retorno vazio quando input é None."""
        resultado = formata_cnpj(None)

        assert resultado == ""


class TestValidarFormatoCnpj:
    """Testa a função validar_formato_cnpj."""

    def test_deve_aceitar_cnpj_com_formato_valido(self) -> None:
        """Valida aceitação de CNPJ com formato correto."""
        # Não deve lançar exceção
        validar_formato_cnpj("12ABC34501DE35")

    def test_deve_aceitar_cnpj_totalmente_numerico(self) -> None:
        """Valida aceitação de CNPJ totalmente numérico."""
        validar_formato_cnpj("12345678000195")

    @pytest.mark.parametrize(
        "cnpj_invalido",
        [
            "",
            "123",
            "12ABC345",
            "12ABC34501DE3599",
            "12ABC34501DE3X",
            "12ABC345-01DE35",
            "12 ABC 345 01 DE 35",
            "12abc34501de35",
            "12.ABC.345/01DE-35",
        ],
    )
    def test_deve_rejeitar_cnpj_com_formato_invalido_parametrizado(
        self, cnpj_invalido: str
    ) -> None:
        """Valida rejeição de vários formatos inválidos."""
        with pytest.raises(CnpjInvalidoError):
            validar_formato_cnpj(cnpj_invalido)


class TestValidarFormatoCep:
    """Testa a função validar_formato_cep."""

    def test_deve_aceitar_cep_com_formato_valido(self) -> None:
        """Valida aceitação de CEP com 8 dígitos."""
        # Não deve lançar exceção
        validar_formato_cep("12345678")

    @pytest.mark.parametrize(
        "cep_invalido",
        [
            "",  # Vazio
            "1234567",  # Menos de 8 dígitos
            "1234567A",  # Com letras
            "123456789",  # Com mais de 8 dígitos
            "12345-678",  # Com máscara
            "12 345 678",  # Com espaços
        ],
    )
    def test_deve_rejeitar_cep_invalido_parametrizado(
        self, cep_invalido: str
    ) -> None:
        """Valida rejeição de vários formatos inválidos."""
        with pytest.raises(CepInvalidoError):
            validar_formato_cep(cep_invalido)


class TestValidarFormatoLinkRastreio:
    """Testa a função validar_formato_link_rastreio."""

    def test_deve_aceitar_link_http(self) -> None:
        """Valida aceitação de link HTTP."""
        validar_formato_link_rastreio(
            "http://rastreamento.exemplo.com.br"  # NOSONAR - HTTP
        )

    def test_deve_aceitar_link_https(self) -> None:
        """Valida aceitação de link HTTPS."""
        validar_formato_link_rastreio("https://rastreamento.exemplo.com.br")

    def test_deve_aceitar_link_com_parametros(self) -> None:
        """Valida aceitação de link com parâmetros."""
        validar_formato_link_rastreio("https://rastreamento.com/track?id=123")

    @pytest.mark.parametrize(
        "link_invalido",
        [
            "",  # Vazio
            "www.exemplo.com.br",  # Sem protocolo
            "ftp://exemplo.com.br",  # NOSONAR - HTTP
            "https://exemplo link.com.br",  # Com espaço
        ],
    )
    def test_deve_rejeitar_link_invalido_parametrizado(
        self, link_invalido: str
    ) -> None:
        """Valida rejeição de formatos inválidos."""
        with pytest.raises(LinkRastreioInvalidoError):
            validar_formato_link_rastreio(link_invalido)


class TestCnpjFormatoValidacao:
    """Testa o validator cnpj_formato_validacao."""

    def test_deve_aceitar_cnpj_valido(self) -> None:
        """Valida aceitação do validator para CNPJ válido."""
        # Não deve lançar exceção
        cnpj_formato_validacao("12ABC34501DE35")

    def test_deve_rejeitar_cnpj_invalido(self) -> None:
        """Valida rejeição do validator para CNPJ inválido."""
        with pytest.raises(ValidationError):
            cnpj_formato_validacao("12ABC345")


class TestLinkFormatoValidacao:
    """Testa o validator link_formato_validacao."""

    def test_deve_aceitar_link_valido(self) -> None:
        """Valida aceitação do validator para link válido."""
        link_formato_validacao("https://exemplo.com.br")

    def test_deve_rejeitar_link_invalido(self) -> None:
        """Valida rejeição do validator para link inválido."""
        with pytest.raises(ValidationError):
            link_formato_validacao("exemplo.com.br")


class TestApenasDigitosValidator:
    """Testa o validator apenas_digitos_validator."""

    def test_deve_aceitar_apenas_digitos(self) -> None:
        """Valida aceitação de apenas dígitos."""
        apenas_digitos_validator("12345")

    def test_deve_rejeitar_com_letras(self) -> None:
        """Valida rejeição quando há letras."""
        with pytest.raises(ValidationError):
            apenas_digitos_validator("123A5")

    def test_deve_rejeitar_com_caracteres_especiais(self) -> None:
        """Valida rejeição quando há caracteres especiais."""
        with pytest.raises(ValidationError):
            apenas_digitos_validator("123-45")
