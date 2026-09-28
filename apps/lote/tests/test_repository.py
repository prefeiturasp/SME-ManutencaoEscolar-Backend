"""Testes do repositório responsável pela persistência de lotes."""

from datetime import date

import pytest

from apps.lote.models import Lote, LoteDiretoriaRegional
from apps.lote.repository.lote_repository import LoteRepository


@pytest.mark.django_db
class TestLoteRepository:
    """Testa as operações de persistência de lotes."""

    def test_deve_possuir_models_configurados(self) -> None:
        """Deve utilizar os models do domínio de lotes."""
        repository = LoteRepository()

        assert repository.model is Lote
        assert repository.vinculo_model is LoteDiretoriaRegional

    def test_deve_atualizar_diretorias_regionais(
        self,
        lote_centro,
        diretoria_regional_centro,
        diretoria_regional_nova,
        usuario_ativo,
    ) -> None:
        """Deve remover vínculos antigos e criar somente os novos."""
        repository = LoteRepository()

        repository.atualizar_diretorias_regionais(
            lote=lote_centro,
            diretorias_regionais=[
                diretoria_regional_centro,
                diretoria_regional_nova,
            ],
            usuario=usuario_ativo,
        )

        vinculos = LoteDiretoriaRegional.objects.filter(lote=lote_centro)

        assert set(
            vinculos.values_list("diretoria_regional_id", flat=True)
        ) == {
            diretoria_regional_centro.pk,
            diretoria_regional_nova.pk,
        }

        novo_vinculo = vinculos.get(
            diretoria_regional=diretoria_regional_nova,
        )
        assert novo_vinculo.criado_por == usuario_ativo

    def test_deve_remover_todas_as_diretorias_quando_lista_vazia(
        self,
        lote_centro,
        usuario_ativo,
    ) -> None:
        """Deve remover todos os vínculos quando nenhuma DRE for informada."""
        repository = LoteRepository()

        repository.atualizar_diretorias_regionais(
            lote=lote_centro,
            diretorias_regionais=[],
            usuario=usuario_ativo,
        )

        assert not LoteDiretoriaRegional.objects.filter(
            lote=lote_centro,
        ).exists()

    def test_deve_obter_diretorias_regionais_vinculadas(
        self,
        lote_centro,
        diretoria_regional_centro,
    ) -> None:
        """Deve retornar DREs vinculadas a lotes ativos."""
        repository = LoteRepository()

        resultado = repository._obter_diretorias_regionais_vinculadas(
            [diretoria_regional_centro],
        )

        assert resultado == [
            (
                diretoria_regional_centro.nome_curto,
                lote_centro.codigo_cadastro,
            ),
        ]

    def test_deve_obter_diretorias_com_lista_vazia(self) -> None:
        """Deve retornar vazio quando nenhuma DRE for informada."""
        repository = LoteRepository()

        resultado = repository._obter_diretorias_regionais_vinculadas([])

        assert resultado == []

    def test_deve_desconsiderar_lote_informado(
        self,
        lote_centro,
        diretoria_regional_centro,
    ) -> None:
        """Deve ignorar o lote informado na busca por vínculos."""
        repository = LoteRepository()

        resultado = repository._obter_diretorias_regionais_vinculadas(
            [diretoria_regional_centro],
            lote_ignorado=lote_centro,
        )

        assert resultado == []

    def test_deve_criar_lote_com_diretorias_regionais(
        self,
        empresa,
        usuario_ativo,
        diretoria_regional_centro,
        diretoria_regional_nova,
    ) -> None:
        """Deve criar o lote e os vínculos com as DREs."""
        repository = LoteRepository()
        diretorias = [
            diretoria_regional_centro,
            diretoria_regional_nova,
        ]

        dados = {
            "codigo_cadastro": "LOTE-002",
            "nome": "Lote Novo",
            "status": True,
            "empresa": empresa,
            "periodo_inicial": date(2026, 9, 1),
            "periodo_final": date(2026, 9, 30),
            "diretorias_regionais": diretorias,
        }

        resultado = repository.criar(
            dados=dados,
            usuario=usuario_ativo,
        )

        lote = Lote.objects.get(pk=resultado["pk"])

        assert resultado["codigo_cadastro"] == "LOTE-002"
        assert resultado["nome"] == "Lote Novo"
        assert resultado["status"] is True
        assert resultado["empresa"] == empresa
        assert resultado["periodo_inicial"] == date(2026, 9, 1)
        assert resultado["periodo_final"] == date(2026, 9, 30)
        assert resultado["diretorias_regionais"] == diretorias
        assert resultado["uuid"] == lote.uuid
        assert resultado["pk"] == lote.pk

        assert lote.criado_por == usuario_ativo
        assert lote.atualizado_por == usuario_ativo

        vinculos = LoteDiretoriaRegional.objects.filter(lote=lote)
        assert set(
            vinculos.values_list("diretoria_regional_id", flat=True)
        ) == {
            diretoria_regional_centro.pk,
            diretoria_regional_nova.pk,
        }

        assert dados["diretorias_regionais"] == diretorias

    def test_deve_criar_lote_sem_diretorias_regionais(
        self,
        empresa,
        usuario_ativo,
    ) -> None:
        """Deve criar lote sem vínculos quando DREs não forem enviadas."""
        repository = LoteRepository()

        dados = {
            "codigo_cadastro": "LOTE-003",
            "nome": "Lote sem DRE",
            "status": True,
            "empresa": empresa,
        }

        resultado = repository.criar(
            dados=dados,
            usuario=usuario_ativo,
        )

        lote = Lote.objects.get(pk=resultado["pk"])

        assert resultado["empresa"] == empresa
        assert resultado["diretorias_regionais"] == []
        assert resultado["uuid"] == lote.uuid
        assert resultado["pk"] == lote.pk
        assert not LoteDiretoriaRegional.objects.filter(lote=lote).exists()

    def test_deve_atualizar_lote_com_diretorias_regionais(
        self,
        lote_centro,
        diretoria_regional_nova,
        usuario_ativo,
    ) -> None:
        """Deve atualizar o lote e sincronizar suas DREs."""
        repository = LoteRepository()

        dados = {
            "nome": "Lote atualizado",
            "status": False,
            "diretorias_regionais": [diretoria_regional_nova],
        }

        resultado = repository.atualizar(
            lote=lote_centro,
            dados=dados,
            usuario=usuario_ativo,
        )

        lote_centro.refresh_from_db()
        vinculos = LoteDiretoriaRegional.objects.filter(lote=lote_centro)

        assert lote_centro.nome == "Lote atualizado"
        assert lote_centro.status is False
        assert lote_centro.atualizado_por == usuario_ativo
        assert list(
            vinculos.values_list("diretoria_regional_id", flat=True)
        ) == [
            diretoria_regional_nova.pk,
        ]
        assert resultado["id"] == lote_centro.id
        assert resultado["nome"] == "Lote atualizado"
        assert resultado["status"] is False
        assert resultado["uuid"] == str(lote_centro.uuid)

        assert "diretorias_regionais" not in dados

    def test_deve_atualizar_lote_sem_diretorias_regionais(
        self,
        lote_centro,
        usuario_ativo,
        diretoria_regional_centro,
    ) -> None:
        """Deve atualizar o lote sem alterar seus vínculos com DREs."""
        repository = LoteRepository()

        dados = {
            "nome": "Lote atualizado",
            "status": True,
        }

        resultado = repository.atualizar(
            lote=lote_centro,
            dados=dados,
            usuario=usuario_ativo,
        )

        lote_centro.refresh_from_db()

        assert lote_centro.nome == "Lote atualizado"
        assert lote_centro.status is True
        assert lote_centro.atualizado_por == usuario_ativo
        assert list(
            LoteDiretoriaRegional.objects.filter(lote=lote_centro).values_list(
                "diretoria_regional_id",
                flat=True,
            )
        ) == [diretoria_regional_centro.pk]
        assert resultado["id"] == lote_centro.id
        assert resultado["nome"] == "Lote atualizado"
        assert resultado["status"] is True

    def test_deve_serializar_lote(self, lote_centro) -> None:
        """Deve acrescentar ID e UUID aos dados serializados."""
        repository = LoteRepository()

        resultado = repository._serializar(lote_centro)

        assert resultado["id"] == lote_centro.id
        assert resultado["uuid"] == str(lote_centro.uuid)
        assert resultado["codigo_cadastro"] == lote_centro.codigo_cadastro
        assert resultado["nome"] == lote_centro.nome
        assert resultado["status"] is lote_centro.status
        assert resultado["empresa"] == lote_centro.empresa_id

    def test_deve_realizar_exclusao_logica_do_lote(
        self,
        lote_centro,
        usuario_ativo,
    ) -> None:
        """Deve registrar o usuário e executar a exclusão lógica do lote."""
        repository = LoteRepository()

        resultado = repository.deletar(
            usuario=usuario_ativo,
            model_lote=lote_centro,
        )

        lote_centro.refresh_from_db()

        assert resultado == (
            1,
            {"lote.Lote": 1},
        )
        assert lote_centro.deletado_por == usuario_ativo
        assert lote_centro.deletado_em is not None
        assert not Lote.objects.filter(pk=lote_centro.pk).exists()
        assert Lote.dm_objects.filter(pk=lote_centro.pk).exists()
