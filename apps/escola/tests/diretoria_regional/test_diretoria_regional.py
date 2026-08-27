"""Testes para o modelo de Diretoria Regional."""

from apps.escola.models import DiretoriaRegional


class TestDiretoriaRegional:
    """Testa os comportamentos do modelo DiretoriaRegional."""

    def test_deve_retornar_representacao_textual(self) -> None:
        """Retorna a abreviação e o nome como representação textual."""
        diretoria_regional = DiretoriaRegional(
            codigo="108500",
            nome="DIRETORIA REGIONAL DE EDUCACAO BUTANTA",
            abreviacao="BT",
        )

        resultado = str(diretoria_regional)

        assert resultado == ("BT - DIRETORIA REGIONAL DE EDUCACAO BUTANTA")

    def test_deve_retornar_nome_curto_da_diretoria(self) -> None:
        """Substitui o prefixo do nome da diretoria pela sigla DRE."""
        diretoria_regional = DiretoriaRegional(
            codigo="108500",
            nome="DIRETORIA REGIONAL DE EDUCACAO BUTANTA",
            abreviacao="BT",
        )

        resultado = diretoria_regional.nome_curto

        assert resultado == "DRE BUTANTA"

    def test_deve_manter_nome_quando_prefixo_nao_estiver_presente(
        self,
    ) -> None:
        """Mantém o nome quando ele não possuir o prefixo esperado."""
        diretoria_regional = DiretoriaRegional(
            codigo="108500",
            nome="DIRETORIA BUTANTA",
            abreviacao="BT",
        )

        resultado = diretoria_regional.nome_curto

        assert resultado == "DIRETORIA BUTANTA"

    def test_deve_retornar_nome_vazio_quando_nome_estiver_vazio(
        self,
    ) -> None:
        """Retorna uma string vazia quando o nome estiver vazio."""
        diretoria_regional = DiretoriaRegional(
            codigo="108500",
            nome="",
            abreviacao="BT",
        )

        resultado = diretoria_regional.nome_curto

        assert resultado == ""
