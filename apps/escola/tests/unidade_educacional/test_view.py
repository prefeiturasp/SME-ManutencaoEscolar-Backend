"""Teste da view de Unidade Educacional."""

import uuid

import pytest
from rest_framework import status

from apps.escola.models import (
    Unidadeeducacional,
)

pytestmark = pytest.mark.django_db


class TestUnidadeEducacionalViewSet:
    """Testes do ViewSet de unidades educacionais."""

    url = "/api/v1/unidades-educacionais/"

    def test_deve_listar_unidades_educacionais(
        self,
        api_cliente,
        unidade_educacional_emef,
        unidade_educacional_inativa_emef,
        unidade_educacional_cemei,
    ):
        """Deve retornar as unidades educacionais cadastradas."""
        resposta = api_cliente.get(self.url)

        assert resposta.status_code == status.HTTP_200_OK

        resultados = resposta.data["results"]

        assert len(resultados) == 3
        assert {resultado["codigo_eol"] for resultado in resultados} == {
            unidade_educacional_emef.codigo_eol,
            unidade_educacional_inativa_emef.codigo_eol,
            unidade_educacional_cemei.codigo_eol,
        }

    def test_deve_buscar_unidade_educacional_por_uuid(
        self,
        api_cliente,
        unidade_educacional_emef,
    ):
        """Deve retornar uma unidade educacional pelo UUID."""
        resposta = api_cliente.get(
            f"{self.url}{unidade_educacional_emef.uuid}/",
        )

        assert resposta.status_code == status.HTTP_200_OK

        resultado = resposta.data

        assert resultado["id"] == unidade_educacional_emef.id
        assert resultado["uuid"] == str(
            unidade_educacional_emef.uuid,
        )
        assert resultado["codigo_eol"] == (unidade_educacional_emef.codigo_eol)
        assert resultado["nome"] == unidade_educacional_emef.nome
        assert resultado["status"] == unidade_educacional_emef.status

    def test_deve_filtrar_por_codigo_eol(
        self,
        api_cliente,
        unidade_educacional_emef,
    ):
        """Deve filtrar unidades pelo código EOL."""
        resposta = api_cliente.get(
            self.url,
            {"codigo_eol": unidade_educacional_emef.codigo_eol},
        )

        assert resposta.status_code == status.HTTP_200_OK

        resultados = resposta.data["results"]

        assert len(resultados) == 1
        assert resultados[0]["uuid"] == str(
            unidade_educacional_emef.uuid,
        )

    def test_deve_filtrar_por_status_ativo(
        self,
        api_cliente,
        unidade_educacional_emef,
        unidade_educacional_inativa_emef,
        unidade_educacional_cemei,
    ):
        """Deve retornar somente unidades ativas."""
        resposta = api_cliente.get(
            self.url,
            {"status": "true"},
        )

        assert resposta.status_code == status.HTTP_200_OK

        resultados = resposta.data["results"]

        assert len(resultados) == 2
        assert {resultado["uuid"] for resultado in resultados} == {
            str(unidade_educacional_emef.uuid),
            str(unidade_educacional_cemei.uuid),
        }

    def test_deve_filtrar_por_status_inativo(
        self,
        api_cliente,
        unidade_educacional_inativa_emef,
        unidade_educacional_emef,
        unidade_educacional_cemei,
    ):
        """Deve retornar somente unidades inativas."""
        resposta = api_cliente.get(
            self.url,
            {"status": "false"},
        )

        assert resposta.status_code == status.HTTP_200_OK

        resultados = resposta.data["results"]

        assert len(resultados) == 1
        assert resultados[0]["uuid"] == str(
            unidade_educacional_inativa_emef.uuid,
        )
        assert resultados[0]["status"] is False

    def test_deve_filtrar_por_tipo_escola(
        self,
        api_cliente,
        unidade_educacional_emef,
        unidade_educacional_inativa_emef,
        tipo_escola_emef,
    ):
        """Deve filtrar unidades pelo tipo de escola."""
        resposta = api_cliente.get(
            self.url,
            {"tipo_escola": str(tipo_escola_emef.uuid)},
        )

        assert resposta.status_code == status.HTTP_200_OK

        resultados = resposta.data["results"]

        assert len(resultados) == 2
        assert {resultado["uuid"] for resultado in resultados} == {
            str(unidade_educacional_emef.uuid),
            str(unidade_educacional_inativa_emef.uuid),
        }

    def test_deve_filtrar_por_diretoria_regional(
        self,
        api_cliente,
        unidade_educacional_emef,
        unidade_educacional_inativa_emef,
        diretoria_regional_centro,
    ):
        """Deve filtrar unidades pela diretoria regional."""
        resposta = api_cliente.get(
            self.url,
            {"diretoria_regional": diretoria_regional_centro.id},
        )

        assert resposta.status_code == status.HTTP_200_OK

        resultados = resposta.data["results"]

        assert len(resultados) == 2
        assert {resultado["uuid"] for resultado in resultados} == {
            str(unidade_educacional_emef.uuid),
            str(unidade_educacional_inativa_emef.uuid),
        }

    def test_deve_filtrar_por_subprefeitura(
        self,
        api_cliente,
        unidade_educacional_emef,
        unidade_educacional_inativa_emef,
        subprefeitura_se,
    ):
        """Deve filtrar unidades pela subprefeitura."""
        resposta = api_cliente.get(
            self.url,
            {"subprefeitura": str(subprefeitura_se.uuid)},
        )

        assert resposta.status_code == status.HTTP_200_OK

        resultados = resposta.data["results"]

        assert len(resultados) == 2
        assert {resultado["uuid"] for resultado in resultados} == {
            str(unidade_educacional_emef.uuid),
            str(unidade_educacional_inativa_emef.uuid),
        }

    def test_deve_filtrar_por_multiplos_campos(
        self,
        api_cliente,
        unidade_educacional_emef,
        tipo_escola_emef,
        diretoria_regional_centro,
        subprefeitura_se,
    ):
        """Deve filtrar por múltiplos campos."""
        resposta = api_cliente.get(
            self.url,
            {
                "tipo_escola": str(tipo_escola_emef.uuid),
                "diretoria_regional": diretoria_regional_centro.id,
                "subprefeitura": str(subprefeitura_se.uuid),
                "status": "true",
            },
        )

        assert resposta.status_code == status.HTTP_200_OK

        resultados = resposta.data["results"]

        assert len(resultados) == 1
        assert resultados[0]["uuid"] == str(
            unidade_educacional_emef.uuid,
        )

    def test_deve_retornar_404_para_uuid_inexistente(
        self,
        api_cliente,
    ):
        """Deve retornar 404 quando o UUID não existir."""
        resposta = api_cliente.get(
            f"{self.url}{uuid.uuid4()}/",
        )

        assert resposta.status_code == status.HTTP_404_NOT_FOUND

    def test_nao_deve_permitir_criacao(
        self,
        api_cliente,
    ):
        """Não deve permitir criação de unidades educacionais."""
        resposta = api_cliente.post(
            self.url,
            data={
                "codigo_eol": "999999",
                "nome": "Unidade Teste",
            },
            format="json",
        )

        assert resposta.status_code == (status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_nao_deve_permitir_atualizacao_parcial(
        self,
        api_cliente,
        unidade_educacional_emef,
    ):
        """Não deve permitir atualização parcial."""
        resposta = api_cliente.patch(
            f"{self.url}{unidade_educacional_emef.uuid}/",
            data={"nome": "Unidade Alterada"},
            format="json",
        )

        assert resposta.status_code == (status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_nao_deve_permitir_exclusao(
        self,
        api_cliente,
        unidade_educacional_emef,
    ):
        """Não deve permitir exclusão de unidades educacionais."""
        resposta = api_cliente.delete(
            f"{self.url}{unidade_educacional_emef.uuid}/",
        )

        assert resposta.status_code == (status.HTTP_405_METHOD_NOT_ALLOWED)

        assert Unidadeeducacional.objects.filter(
            uuid=unidade_educacional_emef.uuid,
        ).exists()

    def test_deve_atualizar_unidade_educacional(
        self,
        api_cliente,
        unidade_educacional_emef,
        dados_unidade_emef,
        historico_responsavel,
        usuario_sincronizacao,
    ):
        """Deve atualizar os dados da unidade educacional."""
        dados = {
            "email": "atualizado@email.com",
            "telefone": "1133334444",
            "ativo": False,
            "responsaveis": [
                {
                    "uuid": str(historico_responsavel.responsavel.uuid),
                    "registro_funcional": (
                        historico_responsavel.responsavel.registro_funcional
                    ),
                    "nome": "Diretor Atualizado",
                    "cargo": historico_responsavel.cargo.codigo,
                    "email": "diretor@atualizado.com",
                    "telefone": "",
                    "celular": "",
                },
            ],
        }

        api_cliente.force_authenticate(
            user=usuario_sincronizacao,
        )

        resposta = api_cliente.put(
            f"{self.url}{unidade_educacional_emef.uuid}/",
            data=dados,
            format="json",
        )

        assert resposta.status_code == status.HTTP_200_OK, resposta.data

        unidade_educacional_emef.refresh_from_db()
        dados_unidade_emef.refresh_from_db()
        historico_responsavel.responsavel.refresh_from_db()

        assert unidade_educacional_emef.status is False
        assert dados_unidade_emef.email == "atualizado@email.com"
        assert dados_unidade_emef.telefone == "1133334444"

        assert historico_responsavel.responsavel.nome == "Diretor Atualizado"
        assert (
            historico_responsavel.responsavel.email == "diretor@atualizado.com"
        )

    def test_nao_deve_atualizar_com_email_invalido(
        self,
        api_cliente,
        unidade_educacional_emef,
        historico_responsavel,
        usuario_sincronizacao,
    ):
        """Deve retornar 400 quando o e-mail da unidade for inválido."""
        dados = {
            "email": "email-invalido",
            "telefone": "1133334444",
            "ativo": True,
            "responsaveis": [
                {
                    "uuid": str(historico_responsavel.responsavel.uuid),
                    "registro_funcional": (
                        historico_responsavel.responsavel.registro_funcional
                    ),
                    "nome": historico_responsavel.responsavel.nome,
                    "cargo": historico_responsavel.cargo.codigo,
                    "email": historico_responsavel.responsavel.email,
                    "telefone": "",
                    "celular": "",
                },
            ],
        }

        api_cliente.force_authenticate(
            user=usuario_sincronizacao,
        )

        resposta = api_cliente.put(
            f"{self.url}{unidade_educacional_emef.uuid}/",
            data=dados,
            format="json",
        )

        assert resposta.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in resposta.data

    def test_nao_deve_atualizar_com_rf_invalido(
        self,
        api_cliente,
        unidade_educacional_emef,
        historico_responsavel,
        usuario_sincronizacao,
    ):
        """Deve retornar 400 quando o RF possuir formato inválido."""
        dados = {
            "email": "atualizado@email.com",
            "telefone": "1133334444",
            "ativo": True,
            "responsaveis": [
                {
                    "uuid": str(historico_responsavel.responsavel.uuid),
                    "registro_funcional": "ABC123",
                    "nome": "Diretor Atualizado",
                    "cargo": historico_responsavel.cargo.codigo,
                    "email": "diretor@email.com",
                    "telefone": "",
                    "celular": "",
                },
            ],
        }

        api_cliente.force_authenticate(
            user=usuario_sincronizacao,
        )

        resposta = api_cliente.put(
            f"{self.url}{unidade_educacional_emef.uuid}/",
            data=dados,
            format="json",
        )

        assert resposta.status_code == status.HTTP_400_BAD_REQUEST
        assert "responsaveis" in resposta.data

    def test_nao_deve_atualizar_sem_responsaveis(
        self,
        api_cliente,
        unidade_educacional_emef,
        usuario_sincronizacao,
    ):
        """Deve retornar 400 quando responsáveis não forem informados."""
        dados = {
            "email": "atualizado@email.com",
            "telefone": "1133334444",
            "ativo": True,
        }

        api_cliente.force_authenticate(
            user=usuario_sincronizacao,
        )

        resposta = api_cliente.put(
            f"{self.url}{unidade_educacional_emef.uuid}/",
            data=dados,
            format="json",
        )

        assert resposta.status_code == status.HTTP_400_BAD_REQUEST
        assert "responsaveis" in resposta.data

    def test_nao_deve_atualizar_com_lista_de_responsaveis_vazia(
        self,
        api_cliente,
        unidade_educacional_emef,
        usuario_sincronizacao,
    ):
        """Deve retornar 400 quando a lista de responsáveis estiver vazia."""
        dados = {
            "email": "atualizado@email.com",
            "telefone": "1133334444",
            "ativo": True,
            "responsaveis": [],
        }

        api_cliente.force_authenticate(
            user=usuario_sincronizacao,
        )

        resposta = api_cliente.put(
            f"{self.url}{unidade_educacional_emef.uuid}/",
            data=dados,
            format="json",
        )

        assert resposta.status_code == status.HTTP_400_BAD_REQUEST
        assert "responsaveis" in resposta.data

    def test_nao_deve_atualizar_com_rf_ja_existente_no_banco(
        self,
        api_cliente,
        unidade_educacional_emef,
        responsavel_unidade,
        usuario_sincronizacao,
    ):
        """Deve retornar 400 quando o RF já estiver cadastrado."""
        dados = {
            "email": "atualizado@email.com",
            "telefone": "1133334444",
            "ativo": True,
            "responsaveis": [
                {
                    "registro_funcional": (
                        responsavel_unidade.registro_funcional
                    ),
                    "nome": "Novo Responsável",
                    "cargo": "DIRETOR",
                    "email": "novo@email.com",
                    "telefone": "",
                    "celular": "",
                },
            ],
        }

        api_cliente.force_authenticate(
            user=usuario_sincronizacao,
        )

        resposta = api_cliente.put(
            f"{self.url}{unidade_educacional_emef.uuid}/",
            data=dados,
            format="json",
        )

        assert resposta.status_code == status.HTTP_400_BAD_REQUEST
        assert resposta.data["title"] == "Não é possível adicionar o contato"
        assert (
            responsavel_unidade.registro_funcional in resposta.data["message"]
        )

    def test_nao_deve_atualizar_com_responsavel_sem_vinculo(
        self,
        api_cliente,
        unidade_educacional_emef,
        responsavel_unidade,
        cargo_perfil_diretor,
        usuario_sincronizacao,
    ):
        """Deve retornar 400 quando responsável não estiver vinculado."""
        dados = {
            "email": "atualizado@email.com",
            "telefone": "1133334444",
            "ativo": True,
            "responsaveis": [
                {
                    "uuid": str(responsavel_unidade.uuid),
                    "registro_funcional": (
                        responsavel_unidade.registro_funcional
                    ),
                    "nome": responsavel_unidade.nome,
                    "cargo": cargo_perfil_diretor.codigo,
                    "email": responsavel_unidade.email,
                    "telefone": "",
                    "celular": "",
                },
            ],
        }

        api_cliente.force_authenticate(
            user=usuario_sincronizacao,
        )

        resposta = api_cliente.put(
            f"{self.url}{unidade_educacional_emef.uuid}/",
            data=dados,
            format="json",
        )

        assert resposta.status_code == status.HTTP_400_BAD_REQUEST
        assert resposta.data["title"] == "Não é possível adicionar o contato"
        assert (
            responsavel_unidade.registro_funcional in resposta.data["message"]
        )
        assert (
            "não está vinculado à unidade educacional."
            in resposta.data["message"]
        )

    def test_nao_deve_atualizar_com_telefone_do_responsavel_invalido(
        self,
        api_cliente,
        unidade_educacional_emef,
        historico_responsavel,
        usuario_sincronizacao,
    ):
        """Deve retornar 400 quando o telefone exceder o limite do model."""
        dados = {
            "email": "atualizado@email.com",
            "telefone": "1133334444",
            "ativo": True,
            "responsaveis": [
                {
                    "uuid": str(historico_responsavel.responsavel.uuid),
                    "registro_funcional": (
                        historico_responsavel.responsavel.registro_funcional
                    ),
                    "nome": historico_responsavel.responsavel.nome,
                    "cargo": historico_responsavel.cargo.codigo,
                    "email": historico_responsavel.responsavel.email,
                    "telefone": "1" * 21,
                    "celular": "",
                },
            ],
        }

        api_cliente.force_authenticate(
            user=usuario_sincronizacao,
        )

        resposta = api_cliente.put(
            f"{self.url}{unidade_educacional_emef.uuid}/",
            data=dados,
            format="json",
        )

        assert resposta.status_code == status.HTTP_400_BAD_REQUEST
        assert "telefone" in resposta.data
