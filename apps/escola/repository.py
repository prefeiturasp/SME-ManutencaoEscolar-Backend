"""Repository do app escola."""

from typing import Any

from django.db import transaction
from django.forms.models import model_to_dict

from apps.escola.models.responsavel_unidade import (
    HistoricoResponsavel,
    ResponsavelUnidade,
)
from apps.escola.models.unidade_educacional import (
    DadosUnidadeEducacional,
    Unidadeeducacional,
)
from apps.usuarios.models.cargo_eol import CargoEOL
from apps.usuarios.models.usuario import Usuario


class UnidadeEducacionalRepository:
    """Gerencia as operações de persistência de unidades educacionais."""

    model: type[Unidadeeducacional] = Unidadeeducacional
    responsavel_model: type[ResponsavelUnidade] = ResponsavelUnidade
    historico_model: type[HistoricoResponsavel] = HistoricoResponsavel
    dados_model: type[DadosUnidadeEducacional] = DadosUnidadeEducacional

    def buscar_por_registro_funcional(
        self,
        registro_funcional: str,
    ) -> ResponsavelUnidade | None:
        """Busca um responsável pelo registro funcional."""
        return self.responsavel_model.objects.filter(
            registro_funcional=registro_funcional,
        ).first()

    def existe_vinculo_ativo(
        self,
        unidade: Unidadeeducacional,
        responsavel_uuid: str,
    ) -> bool:
        """Verifica se um responsável está vinculado à unidade."""
        return self.historico_model.objects.filter(
            responsavel__uuid=responsavel_uuid,
            unidade_educacional=unidade,
            ativo=True,
        ).exists()

    @transaction.atomic
    def atualizar(
        self,
        unidade: Unidadeeducacional,
        dados: dict[str, Any],
        responsaveis: list[dict[str, Any]],
        usuario: Usuario,
    ) -> dict[str, Any]:
        """Atualiza a unidade e seus responsáveis."""
        self._atualizar_dados_unidade(
            unidade=unidade,
            dados=dados,
        )

        for dados_responsavel in responsaveis:
            if dados_responsavel.get("uuid"):
                self._atualizar_responsavel(
                    unidade=unidade,
                    dados=dados_responsavel,
                    usuario=usuario,
                )
            else:
                self._criar_responsavel(
                    unidade=unidade,
                    dados=dados_responsavel,
                    usuario=usuario,
                )

        return self._serializar(unidade)

    def _atualizar_dados_unidade(
        self,
        unidade: Unidadeeducacional,
        dados: dict[str, Any],
    ) -> None:
        """Atualiza os dados principais e de contato da unidade."""
        unidade.status = dados["ativo"]
        unidade.full_clean()
        unidade.save()

        self.dados_model.objects.update_or_create(
            unidade_educacional=unidade,
            defaults={
                "email": dados["email"],
                "telefone": dados["telefone"],
            },
        )

    def _atualizar_responsavel(
        self,
        unidade: Unidadeeducacional,
        dados: dict[str, Any],
        usuario: Usuario,
    ) -> None:
        """Atualiza um responsável já vinculado à unidade."""
        historico = self.historico_model.objects.select_related(
            "responsavel",
            "cargo",
        ).get(
            responsavel__uuid=dados["uuid"],
            unidade_educacional=unidade,
            ativo=True,
        )

        responsavel = historico.responsavel

        responsavel.registro_funcional = dados["registro_funcional"]
        responsavel.nome = dados["nome"]
        responsavel.email = dados["email"]
        responsavel.telefone = dados["telefone"]
        responsavel.celular = dados["celular"]
        responsavel.atualizado_por = usuario

        responsavel.full_clean()
        responsavel.save()

        historico.cargo = self._obter_cargo(
            codigo=dados["cargo"],
        )
        historico.atualizado_por = usuario
        historico.full_clean()
        historico.save()

    def _criar_responsavel(
        self,
        unidade: Unidadeeducacional,
        dados: dict[str, Any],
        usuario: Usuario,
    ) -> None:
        """Cria um responsável e seu vínculo com a unidade."""
        responsavel = self.responsavel_model(
            registro_funcional=dados["registro_funcional"],
            nome=dados["nome"],
            email=dados["email"],
            telefone=dados["telefone"],
            celular=dados["celular"],
            criado_por=usuario,
            atualizado_por=usuario,
        )

        responsavel.full_clean()
        responsavel.save()

        historico = self.historico_model(
            responsavel=responsavel,
            unidade_educacional=unidade,
            cargo=self._obter_cargo(
                codigo=dados["cargo"],
            ),
            ativo=True,
            criado_por=usuario,
            atualizado_por=usuario,
        )

        historico.full_clean()
        historico.save()

    @staticmethod
    def _obter_cargo(
        codigo: str,
    ) -> CargoEOL:
        """Obtém o cargo pelo código EOL."""
        return CargoEOL.objects.get(
            codigo=codigo,
        )

    def _serializar(
        self,
        unidade: Unidadeeducacional,
    ) -> dict[str, Any]:
        """Serializa a unidade atualizada em um dicionário."""
        dados = model_to_dict(unidade)

        dados["id"] = unidade.id
        dados["uuid"] = str(unidade.uuid)

        dados_unidade = getattr(
            unidade,
            "dados",
            None,
        )

        dados["dados"] = (
            model_to_dict(dados_unidade) if dados_unidade else None
        )

        return dados
