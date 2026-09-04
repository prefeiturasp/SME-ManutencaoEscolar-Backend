"""Testes para os serviços de Empresa."""

from unittest.mock import Mock, patch
from uuid import uuid4

import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.core.constants import TipoArquivo
from apps.core.services.anexo_service import AnexoService
from apps.empresa.constants import EmpresaErrorMessages
from apps.empresa.models import (
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
from apps.empresa.services.anexo_service import (
    AnexoResponsavelTecnicoService,
)
from apps.empresa.services.empresa_service import EmpresaService
from apps.empresa.services.responsavel_service import ResponsavelTecnicoService


class TestAnexoResponsavelTecnicoService:
    """Testes para o upload dos anexos de responsáveis técnicos."""

    @pytest.mark.django_db
    def test_sincronizar_arquivos_prepara_e_persiste_anexo(
        self, usuario_ativo
    ):
        """Deve preparar os metadados e delegar a persistência do anexo."""
        repository = Mock(spec=AnexoResponsavelTecnicoRepository)
        repository.criar.return_value = {
            "uuid": "uuid-anexo",
            "nome": "art.pdf",
            "arquivo_url": "https://minio.local/art.pdf",
        }
        anexo_service = Mock(spec=AnexoService)
        service = AnexoResponsavelTecnicoService(
            repository=repository,
            anexo_service=anexo_service,
        )
        responsavel = ResponsavelTecnico(id=1)
        arquivo = SimpleUploadedFile(
            "art.pdf", b"conteudo", content_type="application/pdf"
        )
        arquivo.name = "uuid-gerado.pdf"
        anexo_service.validar_e_preparar_anexo.return_value = {
            "nome_original": "art.pdf",
            "tipo": TipoArquivo.DOCUMENTO,
            "tipo_mime": "application/pdf",
            "tamanho_bytes": len(b"conteudo"),
            "arquivo": arquivo,
            "usuario_id": usuario_ativo.id,
        }
        with patch(
            "apps.empresa.services.anexo_service."
            "ResponsavelTecnico.objects.get",
            return_value=responsavel,
        ):
            resultado = service.sincronizar_arquivos(
                responsavel_uuid=responsavel.uuid,
                arquivos=[{"arquivo": arquivo}],
                usuario=usuario_ativo,
            )

        anexo_service.validar_e_preparar_anexo.assert_called_once_with(
            arquivo=arquivo,
            id_usuario=usuario_ativo.id,
        )
        anexo = repository.criar.call_args.args[0]
        assert anexo.nome_original == "art.pdf"
        assert anexo.tipo == TipoArquivo.DOCUMENTO
        assert anexo.tipo_mime == arquivo.content_type
        assert anexo.tamanho_bytes == len(b"conteudo")
        assert anexo.arquivo.name == "uuid-gerado.pdf"
        assert anexo.criado_por == usuario_ativo
        assert resultado == [
            {
                "uuid": "uuid-anexo",
                "nome": "art.pdf",
                "arquivo_url": "https://minio.local/art.pdf",
            }
        ]
        repository.excluir_nao_preservados.assert_called_once_with(
            responsavel_id=responsavel.id,
            uuids_preservados=["uuid-anexo"],
        )

    @pytest.mark.django_db
    def test_sincronizar_arquivos_preserva_sem_retornar_anexo_existente(self):
        """Deve preservar sem retornar o anexo cujo UUID está no payload."""
        uuid = uuid4()
        repository = Mock(spec=AnexoResponsavelTecnicoRepository)
        service = AnexoResponsavelTecnicoService(repository=repository)

        responsavel = Mock(id=1)
        with patch.object(
            ResponsavelTecnico.objects,
            "get",
            return_value=responsavel,
        ):
            resultado = service.sincronizar_arquivos(
                responsavel_uuid=uuid4(),
                arquivos=[{"uuid": uuid}],
            )

        assert resultado == []
        repository.excluir_nao_preservados.assert_called_once_with(
            responsavel_id=1,
            uuids_preservados=[uuid],
        )


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
        responsaveis_criados = [
            {"uuid": "uuid-preposto", "tipo": "preposto", "nome": "João"},
            {
                "uuid": "uuid-engenheiro",
                "tipo": "engenheiro_civil",
                "nome": "Maria",
            },
        ]
        repository.bulk_criar.return_value = responsaveis_criados
        anexo_service = Mock(spec=AnexoResponsavelTecnicoService)
        anexo_service.sincronizar_arquivos.return_value = []
        service = ResponsavelTecnicoService(
            repository=repository,
            anexo_service=anexo_service,
        )

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

    def test_bulk_criar_salva_arquivos_para_cada_responsavel(self):
        """Deve encaminhar os arquivos após criar o responsável técnico."""
        repository = Mock(spec=ResponsavelTecnicoRepository)
        repository.existe_por_empresa_e_tipo.return_value = False
        usuario = Mock()
        arquivo = Mock()
        repository.bulk_criar.return_value = [
            {"uuid": "uuid-preposto", "tipo": "preposto", "nome": "João"}
        ]
        anexo_service = Mock(spec=AnexoResponsavelTecnicoService)
        anexo_service.sincronizar_arquivos.return_value = [{"nome": "art.pdf"}]
        service = ResponsavelTecnicoService(
            repository=repository,
            anexo_service=anexo_service,
        )

        resultado = service.bulk_criar(
            [
                {
                    "empresa_id": 1,
                    "tipo": "preposto",
                    "nome": "João",
                    "criado_por": usuario,
                    "anexos": [{"arquivo": arquivo}],
                }
            ]
        )

        repository.bulk_criar.assert_called_once_with(
            [
                {
                    "empresa_id": 1,
                    "tipo": "preposto",
                    "nome": "João",
                    "criado_por": usuario,
                }
            ]
        )
        anexo_service.sincronizar_arquivos.assert_called_once_with(
            responsavel_uuid="uuid-preposto",
            arquivos=[{"arquivo": arquivo}],
            usuario=usuario,
        )
        assert resultado == [
            {
                "uuid": "uuid-preposto",
                "tipo": "preposto",
                "nome": "João",
                "anexos": [{"nome": "art.pdf"}],
            }
        ]

    def test_bulk_criar_sincroniza_lista_vazia_quando_nao_tem_arquivos(
        self,
    ):
        """Deve sincronizar lista vazia para remover anexos ausentes."""
        repository = Mock(spec=ResponsavelTecnicoRepository)
        repository.existe_por_empresa_e_tipo.return_value = False
        repository.bulk_criar.return_value = [
            {"uuid": "uuid-preposto", "tipo": "preposto", "nome": "João"}
        ]
        anexo_service = Mock(spec=AnexoResponsavelTecnicoService)
        anexo_service.sincronizar_arquivos.return_value = []
        service = ResponsavelTecnicoService(
            repository=repository,
            anexo_service=anexo_service,
        )

        resultado = service.bulk_criar(
            [{"empresa_id": 1, "tipo": "preposto", "nome": "João"}]
        )

        anexo_service.sincronizar_arquivos.assert_called_once_with(
            responsavel_uuid="uuid-preposto",
            arquivos=[],
            usuario=None,
        )
        assert resultado == [
            {
                "uuid": "uuid-preposto",
                "tipo": "preposto",
                "nome": "João",
                "anexos": [],
            }
        ]

    def test_salvar_anexos_processa_lista_vazia_para_excluir_existentes(self):
        """Deve sincronizar uma lista vazia para excluir anexos existentes."""
        anexo_service = Mock(spec=AnexoResponsavelTecnicoService)
        anexo_service.sincronizar_arquivos.return_value = [{"nome": "art.pdf"}]
        service = ResponsavelTecnicoService(anexo_service=anexo_service)
        responsaveis = [
            {"uuid": "uuid-preposto", "tipo": "preposto"},
            {"uuid": "uuid-engenheiro", "tipo": "engenheiro_civil"},
        ]

        resultado = service._salvar_anexos_dos_responsaveis(
            responsaveis=responsaveis,
            arquivos_por_tipo={
                "preposto": [{"arquivo": Mock()}],
                "engenheiro_civil": [],
            },
            usuario=None,
        )

        assert anexo_service.sincronizar_arquivos.call_count == 2
        anexo_service.sincronizar_arquivos.assert_any_call(
            responsavel_uuid="uuid-engenheiro",
            arquivos=[],
            usuario=None,
        )
        assert resultado[0]["anexos"] == [{"nome": "art.pdf"}]
        assert resultado[1]["anexos"] == [{"nome": "art.pdf"}]

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
            {
                "uuid": "uuid-preposto",
                "tipo": "preposto",
                "nome": "Preposto Novo",
            }
        ]
        repository.bulk_criar.return_value = [
            {
                "uuid": "uuid-eletricista",
                "tipo": "engenheiro_eletricista",
                "nome": "Eletricista",
            }
        ]
        anexo_service = Mock(spec=AnexoResponsavelTecnicoService)
        anexo_service.sincronizar_arquivos.return_value = []
        service = ResponsavelTecnicoService(
            repository=repository,
            anexo_service=anexo_service,
        )
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
            {
                "uuid": "uuid-preposto",
                "tipo": "preposto",
                "nome": "Preposto Novo",
                "anexos": [],
            },
            {
                "uuid": "uuid-eletricista",
                "tipo": "engenheiro_eletricista",
                "nome": "Eletricista",
                "anexos": [],
            },
        ]

    def test_sincronizar_nao_cria_nem_remove_quando_todos_tem_uuid(self):
        """Não deve criar nem remover quando todos os itens têm uuid."""
        repository = Mock(spec=ResponsavelTecnicoRepository)
        preposto = Mock(id=1, uuid="uuid-preposto", tipo="preposto")
        repository.listar_por_empresa.return_value = [preposto]
        repository.bulk_atualizar.return_value = [
            {
                "uuid": "uuid-preposto",
                "tipo": "preposto",
                "nome": "Preposto Novo",
            }
        ]
        anexo_service = Mock(spec=AnexoResponsavelTecnicoService)
        anexo_service.sincronizar_arquivos.return_value = []
        service = ResponsavelTecnicoService(
            repository=repository,
            anexo_service=anexo_service,
        )

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
        assert resultado == [
            {
                "uuid": "uuid-preposto",
                "tipo": "preposto",
                "nome": "Preposto Novo",
                "anexos": [],
            }
        ]

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
