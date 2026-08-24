"""Exceptions do app escola."""


class DadosEscolaError(Exception):
    """Representa um problema recuperável nos dados de uma escola.

    A exceção indica que os dados necessários para importar uma escola
    específica não estão disponíveis ou são inválidos. Nesse caso, a
    escola pode ser ignorada sem interromper a importação das demais.
    """

    pass


class DadosDiretorError(Exception):
    """Representa um problema recuperável nos dados de uma escola.

    A exceção indica que os dados necessários para importar uma escola
    específica não estão disponíveis ou são inválidos. Nesse caso, a
    escola pode ser ignorada sem interromper a importação das demais.
    """

    pass
