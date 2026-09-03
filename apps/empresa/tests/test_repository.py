"""Testes para o repositório de Empresa."""

from unittest.mock import Mock, patch

import pytest
from django.core.exceptions import ValidationError
from django.db.models.fields.files import FieldFile

from apps.empresa.exceptions import EmpresaCnpjDuplicadoError
from apps.empresa.models import (
    AnexoResponsavelTecnico,
    Empresa,
    ResponsavelTecnico,
)
from apps.empresa.repository.anexo_repository import (
    AnexoResponsavelTecnicoRepository,
)
from apps.empresa.repository.empresa_repository import (
    EmpresaRepository,
)
from apps.empresa.repository.responsavel_repository import (
    ResponsavelTecnicoRepository,
)


class TestEmpresaRepository:
    """Testes para o repositório de empresas."""

    def test_criar_chama_full_clean_e_save(self, empresa_payload_valido):
        """
        Retorno dos dados da empresa.

        Deve retornar os dados em formato de dicionário.
        """
        repository = EmpresaRepository()

        with (
            patch.object(Empresa, "full_clean") as mock_full_clean,
            patch.object(Empresa, "save") as mock_save,
        ):
            empresa = repository.criar(empresa_payload_valido)

        assert isinstance(empresa, dict)
        assert empresa["nome"] == empresa_payload_valido["nome"]
        assert empresa["cnpj"] == empresa_payload_valido["cnpj"]
        mock_full_clean.assert_called_once_with()
        mock_save.assert_called_once_with()

    def test_atualizar_altera_campos_chama_full_clean_e_save(
        self, empresa_payload_valido
    ):
        """
        Retorno dos dados atualizados da empresa.

        Deve alterar os campos informados e retornar em dicionário.
        """
        repository = EmpresaRepository()
        empresa = Empresa(**empresa_payload_valido)

        with (
            patch.object(Empresa, "full_clean") as mock_full_clean,
            patch.object(Empresa, "save") as mock_save,
        ):
            resultado = repository.atualizar(empresa, {"nome": "Novo Nome"})

        assert isinstance(resultado, dict)
        assert resultado["nome"] == "Novo Nome"
        assert empresa.nome == "Novo Nome"
        mock_full_clean.assert_called_once_with()
        mock_save.assert_called_once_with()

    @pytest.mark.django_db
    def test_criar_com_cnpj_duplicado_levanta_erro_de_dominio(
        self, empresa_payload_valido
    ):
        """Deve traduzir a violação de unicidade do CNPJ em erro de domínio."""
        repository = EmpresaRepository()
        repository.criar(empresa_payload_valido)

        with pytest.raises(EmpresaCnpjDuplicadoError):
            repository.criar(empresa_payload_valido)

    def test_criar_com_erro_de_validacao_nao_relacionado_a_cnpj_propaga_erro(
        self, empresa_payload_valido
    ):
        """Deve propagar o erro original quando não for de CNPJ duplicado."""
        repository = EmpresaRepository()
        erro_validacao = ValidationError({"nome": ["campo obrigatório"]})

        with (
            patch.object(Empresa, "full_clean", side_effect=erro_validacao),
            pytest.raises(ValidationError) as exc_info,
        ):
            repository.criar(empresa_payload_valido)

        assert exc_info.value is erro_validacao

    @pytest.mark.django_db
    def test_atualizar_com_cnpj_duplicado_levanta_erro_de_dominio(
        self, empresa_payload_valido
    ):
        """Deve traduzir a violação de unicidade do CNPJ ao atualizar."""
        repository = EmpresaRepository()
        repository.criar(empresa_payload_valido)

        outra_empresa = repository.criar(
            {**empresa_payload_valido, "cnpj": "43210987654321"}
        )
        empresa = Empresa.objects.get(uuid=outra_empresa["uuid"])

        with pytest.raises(EmpresaCnpjDuplicadoError):
            repository.atualizar(
                empresa, {"cnpj": empresa_payload_valido["cnpj"]}
            )

    @pytest.mark.django_db
    def test_deletar_marca_empresa_como_deletada(
        self, empresa_payload_valido, usuario_ativo
    ):
        """Deve definir deletado_em e deletado_por e persistir a alteração."""
        repository = EmpresaRepository()
        dados = repository.criar(empresa_payload_valido)
        empresa = Empresa.dm_objects.get(uuid=dados["uuid"])

        repository.deletar(empresa, usuario_ativo)

        empresa.refresh_from_db()
        assert empresa.deletado_em is not None
        assert empresa.deletado_por == usuario_ativo
        assert not Empresa.objects.filter(uuid=empresa.uuid).exists()

    @pytest.mark.django_db
    def test_deletar_sem_usuario_define_deletado_por_como_none(
        self, empresa_payload_valido
    ):
        """Deve definir deletado_por como None quando não houver usuário."""
        repository = EmpresaRepository()
        dados = repository.criar(empresa_payload_valido)
        empresa = Empresa.dm_objects.get(uuid=dados["uuid"])

        repository.deletar(empresa)

        empresa.refresh_from_db()
        assert empresa.deletado_em is not None
        assert empresa.deletado_por is None


class TestAnexoResponsavelTecnicoRepository:
    """Testes para o repositório de anexos de responsáveis técnicos."""

    def test_bulk_criar_persiste_e_serializa_anexos(self):
        """Deve persistir os anexos e devolver seus dados serializados."""
        repository = AnexoResponsavelTecnicoRepository()
        anexo = AnexoResponsavelTecnico(
            nome="art.pdf",
            arquivo_url="https://minio.local/art.pdf",
        )

        with patch.object(
            AnexoResponsavelTecnico.objects,
            "bulk_create",
            return_value=[anexo],
        ) as bulk_create:
            resultado = repository.bulk_criar([anexo])

        bulk_create.assert_called_once_with([anexo])
        assert resultado == [
            {
                "uuid": str(anexo.uuid),
                "nome": "art.pdf",
                "arquivo_url": "https://minio.local/art.pdf",
            }
        ]

    def test_excluir_nao_preservados_remove_arquivos_e_registros(self):
        """Deve excluir do storage e banco os anexos não preservados."""
        repository = AnexoResponsavelTecnicoRepository()
        uuid_preservado = AnexoResponsavelTecnico().uuid
        queryset = Mock()
        queryset_filtrado = Mock()
        anexo = Mock(spec=AnexoResponsavelTecnico)
        queryset.exclude.return_value = queryset_filtrado
        queryset_filtrado.__iter__ = Mock(return_value=iter([anexo]))
        queryset_filtrado.delete.return_value = (
            1,
            {"empresa.AnexoResponsavelTecnico": 1},
        )

        with patch.object(
            AnexoResponsavelTecnico.objects,
            "filter",
            return_value=queryset,
        ) as filter_mock:
            repository.excluir_nao_preservados(
                responsavel_id=1,
                uuids_preservados=[uuid_preservado],
            )

        filter_mock.assert_called_once_with(responsavel_tecnico_id=1)
        queryset.exclude.assert_called_once_with(uuid__in=[uuid_preservado])
        anexo.arquivo.delete.assert_called_once_with(save=False)
        queryset_filtrado.delete.assert_called_once_with()

    @pytest.mark.django_db
    def test_excluir_nao_preservados_remove_fisicamente_do_banco(
        self, responsavel_payload_valido
    ):
        """Deve remover o registro inclusive do manager sem filtro."""
        responsavel = ResponsavelTecnico.objects.create(
            **responsavel_payload_valido
        )
        anexo = AnexoResponsavelTecnico.objects.create(
            responsavel_tecnico=responsavel,
            nome="art.pdf",
            arquivo="anexos_responsaveis_tecnicos/art.pdf",
        )

        with patch.object(FieldFile, "delete") as arquivo_delete:
            AnexoResponsavelTecnicoRepository().excluir_nao_preservados(
                responsavel_id=responsavel.id,
                uuids_preservados=[],
            )

        arquivo_delete.assert_called_once_with(save=False)
        assert not AnexoResponsavelTecnico.dm_objects.filter(
            pk=anexo.pk
        ).exists()


class TestResponsavelTecnicoRepository:
    """Testes para o repositório de responsável técnico."""

    @pytest.mark.django_db
    def test_bulk_criar_persiste_responsaveis_no_banco(
        self, responsavel_payload_valido
    ):
        """Deve persistir múltiplos responsáveis em uma única operação."""
        repository = ResponsavelTecnicoRepository()
        outro_payload = {
            **responsavel_payload_valido,
            "tipo": "engenheiro_civil",
            "email": "outro.responsavel@email.com",
        }

        criados = repository.bulk_criar(
            [responsavel_payload_valido, outro_payload]
        )

        assert len(criados) == 2
        assert all(isinstance(r, dict) for r in criados)
        assert ResponsavelTecnico.objects.count() == 2
        assert {r["tipo"] for r in criados} == {"preposto", "engenheiro_civil"}

    @pytest.mark.django_db
    def test_bulk_atualizar_altera_campos_dos_responsaveis(
        self, responsavel_payload_valido
    ):
        """Deve aplicar os campos informados no responsável identificado."""
        repository = ResponsavelTecnicoRepository()
        (criado,) = repository.bulk_criar([responsavel_payload_valido])
        responsavel_id = ResponsavelTecnico.objects.get(uuid=criado["uuid"]).id

        atualizados = repository.bulk_atualizar(
            [
                {
                    "id": responsavel_id,
                    "nome": "Nome Atualizado",
                    "email": "atualizado@email.com",
                }
            ]
        )

        assert atualizados[0]["nome"] == "Nome Atualizado"
        responsavel = ResponsavelTecnico.objects.get(pk=responsavel_id)
        assert responsavel.nome == "Nome Atualizado"
        assert responsavel.email == "atualizado@email.com"

    @pytest.mark.django_db
    def test_bulk_atualizar_atualiza_atualizado_em_quando_ha_mudanca(
        self, responsavel_payload_valido
    ):
        """Deve atualizar ``atualizado_em`` quando algum campo muda."""
        repository = ResponsavelTecnicoRepository()
        (criado,) = repository.bulk_criar([responsavel_payload_valido])
        responsavel_id = ResponsavelTecnico.objects.get(uuid=criado["uuid"]).id
        atualizado_em_original = ResponsavelTecnico.objects.get(
            pk=responsavel_id
        ).atualizado_em

        repository.bulk_atualizar(
            [{"id": responsavel_id, "nome": "Nome Atualizado"}]
        )

        responsavel = ResponsavelTecnico.objects.get(pk=responsavel_id)
        assert responsavel.atualizado_em > atualizado_em_original

    @pytest.mark.django_db
    def test_bulk_atualizar_nao_salva_quando_nada_muda(
        self, responsavel_payload_valido
    ):
        """Não deve tocar o registro quando nenhum campo é alterado."""
        repository = ResponsavelTecnicoRepository()
        (criado,) = repository.bulk_criar([responsavel_payload_valido])
        responsavel = ResponsavelTecnico.objects.get(uuid=criado["uuid"])
        atualizado_em_original = responsavel.atualizado_em

        repository.bulk_atualizar(
            [
                {
                    "id": responsavel.id,
                    "nome": responsavel.nome,
                    "email": responsavel.email,
                    "tipo": responsavel.tipo,
                }
            ]
        )

        responsavel.refresh_from_db()
        assert responsavel.atualizado_em == atualizado_em_original

    @pytest.mark.django_db
    def test_listar_por_empresa_retorna_responsaveis_da_empresa(
        self, responsavel_payload_valido
    ):
        """Deve retornar as instâncias dos responsáveis da empresa."""
        repository = ResponsavelTecnicoRepository()
        repository.bulk_criar(
            [
                responsavel_payload_valido,
                {
                    **responsavel_payload_valido,
                    "tipo": "engenheiro_civil",
                    "email": "engenheiro@email.com",
                },
            ]
        )

        resultado = repository.listar_por_empresa(
            responsavel_payload_valido["empresa"].id
        )

        assert {responsavel.tipo for responsavel in resultado} == {
            "preposto",
            "engenheiro_civil",
        }

    @pytest.mark.django_db
    def test_remover_marca_responsaveis_como_deletados(
        self, responsavel_payload_valido, usuario_ativo
    ):
        """Deve aplicar soft delete e registrar o usuário responsável."""
        repository = ResponsavelTecnicoRepository()
        repository.bulk_criar([responsavel_payload_valido])
        responsavel = ResponsavelTecnico.objects.get()

        repository.remover([responsavel], usuario_ativo)

        responsavel.refresh_from_db()
        assert responsavel.deletado_em is not None
        assert responsavel.deletado_por == usuario_ativo
        assert not ResponsavelTecnico.objects.filter(
            pk=responsavel.pk
        ).exists()

    @pytest.mark.django_db
    def test_existe_por_empresa_e_tipo_retorna_true_quando_ja_cadastrado(
        self, responsavel_payload_valido
    ):
        """Deve retornar True quando já houver responsável do tipo."""
        repository = ResponsavelTecnicoRepository()
        repository.bulk_criar([responsavel_payload_valido])

        existe = repository.existe_por_empresa_e_tipo(
            responsavel_payload_valido["empresa"].id,
            responsavel_payload_valido["tipo"],
        )

        assert existe is True

    @pytest.mark.django_db
    def test_existe_por_empresa_e_tipo_retorna_false_quando_nao_cadastrado(
        self, responsavel_payload_valido
    ):
        """Deve retornar False quando não houver responsável do tipo."""
        repository = ResponsavelTecnicoRepository()

        existe = repository.existe_por_empresa_e_tipo(
            responsavel_payload_valido["empresa"].id,
            responsavel_payload_valido["tipo"],
        )

        assert existe is False
