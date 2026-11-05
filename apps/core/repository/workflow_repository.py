"""Responsável pela persistência dos processos de workflow."""

from typing import Any

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import QuerySet

from apps.core.models import HistoricoWorkflow, ProcessoWorkflow
from apps.usuarios.models import Usuario


class WorkflowRepository:
    """Gerencia a persistência dos processos e históricos de workflow."""

    @transaction.atomic
    def registrar_transicao(
        self,
        app_label: str,
        tipo_entidade: str,
        entidade: dict[str, Any],
        resultado_workflow: dict[str, Any],
    ) -> None:
        """Registra uma transição e atualiza o processo da entidade."""
        model = apps.get_model(app_label, tipo_entidade)
        content_type = ContentType.objects.get_for_model(model)
        entidade_id = entidade["id"]
        processo, _ = ProcessoWorkflow.objects.get_or_create(
            content_type=content_type,
            entidade_referencia=str(entidade_id),
            defaults={
                "estado_atual": resultado_workflow["proximo_estado"],
                "terminal": resultado_workflow["terminal"],
            },
        )

        processo.estado_atual = resultado_workflow["proximo_estado"]
        processo.terminal = resultado_workflow["terminal"]

        processo.save(
            update_fields=["estado_atual", "terminal"],
        )

        dados_historico = {
            **resultado_workflow,
            "autor": Usuario.objects.get(
                uuid=resultado_workflow["autor"],
            ),
        }

        HistoricoWorkflow.objects.create(
            processo=processo,
            identificador=dados_historico["identificador"],
            estado_anterior=dados_historico["estado_anterior"],
            acao=dados_historico["acao"],
            proximo_estado=dados_historico["proximo_estado"],
            terminal=dados_historico["terminal"],
            sucesso=dados_historico["sucesso"],
            mensagem=dados_historico["mensagem"],
            inicio=dados_historico["inicio"],
            fim=dados_historico["fim"],
            autor=dados_historico["autor"],
            contexto=dados_historico["contexto"],
        )

    def obter_historico(
        self,
        app_label: str,
        tipo_entidade: str,
        entidade_id: str,
    ) -> QuerySet[HistoricoWorkflow]:
        content_type = ContentType.objects.get(
            app_label=app_label,
            model=tipo_entidade.lower(),
        )

        return HistoricoWorkflow.objects.filter(
            processo__content_type=content_type,
            processo__entidade_referencia=str(entidade_id),
        )


# {
#     'identificador': '484522ce-520d-40aa-a067-1295ea4fc770',
#     'estado_anterior': 'nao_criada',
#     'acao': 'enviar',
#     'proximo_estado': 'aguardando_analise_dre',
#     'terminal': False,
#     'sucesso': True,
#     'mensagem': 'Transição executada com sucesso!',
#     'inicio': datetime.datetime(
# 2026, 11, 5, 13, 37, 21, 945036, tzinfo=datetime.timezone.utc),
#     'fim': datetime.datetime(
# 2026, 11, 5, 13, 37, 21, 949372, tzinfo=datetime.timezone.utc),
#     'autor': 'f86c50a6-a31d-4d38-9a51-859f5d549555',
#     'contexto': {
#         'autor': 'f86c50a6-a31d-4d38-9a51-859f5d549555',
#         'identificador': '484522ce-520d-40aa-a067-1295ea4fc770',
#         'dados': {
#             'origem': 'aplicacao_consumidora'
#             }
#         }
#     }
