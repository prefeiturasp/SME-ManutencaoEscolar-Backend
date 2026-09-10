"""Schemas para a API de cargos."""

from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)

from apps.cargo.serializers import CargoCriarSerializer


_TAG_CARGO = "Cargo"

_CREDENCIAIS_INVALIDAS = "Credenciais inválidas"

_DADOS_INVALIDOS = "Dados inválidos ou cargo já cadastrado."

_ERRO_NO_SERVIDOR = "Erro no servidor"

_CARGO_EXEMPLO_ENTRADA: dict[str, object] = {
    "nome": "Eletricista",
    "exige_documento": True,
    "status": True,
    "documentos": [
        {
            "nome": "Certificado NR-10",
        },
        {
            "nome": "Comprovante de formação",
        },
    ],
}

_CARGO_EXEMPLO_SAIDA: dict[str, object] = {
    "nome": "Eletricista",
    "exige_documento": True,
    "status": True,
    "documentos": [
        {
            "nome": "Certificado NR-10",
        },
        {
            "nome": "Comprovante de formação",
        },
    ],
}

_CARGO_EXEMPLO_DADOS_INVALIDOS: dict[str, object] = {
    "documentos": [
        "Informe ao menos um documento para este cargo.",
    ],
}


CARGO_SCHEMA = extend_schema_view(
    create=extend_schema(
        tags=[_TAG_CARGO],
        summary="Cria um novo cargo",
        description=(
            "Cadastra um cargo e vincula os documentos informados. "
            "Quando o cargo exige documentos, ao menos um documento "
            "deve ser informado."
        ),
        operation_id="cadastrarCargo",
        request=CargoCriarSerializer,
        responses={
            201: CargoCriarSerializer,
            400: OpenApiResponse(
                description=_DADOS_INVALIDOS,
            ),
            401: OpenApiResponse(
                description=_CREDENCIAIS_INVALIDAS,
            ),
            500: OpenApiResponse(
                description=_ERRO_NO_SERVIDOR,
            ),
        },
        examples=[
            OpenApiExample(
                name="Exemplo de cadastro de cargo",
                request_only=True,
                value=_CARGO_EXEMPLO_ENTRADA,
            ),
            OpenApiExample(
                name="Cargo cadastrado com sucesso",
                response_only=True,
                status_codes=["201"],
                value=_CARGO_EXEMPLO_SAIDA,
            ),
            OpenApiExample(
                name="Documentos não informados",
                response_only=True,
                status_codes=["400"],
                value=_CARGO_EXEMPLO_DADOS_INVALIDOS,
            ),
        ],
    ),
)
