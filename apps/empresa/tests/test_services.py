"""Testes para os serviços de Empresa."""

from unittest.mock import Mock, patch

from apps.empresa.models import Empresa
from apps.empresa.repository.empresa_repository import (
    EmpresaRepository,
)
from apps.empresa.services.empresa_service import EmpresaService


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
