"""Testes do serviço responsável pelas regras de negócio dos lotes."""

from datetime import date
from typing import Any
from unittest.mock import Mock, patch

import pytest

from apps.empresa.models import Empresa
from apps.equipe.models import Equipe
from apps.escola.models import DiretoriaRegional
from apps.lote.constants import LoteErrorMessages
from apps.lote.exceptions import (
    DiretoriaRegionalJaVinculadaError,
    LoteVinculadoEquipeError,
)
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

    def test_nao_deve_alterar_empresa_de_lote_vinculado_a_equipe(
        self,
        db: None,
        lote_centro: Lote,
        usuario_ativo: Usuario,
        empresa_payload_valido: dict[str, str],
    ) -> None:
        """Não deve alterar a empresa de lote que possui equipe vinculada."""
        equipe = Equipe.objects.create(
            nome="Equipe vinculada",
            empresa=lote_centro.empresa,
            lote=lote_centro,
        )
        dados_outra_empresa = {
            **empresa_payload_valido,
            "nome": "Outra empresa",
            "cnpj": "98765432109876",
        }
        outra_empresa = Empresa.objects.create(**dados_outra_empresa)
        lote_service = LoteService()

        with pytest.raises(LoteVinculadoEquipeError) as exc_info:
            lote_service.atualizar(
                lote=lote_centro,
                dados={"empresa": outra_empresa},
                usuario=usuario_ativo,
            )

        lote_centro.refresh_from_db()
        assert lote_centro.empresa_id != outra_empresa.id
        titulo = LoteErrorMessages.ALTERACAO_EMPRESA_LOTE_VINCULADO_TITULO
        mensagem = LoteErrorMessages.ALTERACAO_EMPRESA_LOTE_VINCULADO
        assert exc_info.value.title == titulo
        assert exc_info.value.detail == {
            "message": mensagem,
            "equipes": [{"uuid": equipe.uuid, "nome": equipe.nome}],
        }

    def test_deve_alterar_empresa_de_lote_sem_equipe_vinculada(
        self,
        db: None,
        lote_centro: Lote,
        usuario_ativo: Usuario,
        empresa_payload_valido: dict[str, str],
    ) -> None:
        """Deve alterar a empresa quando o lote não possui equipe."""
        dados_outra_empresa = {
            **empresa_payload_valido,
            "nome": "Outra empresa",
            "cnpj": "98765432109876",
        }
        outra_empresa = Empresa.objects.create(**dados_outra_empresa)

        resultado = LoteService().atualizar(
            lote=lote_centro,
            dados={"empresa": outra_empresa},
            usuario=usuario_ativo,
        )

        lote_centro.refresh_from_db()
        assert lote_centro.empresa == outra_empresa
        assert resultado["empresa"] == outra_empresa.pk

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
        repository.buscar_equipes_vinculadas.return_value = []

        service = LoteService(repository=repository)

        resultado = service.deletar(
            model_lote=lote,
            usuario=usuario,
        )

        repository.deletar.assert_called_once_with(
            usuario,
            lote,
        )
        repository.buscar_equipes_vinculadas.assert_called_once_with(lote)
        assert resultado == resultado_esperado

    def test_nao_deve_deletar_lote_vinculado_a_equipe(
        self,
        db: None,
        lote_centro: Lote,
        usuario_ativo: Usuario,
    ) -> None:
        """Não deve excluir um lote que possui equipe vinculada."""
        Equipe.objects.create(
            nome="Equipe vinculada",
            empresa=lote_centro.empresa,
            lote=lote_centro,
        )
        service = LoteService()

        with pytest.raises(LoteVinculadoEquipeError) as exc_info:
            service.deletar(
                model_lote=lote_centro,
                usuario=usuario_ativo,
            )

        lote_centro.refresh_from_db()
        assert exc_info.value.title == (
            LoteErrorMessages.LOTE_VINCULADO_EQUIPE_TITULO
        )
        assert exc_info.value.detail == (
            {
                "message": LoteErrorMessages.LOTE_VINCULADO_EQUIPE,
                "equipes": [
                    {
                        "uuid": Equipe.objects.get(
                            nome="Equipe vinculada",
                            lote=lote_centro,
                        ).uuid,
                        "nome": "Equipe vinculada",
                    }
                ],
            }
        )
        assert lote_centro.deletado_em is None
