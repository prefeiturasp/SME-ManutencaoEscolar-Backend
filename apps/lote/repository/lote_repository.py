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
        """Retorna os nomes das DREs e dos lotes vinculados."""
        diretoria_regional_ids = [dre.pk for dre in diretorias_regionais]

        vinculos = self.vinculo_model.objects.filter(
            diretoria_regional_id__in=diretoria_regional_ids,
        ).values_list(
            "diretoria_regional__nome",
            "lote__codigo_cadastro",
        )

        return [
            (str(dre_nome), str(lote_nome)) for dre_nome, lote_nome in vinculos
        ]

    @transaction.atomic
    def criar(
        self,
        dados: dict[str, Any],
        usuario: Usuario,
    ) -> dict[str, Any]:
        """Cria um lote e seus vínculos com DREs."""
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
