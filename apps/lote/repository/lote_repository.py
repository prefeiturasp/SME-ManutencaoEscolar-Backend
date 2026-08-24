"""Repositório de lotes."""

from typing import Any, cast

from django.db import transaction
from django.forms.models import model_to_dict

from apps.escola.models import DiretoriaRegional
from apps.lote.models import Lote, LoteDiretoriaRegional
from apps.usuarios.models.usuario import Usuario


class LoteRepository:
    """Gerencia as operações de persistência de lotes."""

    model: type[Lote] = Lote
    vinculo_model: type[LoteDiretoriaRegional] = LoteDiretoriaRegional

    def _obter_diretorias_regionais_vinculadas(
        self,
        diretorias_regionais: list[DiretoriaRegional],
    ) -> list[tuple[str, str]]:
        """Obtém as diretorias regionais já vinculadas a lotes.

        Args:
            diretorias_regionais: Diretorias regionais cujos vínculos
                devem ser consultados.

        Returns:
            Lista de tuplas contendo o nome da diretoria regional e o
            código de cadastro do lote ao qual ela está vinculada.
        """
        diretoria_regional_ids = [dre.pk for dre in diretorias_regionais]

        vinculos = self.vinculo_model.objects.filter(
            diretoria_regional_id__in=diretoria_regional_ids,
        ).select_related(
            "diretoria_regional",
            "lote",
        )

        return [
            (
                vinculo.diretoria_regional.nome_curto_dre,
                vinculo.lote.codigo_cadastro,
            )
            for vinculo in vinculos
        ]

    @transaction.atomic
    def criar(
        self,
        dados: dict[str, Any],
        usuario: Usuario,
    ) -> dict[str, Any]:
        """Cria e persiste um novo lote.

        O lote é associado ao usuário responsável pela criação e seus
        vínculos com as diretorias regionais são persistidos na mesma
        transação.

        Args:
            dados (dict[str, Any]): Dados necessários para a criação do
                lote, incluindo as diretorias regionais que serão vinculadas.
            usuario (Usuario): Usuário responsável pela criação e pela
                última atualização do lote.

        Returns:
            dict[str, Any]: Dicionário contendo os dados do lote criado:
            - codigo_cadastro: Código de cadastro do lote.
            - nome: Nome do lote.
            - status: Status do lote.
            - empresa: Empresa associada ao lote.
            - periodo_inicial: Data inicial do período do lote.
            - periodo_final: Data final do período do lote.
            - diretorias_regionais: Diretorias regionais vinculadas ao lote.
            - uuid: Identificador único do lote.
            - pk: Chave primária do lote.

        Raises:
            ValidationError: Quando os dados do lote não passam pelas
                validações definidas no modelo.
            IntegrityError: Quando ocorre uma violação de integridade durante
                a criação do lote ou de seus vínculos.
        """
        dados_lote = dados.copy()
        diretorias_regionais = cast(
            list[DiretoriaRegional],
            dados_lote.pop("diretorias_regionais", []),
        )

        lote = self.model(
            **dados_lote,
            criado_por=usuario,
            atualizado_por=usuario,
        )
        lote.full_clean()
        lote.save()

        self.vinculo_model.objects.bulk_create(
            [
                self.vinculo_model(
                    lote=lote,
                    diretoria_regional=diretoria_regional,
                )
                for diretoria_regional in diretorias_regionais
            ]
        )

        dados_lote = model_to_dict(lote)
        dados_lote["empresa"] = lote.empresa
        dados_lote["diretorias_regionais"] = list(lote.diretorias_regionais)
        dados_lote["uuid"] = lote.uuid
        dados_lote["pk"] = lote.id

        return dados_lote
