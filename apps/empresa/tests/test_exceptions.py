"""Testes das exceções da aplicação Serviço."""

from apps.servico.exceptions import ServicoJaCadastradoError


class TestServicoJaCadastradoError:
    """Testes para ServicoJaCadastradoError."""

    def test_deve_inicializar_com_titulo_e_detalhe(self):
        """Deve armazenar o título e o detalhe informados."""
        erro = ServicoJaCadastradoError(
            title="Serviço já cadastrado",
            detail="Já existe um serviço com esse nome.",
        )

        assert erro.title == "Serviço já cadastrado"
        assert erro.detail == "Já existe um serviço com esse nome."
        assert str(erro) == "Já existe um serviço com esse nome."
