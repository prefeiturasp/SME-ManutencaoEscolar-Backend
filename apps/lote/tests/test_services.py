"""Testes do serviço responsável pelas regras de negócio dos lotes."""

from datetime import date
from typing import Any
from unittest.mock import Mock, patch

import pytest

from apps.escola.models import DiretoriaRegional
from apps.lote.constants import LoteErrorMessages
from apps.lote.exceptions import DiretoriaRegionalJaVinculadaError
from apps.lote.models import Lote
from apps.lote.repository.lote_repository import LoteRepository
from apps.lote.services.lote_service import LoteService
from apps.usuarios.models.usuario import Usuario


class TestLoteService:
    """Testa as regras de negócio do serviço de lotes."""

    @staticmethod
    def criar_repository() -> Mock:
        """Cria um repository simulado."""
        return Mock(spec=LoteRepository)

    @staticmethod
    def criar_usuario() -> Mock:
        """Cria um usuário simulado."""
        return Mock(spec=Usuario)

    @staticmethod
    def criar_lote() -> Mock:
        """Cria um lote simulado."""
        return Mock(spec=Lote)

    @staticmethod
    def criar_diretoria_regional() -> Mock:
        """Cria uma diretoria regional simulada."""
        return Mock(spec=DiretoriaRegional)

    @staticmethod
    def criar_dados_completos(
        diretoria: Mock,
    ) -> dict[str, Any]:
        """Cria dados completos para cadastro de lote."""
        return {
            "codigo_cadastro": "  LOTE-001  ",
            "nome": "  Lote Norte  ",
            "status": True,
            "empresa": 1,
            "periodo_inicial": date(2026, 9, 1),
            "periodo_final": date(2026, 9, 30),
            "diretorias_regionais": [diretoria],
        }

    @patch(
        "apps.lote.services.lote_service.LoteRepository",
        autospec=True,
    )
    def test_deve_inicializar_com_repository_padrao(
        self,
        repository_class: Mock,
    ) -> None:
        """Deve criar o repository padrão quando não for informado."""
        repository = repository_class.return_value

        service = LoteService()

        repository_class.assert_called_once_with()
        assert service.repository is repository

    def test_deve_inicializar_com_repository_informado(
        self,
    ) -> None:
        """Deve utilizar o repository recebido."""
        repository = self.criar_repository()

        service = LoteService(repository=repository)

        assert service.repository is repository

    def test_deve_criar_lote_com_dados_normalizados(
        self,
    ) -> None:
        """Deve normalizar nome e código antes da criação."""
        repository = self.criar_repository()
        usuario = self.criar_usuario()
        diretoria = self.criar_diretoria_regional()
        dados = self.criar_dados_completos(diretoria)

        resultado_esperado = {
            "id": 1,
            "codigo_cadastro": "LOTE-001",
            "nome": "Lote Norte",
        }

        repository._obter_diretorias_regionais_vinculadas.return_value = []
        repository.criar.return_value = resultado_esperado

        service = LoteService(repository=repository)

        resultado = service.criar(
            dados=dados,
            usuario=usuario,
        )

        repository._obter_diretorias_regionais_vinculadas.assert_called_once_with(
            [diretoria],
        )
        repository.criar.assert_called_once_with(
            {
                "codigo_cadastro": "LOTE-001",
                "nome": "Lote Norte",
                "status": True,
                "empresa": 1,
                "periodo_inicial": date(2026, 9, 1),
                "periodo_final": date(2026, 9, 30),
                "diretorias_regionais": [diretoria],
            },
            usuario=usuario,
        )

        assert resultado == resultado_esperado

        # O dicionário original não pode ser modificado.
        assert dados["codigo_cadastro"] == "  LOTE-001  "
        assert dados["nome"] == "  Lote Norte  "

    def test_deve_criar_lote_sem_diretorias_regionais(
        self,
    ) -> None:
        """Deve considerar uma lista vazia quando não houver DREs."""
        repository = self.criar_repository()
        usuario = self.criar_usuario()

        dados = {
            "codigo_cadastro": "  LOTE-001  ",
            "nome": "  Lote Norte  ",
            "status": True,
        }
        resultado_esperado = {
            "id": 1,
            "codigo_cadastro": "LOTE-001",
            "nome": "Lote Norte",
            "status": True,
        }

        repository._obter_diretorias_regionais_vinculadas.return_value = []
        repository.criar.return_value = resultado_esperado

        service = LoteService(repository=repository)

        resultado = service.criar(
            dados=dados,
            usuario=usuario,
        )

        repository._obter_diretorias_regionais_vinculadas.assert_called_once_with(
            [],
        )
        repository.criar.assert_called_once_with(
            {
                "codigo_cadastro": "LOTE-001",
                "nome": "Lote Norte",
                "status": True,
            },
            usuario=usuario,
        )

        assert resultado == resultado_esperado
        assert dados["codigo_cadastro"] == "  LOTE-001  "
        assert dados["nome"] == "  Lote Norte  "

    def test_deve_rejeitar_criacao_com_diretoria_vinculada(
        self,
    ) -> None:
        """Deve rejeitar DRE vinculada a outro lote."""
        repository = self.criar_repository()
        usuario = self.criar_usuario()
        diretoria = self.criar_diretoria_regional()

        dados = {
            "codigo_cadastro": "LOTE-001",
            "nome": "Lote Norte",
            "diretorias_regionais": [diretoria],
        }
        vinculados = [
            (
                "DRE CAPELA DO SOCORRO",
                "LOTE-002",
            )
        ]

        repository._obter_diretorias_regionais_vinculadas.return_value = (
            vinculados
        )

        service = LoteService(repository=repository)

        with pytest.raises(DiretoriaRegionalJaVinculadaError) as exc_info:
            service.criar(
                dados=dados,
                usuario=usuario,
            )

        repository._obter_diretorias_regionais_vinculadas.assert_called_once_with(
            [diretoria],
        )
        repository.criar.assert_not_called()

        assert exc_info.value.title == (
            LoteErrorMessages.DIRETORIA_REGIONAL_VINCULADA_TITULO
        )
        assert exc_info.value.detail == {
            "message": (LoteErrorMessages.DIRETORIA_REGIONAL_VINCULADA),
            "vinculados": vinculados,
        }

    def test_deve_atualizar_lote_com_sucesso(
        self,
    ) -> None:
        """Deve validar as DREs e encaminhar a atualização."""
        repository = self.criar_repository()
        usuario = self.criar_usuario()
        lote = self.criar_lote()
        diretoria = self.criar_diretoria_regional()

        dados = {
            "nome": "Lote atualizado",
            "status": True,
            "diretorias_regionais": [diretoria],
        }
        resultado_esperado = {
            "id": 1,
            "nome": "Lote atualizado",
            "status": True,
        }

        repository._obter_diretorias_regionais_vinculadas.return_value = []
        repository.atualizar.return_value = resultado_esperado

        service = LoteService(repository=repository)

        resultado = service.atualizar(
            lote=lote,
            dados=dados,
            usuario=usuario,
        )

        repository._obter_diretorias_regionais_vinculadas.assert_called_once_with(
            [diretoria],
            lote_ignorado=lote,
        )
        repository.atualizar.assert_called_once_with(
            lote,
            dados,
            usuario=usuario,
        )

        assert resultado == resultado_esperado

    def test_deve_atualizar_lote_sem_diretorias_regionais(
        self,
    ) -> None:
        """Deve considerar lista vazia quando DREs não forem enviadas."""
        repository = self.criar_repository()
        usuario = self.criar_usuario()
        lote = self.criar_lote()

        dados = {
            "nome": "Lote atualizado",
            "status": False,
        }
        resultado_esperado = {
            "id": 1,
            "nome": "Lote atualizado",
            "status": False,
        }

        repository._obter_diretorias_regionais_vinculadas.return_value = []
        repository.atualizar.return_value = resultado_esperado

        service = LoteService(repository=repository)

        resultado = service.atualizar(
            lote=lote,
            dados=dados,
            usuario=usuario,
        )

        repository._obter_diretorias_regionais_vinculadas.assert_called_once_with(
            [],
            lote_ignorado=lote,
        )
        repository.atualizar.assert_called_once_with(
            lote,
            dados,
            usuario=usuario,
        )

        assert resultado == resultado_esperado

    def test_atualizacao_nao_deve_modificar_dicionario_original(
        self,
    ) -> None:
        """Deve enviar uma cópia dos dados ao repository."""
        repository = self.criar_repository()
        usuario = self.criar_usuario()
        lote = self.criar_lote()
        diretoria = self.criar_diretoria_regional()

        dados = {
            "nome": "Lote atualizado",
            "diretorias_regionais": [diretoria],
        }
        dados_originais = dados.copy()

        repository._obter_diretorias_regionais_vinculadas.return_value = []
        repository.atualizar.return_value = {
            "nome": "Lote atualizado",
        }

        service = LoteService(repository=repository)

        service.atualizar(
            lote=lote,
            dados=dados,
            usuario=usuario,
        )

        dados_enviados = repository.atualizar.call_args.args[1]

        assert dados == dados_originais
        assert dados_enviados == dados
        assert dados_enviados is not dados

    def test_deve_rejeitar_atualizacao_com_diretoria_vinculada(
        self,
    ) -> None:
        """Deve rejeitar atualização com DRE vinculada."""
        repository = self.criar_repository()
        usuario = self.criar_usuario()
        lote = self.criar_lote()
        diretoria = self.criar_diretoria_regional()

        dados = {
            "nome": "Lote atualizado",
            "diretorias_regionais": [diretoria],
        }
        vinculados = [
            (
                "DRE CAPELA DO SOCORRO",
                "LOTE-002",
            )
        ]

        repository._obter_diretorias_regionais_vinculadas.return_value = (
            vinculados
        )

        service = LoteService(repository=repository)

        with pytest.raises(DiretoriaRegionalJaVinculadaError) as exc_info:
            service.atualizar(
                lote=lote,
                dados=dados,
                usuario=usuario,
            )

        repository._obter_diretorias_regionais_vinculadas.assert_called_once_with(
            [diretoria],
            lote_ignorado=lote,
        )
        repository.atualizar.assert_not_called()

        assert exc_info.value.title == (
            LoteErrorMessages.DIRETORIA_REGIONAL_VINCULADA_TITULO
        )
        assert exc_info.value.detail == {
            "message": (LoteErrorMessages.DIRETORIA_REGIONAL_VINCULADA),
            "vinculados": vinculados,
        }

    def test_deve_deletar_lote(
        self,
    ) -> None:
        """Deve delegar a exclusão lógica ao repository."""
        repository = self.criar_repository()
        usuario = self.criar_usuario()
        lote = self.criar_lote()

        resultado_esperado = (
            1,
            {
                "lotes": 1,
            },
        )
        repository.deletar.return_value = resultado_esperado

        service = LoteService(repository=repository)

        resultado = service.deletar(
            model_lote=lote,
            usuario=usuario,
        )

        repository.deletar.assert_called_once_with(
            usuario,
            lote,
        )
        assert resultado == resultado_esperado
