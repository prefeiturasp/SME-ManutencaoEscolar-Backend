import pytest

from apps.usuarios.repository.cargo_repository import CargoEOLRepository


class TestCargoEOL:
    @pytest.mark.django_db
    def test_buscar_por_codigo_que_existe(
        self,
    ):
        cargo = CargoEOLRepository.buscar_por_codigo(3360)
        assert cargo == {
            "id": 1,
            "codigo": "3360",
            "nome": "DIRETOR DE ESCOLA",
            "perfil": "UE",
            "ativo": True,
        }

    @pytest.mark.django_db
    def test_buscar_por_codigo_que_nao_existe(
        self,
    ):
        cargo = CargoEOLRepository.buscar_por_codigo(0000)
        assert cargo is None
