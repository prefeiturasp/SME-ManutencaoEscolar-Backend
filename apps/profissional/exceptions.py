"""Exceções do domínio Profissional."""

from rest_framework import status
from rest_framework.exceptions import APIException


class ProfissionalJaCadastradoError(APIException):
    """Indica que o CPF e/ou o RG já pertencem a outro profissional.

    A resposta da API (HTTP 400) informa, para cada documento, se ele está
    duplicado: ``{"cpf": true, "rg": false}``. A mensagem exibida ao usuário
    fica a cargo do frontend.
    """

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "CPF e/ou RG já cadastrados para outro profissional."
    default_code = "profissional_ja_cadastrado"

    def __init__(self, duplicidade: dict[str, bool]) -> None:
        """Armazena quais documentos estão duplicados.

        Args:
            duplicidade: Dicionário com as chaves ``cpf`` e ``rg``, indicando
                se cada documento já pertence a outro profissional.
        """
        super().__init__()
        self.duplicidade = duplicidade
        # O construtor de APIException converteria os booleanos em texto;
        # por isso o detalhe é atribuído depois, preservando os valores.
        self.detail = duplicidade  # type: ignore[assignment]
