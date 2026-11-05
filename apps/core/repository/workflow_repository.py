"""Responsável pela persistência dos processos de workflow."""

from typing import Any

from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from apps.core.models import HistoricoWorkflow, ProcessoWorkflow
from apps.usuarios.models import Usuario


class WorkflowRepository:
    """Gerencia a persistência dos processos e históricos de workflow."""

    @transaction.atomic
    def registrar_transicao(
        self,
        entidade: Any,
        resultado_workflow: dict[str, Any],
    ) -> ProcessoWorkflow:
        """Registra uma transição e atualiza o processo da entidade.

        Args:
            entidade: Instância da entidade controlada pelo workflow.
            resultado_workflow: Resultado completo retornado pelo SDK.

        Returns:
            Processo de workflow atualizado.
        """
        content_type = ContentType.objects.get_for_model(entidade)

        processo, _ = ProcessoWorkflow.objects.get_or_create(
            content_type=content_type,
            entidade_referencia=str(entidade.pk),
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
            resultado_completo={
                **resultado_workflow,
                "inicio": resultado_workflow["inicio"].isoformat(),
                "fim": (
                    resultado_workflow["fim"].isoformat()
                    if resultado_workflow["fim"]
                    else None
                ),
            },
        )

        return processo


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
