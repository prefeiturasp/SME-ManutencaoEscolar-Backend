"""Serializer responsável pela representação dos cargos EOL."""

from rest_framework import serializers

from apps.usuarios.models import CargoEOL


class CargoEOLSerializer(serializers.ModelSerializer):
    """Serializa os dados dos cargos EOL para resposta da API.

    Inclui a identificação, o código e o nome do cargo, além do perfil
    de acesso associado e da situação de atividade do cargo.
    """

    class Meta:
        model = CargoEOL
        fields = (
            "id",
            "codigo",
            "nome",
            "perfil",
            "ativo",
        )
