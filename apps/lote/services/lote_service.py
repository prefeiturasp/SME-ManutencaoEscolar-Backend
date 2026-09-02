"""Serviços relacionados ao cadastro de lotes."""

from typing import Any, cast

from django.utils import timezone

from apps.escola.models import DiretoriaRegional
from apps.lote.constants import LoteErrorMessages
from apps.lote.exceptions import DiretoriaRegionalJaVinculadaError
from apps.lote.models import Lote
from apps.lote.repository.lote_repository import LoteRepository
from apps.usuarios.models.usuario import Usuario


class LoteService:
    """Orquestra as regras de negócio relacionadas aos lotes."""

    def __init__(
        self,
        repository: LoteRepository | None = None,
    ) -> None:
        """Inicializa o serviço com o repositório informado ou o padrão."""
        self.repository = repository or LoteRepository()

    def inativar_lotes_com_prazo_finalizado(self) -> int:
        """Inativa os lotes cujo prazo da licitação já terminou.

        Returns:
            Quantidade de lotes inativados.
        """
        data_atual = timezone.localdate()

        return self.repository.inativar_lotes_com_prazo_finalizado(
            data_referencia=data_atual,
        )

    def criar(
        self,
        dados: dict[str, Any],
        usuario: Usuario,
    ) -> dict[str, Any]:
        """Valida e cria um novo lote.

        O nome e o código de cadastro são normalizados, e as diretorias
        regionais são verificadas antes da persistência do lote.

        Args:
            dados (dict[str, Any]): Dados necessários para a criação do lote,
                incluindo nome, código de cadastro, status, empresa, período
                inicial, período final e diretorias regionais.
            usuario (Usuario): Usuário responsável pela criação do lote.

        Returns:
            dict[str, Any]: Dicionário contendo os dados do lote criado:
            - codigo_cadastro (str): Código de cadastro do lote.
            - nome (str): Nome normalizado do lote.
            - status (bool): Status do lote.
            - empresa (Empresa): Empresa associada ao lote.
            - periodo_inicial (date): Data inicial do período do lote.
            - periodo_final (date): Data final do período do lote.
            - diretorias_regionais (list[DiretoriaRegional]): Diretorias
                regionais vinculadas ao lote.
            - uuid (str): Identificador único do lote.
            - pk (int): Chave primária do lote.

        Raises:
            DiretoriaRegionalJaVinculadaError: Quando uma ou mais diretorias
                regionais informadas já estão vinculadas a outro lote.
            ValidationError: Quando os dados do lote não passam pelas
                validações definidas no modelo.
            IntegrityError: Quando ocorre uma violação de integridade durante
                a criação do lote ou de seus vínculos.
        """
        dados_normalizados = dados.copy()

        nome = dados_normalizados["nome"].strip()
        codigo_cadastro = dados_normalizados["codigo_cadastro"].strip()
        diretorias_regionais = cast(
            list[DiretoriaRegional],
            dados_normalizados.get("diretorias_regionais", []),
        )

        diretorias_regionais_vinculadas = (
            self.repository._obter_diretorias_regionais_vinculadas(
                diretorias_regionais,
            )
        )

        if diretorias_regionais_vinculadas:
            raise DiretoriaRegionalJaVinculadaError(
                title=LoteErrorMessages.DIRETORIA_REGIONAL_VINCULADA_TITULO,
                detail={
                    "message": LoteErrorMessages.DIRETORIA_REGIONAL_VINCULADA,
                    "vinculados": diretorias_regionais_vinculadas,
                },
            )
        dados_normalizados["nome"] = nome
        dados_normalizados["codigo_cadastro"] = codigo_cadastro

        return self.repository.criar(
            dados_normalizados,
            usuario=usuario,
        )

    def atualizar(
        self,
        lote: Lote,
        dados: dict[str, Any],
        usuario: Usuario,
    ) -> dict[str, Any]:
        """Atualiza um lote existente e retorna seus dados serializados.

        O nome e o código de cadastro são normalizados, e o usuário logado é
        registrado como responsável pela atualização. Quando ``dados`` contém a
        chave ``diretorias_regionais``, os vínculos informados são validados e
        sincronizados dentro de uma transação.

        Args:
            lote (Lote): Instância do lote a ser atualizado.
            dados (dict[str, Any]): Dados a serem aplicados na atualização,
                podendo incluir as diretorias regionais em
                ``diretorias_regionais``.
            usuario (Usuario): Usuário logado responsável pela atualização.

        Returns:
            dict[str, Any]: Dados serializados do lote atualizado.

        Raises:
            DiretoriaRegionalJaVinculadaError: Quando uma ou mais diretorias
                regionais informadas já estão vinculadas a outro lote.
            ValidationError: Quando os dados do lote não passam pelas
                validações definidas no modelo.
            IntegrityError: Quando ocorre uma violação de integridade durante
                a atualização do lote ou de seus vínculos.
        """
        dados_normalizados = dados.copy()

        diretorias_regionais = cast(
            list[DiretoriaRegional],
            dados_normalizados.get("diretorias_regionais", []),
        )

        diretorias_regionais_vinculadas = (
            self.repository._obter_diretorias_regionais_vinculadas(
                diretorias_regionais,
                lote_ignorado=lote,
            )
        )

        if diretorias_regionais_vinculadas:
            raise DiretoriaRegionalJaVinculadaError(
                title=LoteErrorMessages.DIRETORIA_REGIONAL_VINCULADA_TITULO,
                detail={
                    "message": LoteErrorMessages.DIRETORIA_REGIONAL_VINCULADA,
                    "vinculados": diretorias_regionais_vinculadas,
                },
            )

        return self.repository.atualizar(
            lote,
            dados_normalizados,
            usuario=usuario,
        )
