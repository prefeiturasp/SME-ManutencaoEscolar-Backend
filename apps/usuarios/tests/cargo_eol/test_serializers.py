import pytest
from django.test import TestCase
from rest_framework.exceptions import ValidationError

from apps.usuarios.constants import PerfilAcesso
from apps.usuarios.models import CargoEOL
from apps.usuarios.serializers.cargo_eol_serializer import CargoEOLSerializer


class TestCargoEOLSerializer(TestCase):
    """Testa o serializer de CargoEOL."""

    def test_deve_serializar_todos_os_campos(self):
        cargo = CargoEOL.objects.create(
            codigo="4444",
            nome="RESPONSAVEL UNIDADE",
            perfil=PerfilAcesso.UE,
            ativo=True,
        )

        serializer = CargoEOLSerializer(cargo)

        assert serializer.data == {
            "id": cargo.id,
            "codigo": "4444",
            "nome": "RESPONSAVEL UNIDADE",
            "perfil": PerfilAcesso.UE,
            "ativo": True,
        }

    def test_deve_serializar_cargo_sem_perfil(self):
        cargo = CargoEOL.objects.create(
            codigo="9998",
            nome="COORDENADOR II - ENS MED",
            perfil="",
            ativo=True,
        )

        serializer = CargoEOLSerializer(cargo)

        assert serializer.data["codigo"] == "9998"
        assert serializer.data["nome"] == "COORDENADOR II - ENS MED"
        assert serializer.data["perfil"] == ""
        assert serializer.data["ativo"] is True

    def test_deve_serializar_cargo_inativo(self):
        cargo = CargoEOL.objects.create(
            codigo="9998",
            nome="COORDENADOR II - ENS MED",
            ativo=False,
        )

        serializer = CargoEOLSerializer(cargo)

        assert serializer.data["ativo"] is False

    def test_nao_deve_permitir_criacao_sem_codigo(self):
        serializer = CargoEOLSerializer(
            data={
                "nome": "DIRETOR DE ESCOLA",
                "perfil": PerfilAcesso.UE,
                "ativo": True,
            }
        )

        assert not serializer.is_valid()

        assert "codigo" in serializer.errors

    def test_nao_deve_permitir_criacao_sem_nome(self):
        serializer = CargoEOLSerializer(
            data={
                "codigo": "3360",
                "perfil": PerfilAcesso.UE,
                "ativo": True,
            }
        )

        assert not serializer.is_valid()

        assert "nome" in serializer.errors

    def test_deve_aceitar_cargo_sem_perfil(self):
        serializer = CargoEOLSerializer(
            data={
                "codigo": "9998",
                "nome": "COORDENADOR II - ENS MED",
                "perfil": "",
                "ativo": True,
            }
        )

        assert serializer.is_valid(), serializer.errors

    def test_nao_deve_aceitar_perfil_invalido(self):
        serializer = CargoEOLSerializer(
            data={
                "codigo": "9998",
                "nome": "COORDENADOR II - ENS MED",
                "perfil": "PERFIL_INVALIDO",
                "ativo": True,
            }
        )

        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)
