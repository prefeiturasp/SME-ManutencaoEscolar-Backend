"""Repositório de lotes."""

from collections.abc import Sequence
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

    def atualizar_diretorias_regionais(
        self,
        lote: Lote,
        diretorias_regionais: Sequence[DiretoriaRegional],
        usuario: Usuario,
    ) -> None:
        """Atualiza as diretorias regionais vinculadas ao lote.

        Remove vínculos que não foram mantidos e cria os novos
        vínculos informados.

        Args:
            lote: Lote cujos vínculos serão atualizados.
            diretorias_regionais: Diretorias que devem permanecer vinculadas.
            usuario: Usuário responsável pela atualização.
        """
        ids_recebidos = {diretoria.pk for diretoria in diretorias_regionais}

        vinculos_atuais = LoteDiretoriaRegional.objects.filter(
            lote=lote,
        )

        vinculos_atuais.exclude(
            diretoria_regional_id__in=ids_recebidos,
        ).delete()

        ids_atuais = set(
            vinculos_atuais.values_list(
                "diretoria_regional_id",
                flat=True,
            )
        )

        novos_vinculos = [
            LoteDiretoriaRegional(
                lote=lote,
                diretoria_regional=diretoria,
                criado_por=usuario,
            )
            for diretoria in diretorias_regionais
            if diretoria.pk not in ids_atuais
        ]

        LoteDiretoriaRegional.objects.bulk_create(novos_vinculos)

    def _obter_diretorias_regionais_vinculadas(
        self,
        diretorias_regionais: list[DiretoriaRegional],
        lote_ignorado: Lote | None = None,
    ) -> list[tuple[str, str]]:
        """Obtém DREs já vinculadas a outros lotes ativos."""

        diretoria_regional_ids = [
            diretoria.pk
            for diretoria in diretorias_regionais
        ]

        vinculos = self.vinculo_model.objects.filter(
            diretoria_regional_id__in=diretoria_regional_ids,
            lote__status=True,
        )

        if lote_ignorado is not None:
            vinculos = vinculos.exclude(
                lote_id=lote_ignorado.pk,
            )

        vinculos = vinculos.select_related(
            "diretoria_regional",
            "lote",
        )

        return [
            (
                vinculo.diretoria_regional.nome_curto,
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

    def atualizar(
        self,
        lote: Lote,
        dados: dict[str, Any],
        usuario: Usuario,
    ) -> dict[str, Any]:
        """Atualiza um lote e retorna seus dados serializados.

        Args:
            lote: Instância do lote que será atualizada.
            dados: Dados validados utilizados na atualização.
            usuario: Usuário responsável pela atualização.

        Returns:
            Dados serializados do lote atualizado.
        """
        lista_diretorias_regionais = dados.get("diretorias_regionais")
        print("vamos caralho >>>>", dados.get("diretorias_regionais"))

        if  lista_diretorias_regionais:
            dados.pop("diretorias_regionais")

        for campo, valor in dados.items():
            setattr(lote, campo, valor)
        lote.save()

        if lista_diretorias_regionais:
            diretorias_regionais = cast(
                list[DiretoriaRegional],
                lista_diretorias_regionais,
            )

            self.atualizar_diretorias_regionais(
                lote=lote,
                diretorias_regionais=diretorias_regionais,
                usuario=usuario,
            )

        lote.atualizado_por = usuario
        lote.full_clean()
        lote.save()

        return self._serializar(lote)

    def _serializar(self, lote: Lote) -> dict[str, Any]:
        """Serializa uma instância de Lote em um dicionário.

        Args:
            lote: Instância do lote a ser serializada.

        Returns:
            Dicionário contendo os dados do lote.
        """
        dados_lote = model_to_dict(lote)
        dados_lote["id"] = lote.id
        dados_lote["uuid"] = str(lote.uuid)

        return dados_lote
