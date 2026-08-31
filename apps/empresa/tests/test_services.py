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

    @pytest.mark.django_db
    def test_atualizar_delega_para_repository(self, empresa_payload_valido):
        """
        Fluxo serviço e repositório.

        Deve delegar a atualização ao repositório, sincronizar os
        responsáveis técnicos e devolver o dicionário retornado.
        """
        empresa_repository = Mock(spec=EmpresaRepository)
        responsavel_tecnico_service = Mock(spec=ResponsavelTecnicoService)
        instancia = Empresa(**empresa_payload_valido)
        dados_atualizados = {"nome": "Novo Nome", "responsaveis_tecnicos": []}
        empresa = {"id": 1, "nome": "Novo Nome"}
        empresa_repository.atualizar.return_value = empresa
        responsavel_tecnico_service.sincronizar.return_value = []
        service = EmpresaService(
            empresa_repository=empresa_repository,
            responsavel_tecnico_service=responsavel_tecnico_service,
        )
        usuario = Mock()

        resultado = service.atualizar(instancia, dados_atualizados, usuario)

        assert resultado == {**empresa, "responsaveis_tecnicos": []}
        empresa_repository.atualizar.assert_called_once_with(
            instancia, {"nome": "Novo Nome", "atualizado_por": usuario}
        )

    @pytest.mark.django_db
    def test_atualizar_sem_usuario_define_atualizado_por_como_none(
        self, empresa_payload_valido
    ):
        """Deve definir atualizado_por como None quando não houver usuário."""
        empresa_repository = Mock(spec=EmpresaRepository)
        responsavel_tecnico_service = Mock(spec=ResponsavelTecnicoService)
        instancia = Empresa(**empresa_payload_valido)
        dados_atualizados = {"nome": "Novo Nome", "responsaveis_tecnicos": []}
        empresa_repository.atualizar.return_value = {
            "id": 1,
            "nome": "Novo Nome",
        }
        responsavel_tecnico_service.sincronizar.return_value = []
        service = EmpresaService(
            empresa_repository=empresa_repository,
            responsavel_tecnico_service=responsavel_tecnico_service,
        )

        service.atualizar(instancia, dados_atualizados)

        empresa_repository.atualizar.assert_called_once_with(
            instancia, {"nome": "Novo Nome", "atualizado_por": None}
        )

    @pytest.mark.django_db
    def test_atualizar_com_responsaveis_sincroniza_lista(
        self, empresa_payload_valido, responsavel_tecnico_payload_valido
    ):
        """Deve atualizar a empresa e sincronizar os responsáveis técnicos."""
        empresa_repository = Mock(spec=EmpresaRepository)
        responsavel_tecnico_service = Mock(spec=ResponsavelTecnicoService)
        empresa_repository.atualizar.return_value = {
            "id": 7,
            "nome": "Novo Nome",
        }
        responsavel_tecnico_service.sincronizar.return_value = [
            {"tipo": "preposto"}
        ]
        service = EmpresaService(
            empresa_repository=empresa_repository,
            responsavel_tecnico_service=responsavel_tecnico_service,
        )
        instancia = Empresa(**empresa_payload_valido)
        usuario = Mock()
        dados = {
            "nome": "Novo Nome",
            "responsaveis_tecnicos": [responsavel_tecnico_payload_valido],
        }

        resultado = service.atualizar(instancia, dados, usuario)

        empresa_repository.atualizar.assert_called_once_with(
            instancia, {"nome": "Novo Nome", "atualizado_por": usuario}
        )
        responsavel_tecnico_service.sincronizar.assert_called_once_with(
            empresa_id=7,
            dados_lista=[responsavel_tecnico_payload_valido],
            usuario=usuario,
        )
        assert resultado == {
            "id": 7,
            "nome": "Novo Nome",
            "responsaveis_tecnicos": [{"tipo": "preposto"}],
        }

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

    def test_sincronizar_atualiza_por_uuid_cria_sem_uuid_e_remove_ausentes(
        self,
    ):
        """Deve atualizar por uuid, criar itens sem uuid e remover ausentes."""
        repository = Mock(spec=ResponsavelTecnicoRepository)
        preposto = Mock(id=1, uuid="uuid-preposto", tipo="preposto")
        engenheiro_civil = Mock(
            id=2, uuid="uuid-engenheiro", tipo="engenheiro_civil"
        )
        repository.listar_por_empresa.return_value = [
            preposto,
            engenheiro_civil,
        ]
        repository.bulk_atualizar.return_value = [
            {"tipo": "preposto", "nome": "Preposto Novo"}
        ]
        repository.bulk_criar.return_value = [
            {"tipo": "engenheiro_eletricista", "nome": "Eletricista"}
        ]
        service = ResponsavelTecnicoService(repository=repository)
        usuario = Mock()
        dados_lista = [
            {
                "uuid": "uuid-preposto",
                "tipo": "preposto",
                "nome": "Preposto Novo",
            },
            {"tipo": "engenheiro_eletricista", "nome": "Eletricista"},
        ]

        resultado = service.sincronizar(1, dados_lista, usuario)

        repository.bulk_atualizar.assert_called_once_with(
            [
                {
                    "uuid": "uuid-preposto",
                    "tipo": "preposto",
                    "nome": "Preposto Novo",
                    "id": 1,
                    "atualizado_por": usuario,
                }
            ]
        )
        repository.bulk_criar.assert_called_once_with(
            [
                {
                    "tipo": "engenheiro_eletricista",
                    "nome": "Eletricista",
                    "empresa_id": 1,
                    "criado_por": usuario,
                }
            ]
        )
        repository.remover.assert_called_once_with([engenheiro_civil], usuario)
        assert resultado == [
            {"tipo": "preposto", "nome": "Preposto Novo"},
            {"tipo": "engenheiro_eletricista", "nome": "Eletricista"},
        ]

    def test_sincronizar_nao_cria_nem_remove_quando_todos_tem_uuid(self):
        """Não deve criar nem remover quando todos os itens têm uuid."""
        repository = Mock(spec=ResponsavelTecnicoRepository)
        preposto = Mock(id=1, uuid="uuid-preposto", tipo="preposto")
        repository.listar_por_empresa.return_value = [preposto]
        repository.bulk_atualizar.return_value = [
            {"tipo": "preposto", "nome": "Preposto Novo"}
        ]
        service = ResponsavelTecnicoService(repository=repository)

        resultado = service.sincronizar(
            1,
            [
                {
                    "uuid": "uuid-preposto",
                    "tipo": "preposto",
                    "nome": "Preposto Novo",
                }
            ],
            None,
        )

        repository.remover.assert_not_called()
        repository.bulk_criar.assert_not_called()
        assert resultado == [{"tipo": "preposto", "nome": "Preposto Novo"}]

    def test_sincronizar_com_uuid_desconhecido_levanta_validation_error(self):
        """Deve falhar quando um uuid informado não pertence à empresa."""
        repository = Mock(spec=ResponsavelTecnicoRepository)
        repository.listar_por_empresa.return_value = []
        service = ResponsavelTecnicoService(repository=repository)

        with pytest.raises(ValidationError) as exc_info:
            service.sincronizar(
                1, [{"uuid": "uuid-inexistente", "tipo": "preposto"}], None
            )

        assert exc_info.value.message_dict == {
            "responsaveis_tecnicos": [
                EmpresaErrorMessages.RESPONSAVEL_TECNICO_NAO_ENCONTRADO
            ]
        }
        repository.bulk_atualizar.assert_not_called()
        repository.bulk_criar.assert_not_called()
        repository.remover.assert_not_called()
