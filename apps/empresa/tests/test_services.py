"""Testes para os serviços de Empresa."""

from unittest.mock import Mock, patch

import pytest
from django.core.exceptions import ValidationError

from apps.empresa.constants import EmpresaErrorMessages
from apps.empresa.models import Empresa
from apps.empresa.repository.empresa_repository import (
    EmpresaRepository,
)
from apps.empresa.repository.responsavel_repository import (
    ResponsavelTecnicoRepository,
)
from apps.empresa.services.empresa_service import EmpresaService
from apps.empresa.services.responsavel_service import ResponsavelTecnicoService


class TestEmpresaService:
    """Testes para a classe EmpresaService."""

    def test_init_sem_argumentos_usa_dependencias_padrao(self):
        """Deve usar as dependências padrão quando nenhuma for informada."""
        service = EmpresaService()

        assert isinstance(service.empresa_repository, EmpresaRepository)
        assert isinstance(
            service.responsavel_tecnico_service, ResponsavelTecnicoService
        )

    def test_criar_delega_para_criar_com_responsaveis(
        self, empresa_payload_valido_com_responsaveis
    ):
        """Deve delegar a criação para criar_com_responsaveis."""
        service = EmpresaService()
        empresa = {"nome": empresa_payload_valido_com_responsaveis["nome"]}
        usuario = Mock()

        with patch.object(
            service, "criar_com_responsaveis", return_value=empresa
        ) as mock_criar_com_responsaveis:
            resultado = service.criar(
                empresa_payload_valido_com_responsaveis, usuario
            )

        assert resultado == empresa
        mock_criar_com_responsaveis.assert_called_once_with(
            {**empresa_payload_valido_com_responsaveis, "criado_por": usuario}
        )

    def test_criar_sem_usuario_define_criado_por_como_none(
        self, empresa_payload_valido_com_responsaveis
    ):
        """Deve definir criado_por como None quando não houver usuário."""
        service = EmpresaService()

        with patch.object(
            service, "criar_com_responsaveis", return_value={}
        ) as mock_criar_com_responsaveis:
            service.criar(empresa_payload_valido_com_responsaveis)

        mock_criar_com_responsaveis.assert_called_once_with(
            {**empresa_payload_valido_com_responsaveis, "criado_por": None}
        )

    @pytest.mark.django_db
    def test_criar_com_responsaveis_cria_empresa_e_responsaveis(
        self,
        empresa_payload_valido_com_responsaveis,
        responsavel_tecnico_payload_valido,
    ):
        """Deve criar a empresa e delegar a criação dos responsáveis."""
        empresa_repository = Mock(spec=EmpresaRepository)
        responsavel_tecnico_service = Mock(spec=ResponsavelTecnicoService)
        empresa_repository.criar.return_value = {"id": 1, "nome": "Empresa"}
        responsavel_tecnico_service.bulk_criar.return_value = [
            {"nome": responsavel_tecnico_payload_valido["nome"]}
        ]
        service = EmpresaService(
            empresa_repository=empresa_repository,
            responsavel_tecnico_service=responsavel_tecnico_service,
        )
        usuario = Mock()
        dados = {
            **empresa_payload_valido_com_responsaveis,
            "criado_por": usuario,
        }

        resultado = service.criar_com_responsaveis(dados)

        dados_empresa_esperados = {
            **empresa_payload_valido_com_responsaveis,
            "criado_por": usuario,
        }
        del dados_empresa_esperados["responsaveis_tecnicos"]
        empresa_repository.criar.assert_called_once_with(
            dados_empresa_esperados
        )
        responsavel_tecnico_service.bulk_criar.assert_called_once_with(
            [
                {
                    **responsavel_tecnico_payload_valido,
                    "empresa_id": 1,
                    "criado_por": usuario,
                }
            ]
        )
        assert resultado == {
            "id": 1,
            "nome": "Empresa",
            "responsaveis_tecnicos": [
                {"nome": responsavel_tecnico_payload_valido["nome"]}
            ],
        }

    def test_atualizar_delega_para_repository(self, empresa_payload_valido):
        """
        Fluxo serviço e repositório.

        Deve delegar a atualização ao repositório
        e devolver o dicionário retornado.
        """
        empresa_repository = Mock(spec=EmpresaRepository)
        instancia = Empresa(**empresa_payload_valido)
        dados_atualizados = {"nome": "Novo Nome"}
        empresa = {**empresa_payload_valido, "nome": "Novo Nome"}
        empresa_repository.atualizar.return_value = empresa
        service = EmpresaService(empresa_repository=empresa_repository)
        usuario = Mock()

        resultado = service.atualizar(instancia, dados_atualizados, usuario)

        assert resultado == empresa
        empresa_repository.atualizar.assert_called_once_with(
            instancia, {**dados_atualizados, "atualizado_por": usuario}
        )

    def test_atualizar_sem_usuario_define_atualizado_por_como_none(
        self, empresa_payload_valido
    ):
        """Deve definir atualizado_por como None quando não houver usuário."""
        empresa_repository = Mock(spec=EmpresaRepository)
        instancia = Empresa(**empresa_payload_valido)
        dados_atualizados = {"nome": "Novo Nome"}
        service = EmpresaService(empresa_repository=empresa_repository)

        service.atualizar(instancia, dados_atualizados)

        empresa_repository.atualizar.assert_called_once_with(
            instancia, {**dados_atualizados, "atualizado_por": None}
        )

    def test_deletar_delega_para_repository(self, empresa_payload_valido):
        """Deve delegar a exclusão da empresa ao repositório."""
        empresa_repository = Mock(spec=EmpresaRepository)
        instancia = Empresa(**empresa_payload_valido)
        service = EmpresaService(empresa_repository=empresa_repository)
        usuario = Mock()

        service.deletar(instancia, usuario)

        empresa_repository.deletar.assert_called_once_with(instancia, usuario)

    def test_deletar_sem_usuario_delega_usuario_como_none(
        self, empresa_payload_valido
    ):
        """Deve delegar usuário None ao repositório quando não informado."""
        empresa_repository = Mock(spec=EmpresaRepository)
        instancia = Empresa(**empresa_payload_valido)
        service = EmpresaService(empresa_repository=empresa_repository)

        service.deletar(instancia)

        empresa_repository.deletar.assert_called_once_with(instancia, None)


class TestResponsavelTecnicoService:
    """Testes para a classe ResponsavelTecnicoService."""

    def test_init_sem_repositorio_usa_repositorio_padrao(self):
        """Deve usar o repositório padrão quando nenhum for informado."""
        service = ResponsavelTecnicoService()

        assert isinstance(service.repository, ResponsavelTecnicoRepository)

    def test_bulk_criar_delega_para_repository_quando_nao_ha_duplicidade(
        self,
    ):
        """Deve delegar a criação ao repositório quando não há duplicidade."""
        repository = Mock(spec=ResponsavelTecnicoRepository)
        repository.existe_por_empresa_e_tipo.return_value = False
        dados_lista = [
            {"empresa_id": 1, "tipo": "preposto", "nome": "João"},
            {"empresa_id": 1, "tipo": "engenheiro_civil", "nome": "Maria"},
        ]
        responsaveis_criados = [{"nome": "João"}, {"nome": "Maria"}]
        repository.bulk_criar.return_value = responsaveis_criados
        service = ResponsavelTecnicoService(repository=repository)

        resultado = service.bulk_criar(dados_lista)

        assert resultado == responsaveis_criados
        assert repository.existe_por_empresa_e_tipo.call_count == 2
        repository.existe_por_empresa_e_tipo.assert_any_call(1, "preposto")
        repository.existe_por_empresa_e_tipo.assert_any_call(
            1, "engenheiro_civil"
        )
        repository.bulk_criar.assert_called_once_with(dados_lista)

    def test_bulk_criar_com_tipo_duplicado_na_empresa_levanta_validation_error(
        self,
    ):
        """Deve impedir a criação quando já existir o mesmo tipo na empresa."""
        repository = Mock(spec=ResponsavelTecnicoRepository)
        repository.existe_por_empresa_e_tipo.return_value = True
        dados_lista = [{"empresa_id": 1, "tipo": "preposto", "nome": "João"}]
        service = ResponsavelTecnicoService(repository=repository)

        with pytest.raises(ValidationError) as exc_info:
            service.bulk_criar(dados_lista)

        assert exc_info.value.message_dict == {
            "tipo": [
                EmpresaErrorMessages.RESPONSAVEL_TECNICO_TIPO_JA_CADASTRADO
            ]
        }
        repository.bulk_criar.assert_not_called()
