"""Constantes do app escola."""

ENDPOINT_TIPO_ESCOLA = "/escolas/tiposEscolas"
ENDPOINT_SUBPREFEITURA = "/DREs/{codigo_dre}/subprefeituras"
ENDPOINT_OBTER_ESCOLA = "/escolas/todas-unidades"
ENDPOINT_OBTER_FUNCIONARIOS_POR_CARGO = (
    "/escolas/{codigo_escola}/funcionarios/cargos/{codigo_cargo}"
)

FORMATO_DATA_FUNCIONARIOS_POR_CARGO = "%m/%d/%Y %H:%M:%S"

TIPO_ESCOLA_NAO_ACEITAS = {
    "CCA",
    "CEU",
    "CEU POLO UAB",
    "E TEC",
    "EMES 1.2",
    "EMES 1.G",
    "EMES 2.G",
    "EMFORPEF",
    "ESC PART NR",
    "ESC.PART.",
    "EXTE",
    "EXTF",
    "EXTM",
    "EXTP",
    "PBA",
}
