"""_summary_."""

from __future__ import annotations

import logging
import time
from datetime import date, datetime
from typing import Any

import requests
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from apps.core.constants import TIMEOUT_DEFAULT
from apps.escola.models.diretor import Diretor, HistoricoDiretorEscola
from apps.escola.models.unidade_educacional import Unidadeeducacional
from config.settings import SME_API_EOL_URL

logger = logging.getLogger(__name__)

CARGO_DIRETOR_ESCOLA = "3360"
FORMATO_DATA_API = "%m/%d/%Y %H:%M:%S"


class Command(BaseCommand):
    """Sincroniza os diretores das escolas com a API de integração."""

    help = "Sincroniza os diretores das escolas com a API de integração."

    def handle(self, *args: Any, **options: Any) -> None:
        """Executa a sincronização dos diretores."""
        inicio = time.perf_counter()

        escolas = Unidadeeducacional.objects.all().order_by("codigo_eol")
        total_escolas = escolas.count()

        if total_escolas == 0:
            logger.info("Nenhuma escola encontrada para sincronização.")
            return

        logger.info(
            "Iniciando importação de diretores para %s escolas.",
            total_escolas,
        )

        criados = 0
        atualizados = 0
        encerrados = 0
        sem_diretor = 0
        erros = 0

        for numero, escola in enumerate(escolas.iterator(), start=1):
            try:
                resultado = self._sincronizar_escola(escola)

                criados += resultado["criados"]
                atualizados += resultado["atualizados"]
                encerrados += resultado["encerrados"]

                if resultado["sem_diretor"]:
                    sem_diretor += 1

            except Exception as exc:
                erros += 1
                logger.exception(
                    "Erro ao sincronizar diretor da escola %s: %s",
                    escola.codigo_eol,
                    exc,
                )

            if numero % 100 == 0 or numero == total_escolas:
                logger.info(
                    "%s de %s escolas analisadas.",
                    numero,
                    total_escolas,
                )

        tempo = (time.perf_counter() - inicio) / 60

        logger.info(
            "Importação de diretores concluída em %.2f minutos:\n"
            "%s diretores criados\n"
            "%s diretores atualizados\n"
            "%s históricos encerrados\n"
            "%s escolas sem diretor\n"
            "%s escolas com erro",
            tempo,
            criados,
            atualizados,
            encerrados,
            sem_diretor,
            erros,
        )

    def _sincronizar_escola(
        self,
        escola: Unidadeeducacional,
    ) -> dict[str, int | bool]:
        """Sincroniza o diretor atual de uma escola."""
        registros = self._obter_diretor(escola.codigo_eol)

        if not registros:
            encerrado = self._encerrar_diretor_atual(escola)

            if encerrado:
                logger.info(
                    "Diretor encerrado para a escola %s.",
                    escola.codigo_eol,
                )

            return {
                "criados": 0,
                "atualizados": 0,
                "encerrados": int(encerrado),
                "sem_diretor": True,
            }

        registro = self._obter_registro_diretor_atual(
            registros,
            escola.codigo_eol,
        )

        codigo_rf = self._obter_string_obrigatoria(
            registro,
            "codigoRF",
            escola.codigo_eol,
        )
        nome = self._obter_string_obrigatoria(
            registro,
            "nomeServidor",
            escola.codigo_eol,
        )
        data_inicio = self._obter_data_inicio(
            registro,
            escola.codigo_eol,
        )

        email = self._obter_email(codigo_rf, escola.codigo_eol)

        with transaction.atomic():
            diretor, foi_criado = Diretor.objects.update_or_create(
                registro_funcional=codigo_rf,
                defaults={
                    "nome": nome,
                    "email": email,
                },
            )

            historico_atual = (
                HistoricoDiretorEscola.objects.select_for_update()
                .filter(
                    unidade_educacional=escola,
                    data_fim__isnull=True,
                )
                .select_related("diretor")
                .first()
            )

            if historico_atual and historico_atual.diretor_id == diretor.id:
                if historico_atual.data_inicio != data_inicio:
                    historico_atual.data_inicio = data_inicio
                    historico_atual.save(update_fields=("data_inicio",))

                return {
                    "criados": int(foi_criado),
                    "atualizados": 1,
                    "encerrados": 0,
                    "sem_diretor": False,
                }

            if historico_atual:
                self._encerrar_historico(
                    historico_atual,
                    data_inicio,
                )

            HistoricoDiretorEscola.objects.create(
                diretor=diretor,
                unidade_educacional=escola,
                data_inicio=data_inicio,
            )

        logger.info(
            "Diretor %s sincronizado para a escola %s.",
            codigo_rf,
            escola.codigo_eol,
        )

        return {
            "criados": int(foi_criado),
            "atualizados": int(not foi_criado),
            "encerrados": int(historico_atual is not None),
            "sem_diretor": False,
        }

    def _obter_diretor(
        self,
        codigo_escola: str,
    ) -> list[dict[str, Any]]:
        """Consulta o diretor da escola."""
        url = (
            f"{SME_API_EOL_URL}/escolas/"
            f"{codigo_escola}/funcionarios/cargos/{CARGO_DIRETOR_ESCOLA}"
        )

        try:
            response = requests.get(
                url,
                headers={"accept": "application/json"},
                timeout=TIMEOUT_DEFAULT,
            )
        except requests.RequestException as exc:
            raise CommandError(
                f"Erro ao consultar diretor da escola {codigo_escola}: {exc}"
            ) from exc

        if response.status_code == 204:
            return []

        if response.status_code != 200:
            raise CommandError(
                f"API de diretores retornou HTTP {response.status_code} "
                f"para a escola {codigo_escola}."
            )

        try:
            payload = response.json()
        except ValueError as exc:
            raise CommandError(
                f"A API de diretores retornou JSON inválido "
                f"para a escola {codigo_escola}."
            ) from exc

        if not isinstance(payload, list):
            raise CommandError(
                f"A API de diretores deveria retornar uma lista "
                f"para a escola {codigo_escola}."
            )

        return payload

    def _obter_email(
        self,
        codigo_rf: str,
        codigo_escola: str,
    ) -> str:
        """Consulta os dados de autenticação do servidor."""
        url = f"{SME_API_EOL_URL}/AutenticacaoCOMAPRE/{codigo_rf}/dados"

        try:
            response = requests.get(
                url,
                headers={"accept": "application/json"},
                timeout=TIMEOUT_DEFAULT,
            )
        except requests.RequestException as exc:
            logger.warning(
                "Não foi possível consultar o e-mail do RF %s "
                "da escola %s: %s",
                codigo_rf,
                codigo_escola,
                exc,
            )
            return ""

        if response.status_code != 200:
            logger.warning(
                "API de autenticação retornou HTTP %s para o RF %s "
                "da escola %s.",
                response.status_code,
                codigo_rf,
                codigo_escola,
            )
            return ""

        try:
            payload = response.json()
        except ValueError:
            logger.warning(
                "API de autenticação retornou JSON inválido para o RF %s.",
                codigo_rf,
            )
            return ""

        if not isinstance(payload, dict):
            logger.warning(
                "API de autenticação retornou payload inválido para o RF %s.",
                codigo_rf,
            )
            return ""

        email = payload.get("email", "")

        if not isinstance(email, str):
            return ""

        return email.strip()

    @staticmethod
    def _obter_registro_diretor_atual(
        registros: list[dict[str, Any]],
        codigo_escola: str,
    ) -> dict[str, Any]:
        """Seleciona o diretor atualmente ativo no retorno da API."""
        registros_validos = [
            registro
            for registro in registros
            if isinstance(registro, dict) and registro.get("dataFim") is None
        ]

        if len(registros_validos) == 1:
            return registros_validos[0]

        if not registros_validos:
            raise CommandError(
                f"A API não retornou diretor atual para a escola "
                f"{codigo_escola}, apesar de responder HTTP 200."
            )

        raise CommandError(
            f"A API retornou mais de um diretor atual para a escola "
            f"{codigo_escola}. Sincronização ignorada para evitar "
            "ambiguidade."
        )

    @staticmethod
    def _obter_string_obrigatoria(
        registro: dict[str, Any],
        campo: str,
        codigo_escola: str,
    ) -> str:
        """Obtém e valida um campo textual obrigatório."""
        valor = registro.get(campo)

        if not isinstance(valor, str) or not valor.strip():
            raise CommandError(
                f"Campo '{campo}' inválido para a escola {codigo_escola}."
            )

        return valor.strip()

    @staticmethod
    def _obter_data_inicio(
        registro: dict[str, Any],
        codigo_escola: str,
    ) -> date:
        """Converta a data de início retornada pela API."""
        valor = registro.get("dataInicio")

        if not isinstance(valor, str) or not valor.strip():
            raise CommandError(
                f"Campo 'dataInicio' inválido para a escola {codigo_escola}."
            )

        try:
            return datetime.strptime(
                valor.strip(),
                FORMATO_DATA_API,
            ).date()
        except ValueError as exc:
            raise CommandError(
                f"Data 'dataInicio' inválida para a escola "
                f"{codigo_escola}: {valor!r}."
            ) from exc

    @staticmethod
    def _encerrar_historico(
        historico: HistoricoDiretorEscola,
        data_inicio_novo: date,
    ) -> None:
        """Encerra o histórico anterior na data de início do novo diretor."""
        data_fim = data_inicio_novo

        if data_fim < historico.data_inicio:
            data_fim = historico.data_inicio

        historico.data_fim = data_fim
        historico.save(update_fields=("data_fim",))

    @staticmethod
    def _encerrar_diretor_atual(
        escola: Unidadeeducacional,
    ) -> bool:
        """Encerra o vínculo atual quando a API retorna 204."""
        historico = HistoricoDiretorEscola.objects.filter(
            unidade_educacional=escola,
            data_fim__isnull=True,
        ).first()

        if historico is None:
            return False

        historico.data_fim = timezone.localdate()
        historico.save(update_fields=("data_fim",))
        return True
