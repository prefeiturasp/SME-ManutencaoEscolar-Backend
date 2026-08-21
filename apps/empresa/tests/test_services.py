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

    def test_init_sem_repositorio_usa_repositorio_padrao(self):
        """Deve usar o repositório padrão quando nenhum for informado."""
        service = EmpresaService()

        assert isinstance(service.repository, EmpresaRepository)

    def test_criar_delega_para_repository(self, empresa_payload_valido):
        """
        Fluxo serviço e repositório.

        Deve delegar a criação ao repositório
        e devolver o dicionário retornado.
        """
        repository = Mock(spec=EmpresaRepository)
        empresa = {"nome": empresa_payload_valido["nome"]}
        repository.criar.return_value = empresa
        service = EmpresaService(repository=repository)
        usuario = Mock()

        resultado = service.criar(empresa_payload_valido, usuario)

        assert resultado == empresa
        repository.criar.assert_called_once_with(
            {**empresa_payload_valido, "criado_por": usuario}
        )

    def test_criar_sem_usuario_define_criado_por_como_none(
        self, empresa_payload_valido
    ):
        """Deve definir criado_por como None quando não houver usuário."""
        repository = Mock(spec=EmpresaRepository)
        service = EmpresaService(repository=repository)

        service.criar(empresa_payload_valido)

        repository.criar.assert_called_once_with(
            {**empresa_payload_valido, "criado_por": None}
        )

    def test_criar_retorna_instancia_de_empresa(self, empresa_payload_valido):
        """Deve devolver o dicionário retornado pelo repositório."""
        service = EmpresaService()
        empresa = {"nome": empresa_payload_valido["nome"]}

        with patch.object(
            EmpresaRepository, "criar", return_value=empresa
        ) as mock_create:
            resultado = service.criar(empresa_payload_valido)

        assert resultado == empresa
        mock_create.assert_called_once_with(
            {**empresa_payload_valido, "criado_por": None}
        )

    def test_atualizar_delega_para_repository(self, empresa_payload_valido):
        """
        Fluxo serviço e repositório.

        Deve delegar a atualização ao repositório
        e devolver o dicionário retornado.
        """
        repository = Mock(spec=EmpresaRepository)
        instancia = Empresa(**empresa_payload_valido)
        dados_atualizados = {"nome": "Novo Nome"}
        empresa = {**empresa_payload_valido, "nome": "Novo Nome"}
        repository.atualizar.return_value = empresa
        service = EmpresaService(repository=repository)
        usuario = Mock()

        resultado = service.atualizar(instancia, dados_atualizados, usuario)

        assert resultado == empresa
        repository.atualizar.assert_called_once_with(
            instancia, {**dados_atualizados, "atualizado_por": usuario}
        )

    def test_atualizar_sem_usuario_define_atualizado_por_como_none(
        self, empresa_payload_valido
    ):
        """Deve definir atualizado_por como None quando não houver usuário."""
        repository = Mock(spec=EmpresaRepository)
        instancia = Empresa(**empresa_payload_valido)
        dados_atualizados = {"nome": "Novo Nome"}
        service = EmpresaService(repository=repository)

        service.atualizar(instancia, dados_atualizados)

        repository.atualizar.assert_called_once_with(
            instancia, {**dados_atualizados, "atualizado_por": None}
        )

    def test_deletar_delega_para_repository(self, empresa_payload_valido):
        """Deve delegar a exclusão da empresa ao repositório."""
        repository = Mock(spec=EmpresaRepository)
        instancia = Empresa(**empresa_payload_valido)
        service = EmpresaService(repository=repository)
        usuario = Mock()

        service.deletar(instancia, usuario)

        repository.deletar.assert_called_once_with(instancia, usuario)

    def test_deletar_sem_usuario_delega_usuario_como_none(
        self, empresa_payload_valido
    ):
        """Deve delegar usuário None ao repositório quando não informado."""
        repository = Mock(spec=EmpresaRepository)
        instancia = Empresa(**empresa_payload_valido)
        service = EmpresaService(repository=repository)

        service.deletar(instancia)

        repository.deletar.assert_called_once_with(instancia, None)


class TestResponsavelTecnicoService:
    """Testes para a classe ResponsavelTecnicoService."""

    def test_init_sem_repositorio_usa_repositorio_padrao(self):
        """Deve usar o repositório padrão quando nenhum for informado."""
        service = ResponsavelTecnicoService()

        assert isinstance(service.repository, ResponsavelTecnicoRepository)

    def test_criar_delega_para_repository(self, responsavel_payload_valido):
        """Deve delegar a criação ao repositório quando não há duplicidade."""
        repository = Mock(spec=ResponsavelTecnicoRepository)
        repository.existe_por_empresa_e_tipo.return_value = False
        responsavel = {"nome": responsavel_payload_valido["nome"]}
        repository.criar.return_value = responsavel
        service = ResponsavelTecnicoService(repository=repository)
        usuario = Mock()

        resultado = service.criar(responsavel_payload_valido, usuario)

        assert resultado == responsavel
        repository.existe_por_empresa_e_tipo.assert_called_once_with(
            responsavel_payload_valido["empresa"].id,
            responsavel_payload_valido["tipo"],
        )
        repository.criar.assert_called_once_with(
            {**responsavel_payload_valido, "criado_por": usuario}
        )

    def test_criar_sem_usuario_define_criado_por_como_none(
        self, responsavel_payload_valido
    ):
        """Deve definir criado_por como None quando não houver usuário."""
        repository = Mock(spec=ResponsavelTecnicoRepository)
        repository.existe_por_empresa_e_tipo.return_value = False
        service = ResponsavelTecnicoService(repository=repository)

        service.criar(responsavel_payload_valido)

        repository.criar.assert_called_once_with(
            {**responsavel_payload_valido, "criado_por": None}
        )

    def test_criar_com_tipo_duplicado_na_empresa_levanta_validation_error(
        self, responsavel_payload_valido
    ):
        """Deve impedir a criação quando já existir o mesmo tipo na empresa."""
        repository = Mock(spec=ResponsavelTecnicoRepository)
        repository.existe_por_empresa_e_tipo.return_value = True
        service = ResponsavelTecnicoService(repository=repository)

        with pytest.raises(ValidationError) as exc_info:
            service.criar(responsavel_payload_valido)

        assert exc_info.value.message_dict == {
            "tipo": [
                EmpresaErrorMessages.RESPONSAVEL_TECNICO_TIPO_JA_CADASTRADO
            ]
        }
        repository.criar.assert_not_called()
