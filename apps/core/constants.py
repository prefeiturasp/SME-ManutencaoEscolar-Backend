"""Constantes utilizadas pela aplicação Core."""

from django.db import models

ENDPOINT_AUTENTICACAO = "/v1/autenticacao"
ENDPOINT_USUARIO_EXISTE_CORESSO = "/AutenticacaoSgp/UsuarioExisteCoreSSO"
ENDPOINT_ALTERAR_SENHA_CORESSO = "/AutenticacaoSgp/AlterarSenha"

EXTENSOES_IMAGENS = [".jpg", ".jpeg", ".png"]
EXTENSOES_DOCUMENTOS = [
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".csv",
    ".txt",
]

EXTENSOES_COMPACTADOS = [
    ".zip",
    ".rar",
]
TAMANHO_MAXIMO_ARQUIVO = 2 * 1024 * 1024


class EstadoChoices(models.TextChoices):
    """UFs do Brasil."""

    AC = "AC", "Acre"
    AL = "AL", "Alagoas"
    AP = "AP", "Amapá"
    AM = "AM", "Amazonas"
    BA = "BA", "Bahia"
    CE = "CE", "Ceará"
    DF = "DF", "Distrito Federal"
    ES = "ES", "Espírito Santo"
    GO = "GO", "Goiás"
    MA = "MA", "Maranhão"
    MT = "MT", "Mato Grosso"
    MS = "MS", "Mato Grosso do Sul"
    MG = "MG", "Minas Gerais"
    PA = "PA", "Pará"
    PB = "PB", "Paraíba"
    PR = "PR", "Paraná"
    PE = "PE", "Pernambuco"
    PI = "PI", "Piauí"
    RJ = "RJ", "Rio de Janeiro"
    RN = "RN", "Rio Grande do Norte"
    RS = "RS", "Rio Grande do Sul"
    RO = "RO", "Rondônia"
    RR = "RR", "Roraima"
    SC = "SC", "Santa Catarina"
    SP = "SP", "São Paulo"
    SE = "SE", "Sergipe"
    TO = "TO", "Tocantins"


class TipoArquivo(models.TextChoices):
    """Define os tipos de arquivo suportados pela aplicação."""

    IMAGEM = "imagem", "Imagem"
    DOCUMENTO = "documento", "Documento"
    COMPACTADO = "compactado", "Compactado"


MAPA_EXTENSOES_TIPO_ARQUIVO = {
    **dict.fromkeys(EXTENSOES_IMAGENS, TipoArquivo.IMAGEM),
    **dict.fromkeys(EXTENSOES_DOCUMENTOS, TipoArquivo.DOCUMENTO),
    **dict.fromkeys(EXTENSOES_COMPACTADOS, TipoArquivo.COMPACTADO),
}
