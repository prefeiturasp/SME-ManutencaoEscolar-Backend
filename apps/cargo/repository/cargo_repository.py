"""Repositório de cargos."""

from typing import Any, cast

from django.db import transaction
from django.forms.models import model_to_dict

from apps.cargo.models import Cargo, DocumentoCargo
from apps.usuarios.models.usuario import Usuario


class CargoRepository:
    """Gerencia as operações de persistência de cargos."""

    model: type[Cargo] = Cargo
    documento_model: type[DocumentoCargo] = DocumentoCargo

    @transaction.atomic
    def criar(
        self,
        dados: dict[str, Any],
        usuario: Usuario,
    ) -> dict[str, Any]:
        """Cria e persiste um cargo e seus documentos.

        O cargo e seus documentos são persistidos na mesma transação. Caso
        alguma operação falhe, nenhuma alteração será mantida no banco.

        Args:
            dados: Dados necessários para criar o cargo, incluindo os
                documentos que serão vinculados.
            usuario: Usuário responsável pela criação e pela última
                atualização do cargo.

        Returns:
            Dicionário contendo os dados do cargo criado, seus documentos,
            UUID e chave primária.

        Raises:
            ValidationError: Quando os dados do cargo ou de seus documentos
                não passam pelas validações dos modelos.
            IntegrityError: Quando ocorre uma violação de integridade durante
                a criação do cargo ou de seus documentos.
        """
        dados_cargo = dados.copy()
        documentos = cast(
            list[dict[str, Any]],
            dados_cargo.pop("documentos", []),
        )

        cargo = self.model(
            **dados_cargo,
            criado_por=usuario,
            atualizado_por=usuario,
        )
        cargo.full_clean()
        cargo.save()

        documentos_cargo = [
            self.documento_model(
                **dados_documento,
                cargo=cargo,
                criado_por=usuario,
                atualizado_por=usuario,
            )
            for dados_documento in documentos
        ]

        for documento in documentos_cargo:
            documento.full_clean()

        self.documento_model.objects.bulk_create(documentos_cargo)

        dados_cargo = model_to_dict(cargo)
        dados_cargo["documentos"] = documentos_cargo
        dados_cargo["uuid"] = cargo.uuid
        dados_cargo["pk"] = cargo.pk

        return dados_cargo
