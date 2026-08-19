"""Repositório de lotes."""

from typing import Any, cast

from django.db import transaction
from django.forms.models import model_to_dict

from apps.escola.models import DiretoriaRegional
from apps.lote.models import Lote, LoteDRE
from apps.usuarios.models.usuario import Usuario
from apps.escola.models import DiretoriaRegional

class LoteRepository:
    """Gerencia as operações de persistência de lotes."""

    model: type[Lote] = Lote
    vinculo_model: type[LoteDRE] = LoteDRE

    def _obter_dres_vinculadas(
    self,
    dres: list[DiretoriaRegional],
    ) -> list[tuple[str, str]]:
        """Retorna os nomes das DREs e dos lotes vinculados."""
        dre_ids = [dre.pk for dre in dres]

        vinculos = self.vinculo_model.objects.filter(
            dre_id__in=dre_ids,
        ).values_list(
            "dre__nome",
            "lote__codigo_cadastro",
        )

        return [
            (str(dre_nome), str(lote_nome))
            for dre_nome, lote_nome in vinculos
        ]

    @transaction.atomic
    def criar(
        self,
        dados: dict[str, Any],
        usuario: Usuario,
    ) -> Lote:
        """Cria um lote e seus vínculos com DREs."""
        dados_lote = dados.copy()
        dres = cast(
            list[DiretoriaRegional],
            dados_lote.pop("dres", []),
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
                    dre=dre,
                )
                for dre in dres
            ]
        )

        dados_lote = model_to_dict(lote)
        dados_lote["empresa"] = lote.empresa
        dados_lote["dres"] = list(lote.dres)
        dados_lote["uuid"] = lote.uuid
        dados_lote["pk"] = lote.id

        return dados_lote
