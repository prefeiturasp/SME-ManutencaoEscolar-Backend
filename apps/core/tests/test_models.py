"""Testes para os modelos e mixins da aplicação Core."""

import uuid

import pytest
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from apps.usuarios.constants import PerfilAcesso
from apps.usuarios.models.cargo_eol import CargoEOL

from .conftest import ModelBase

User = get_user_model()


password = str(uuid.uuid4())


@pytest.fixture
def cargo_teste(db):
    """Fixture que cria um cargo de teste.."""
    return CargoEOL.objects.create(
        codigo=999999,
        nome="CARGO IMPORTANTE",
        perfil=PerfilAcesso.UE,
        ativo=True,
    )


@pytest.fixture
def usuario_teste(db, cargo_teste):
    """Fixture que cria um usuário de teste."""
    return User.objects.create_user(
        username="teste", password=password, cargo=cargo_teste
    )


class TestUUIDMixin:
    def test_uuid_mixin_configura_campo_id_corretamente(self):
        field = ModelBase._meta.get_field("uuid")
        assert isinstance(field, models.UUIDField)
        assert field.default == uuid.uuid4
        assert field.editable is False


class TestTimestampMixin:
    def test_timestamp_mixin_configura_campos_corretamente(self):
        criado_em = ModelBase._meta.get_field("criado_em")
        atualizado_em = ModelBase._meta.get_field("atualizado_em")

        assert criado_em.auto_now_add is True
        assert criado_em.auto_now is False

        assert atualizado_em.auto_now is True
        assert atualizado_em.auto_now_add is False


class TestAuditMixin:
    @pytest.mark.django_db
    def test_criado_por_no_save_nao_e_alterado_por_atualizacoes_posteriores(
        self, usuario_teste, cargo_teste
    ):
        obj = ModelBase.objects.create(nome="Teste", criado_por=usuario_teste)
        novo_usuario = User.objects.create_user(
            username="novo_usuario", password=password, cargo=cargo_teste
        )

        obj.atualizado_por = novo_usuario
        obj.save()
        obj.refresh_from_db()

        assert obj.atualizado_por == novo_usuario
        assert obj.criado_por == usuario_teste

    def test_audit_mixin_configura_campos_como_opcionais(self):
        criado_por = ModelBase._meta.get_field("criado_por")
        atualizado_por = ModelBase._meta.get_field("atualizado_por")
        assert criado_por.null is True
        assert atualizado_por.null is True


class TestSoftDeleteMixin:
    """Testes para o mixin SoftDeleteMixin."""

    @pytest.mark.django_db
    def test_delete_soft_delete(self):
        """Testa que delete() realiza soft-delete."""
        obj = ModelBase.objects.create(nome="Teste")
        assert obj.deletado_em is None

        obj.delete()

        obj.refresh_from_db()
        assert obj.deletado_em is not None
        assert isinstance(obj.deletado_em, type(timezone.now()))

    @pytest.mark.django_db
    def test_hard_delete_remove_permanentemente(self):
        """Testa que hard_delete() remove permanentemente."""
        obj = ModelBase.objects.create(nome="Teste")
        obj_id = obj.id

        obj.hard_delete()

        assert ModelBase.dm_objects.filter(id=obj_id).count() == 0

    @pytest.mark.django_db
    def test_restore_restaura_objeto(self):
        """Testa que restore() restaura um objeto soft-deleted."""
        obj = ModelBase.objects.create(nome="Teste")
        obj.delete()

        assert obj.deletado_em is not None

        obj.restore()

        obj.refresh_from_db()
        assert obj.deletado_em is None

    @pytest.mark.django_db
    def test_soft_deleted_nao_aparece_em_objects(self):
        """Testa que objetos soft-deleted não aparecem em objects."""
        obj = ModelBase.objects.create(nome="Teste")
        obj.delete()

        assert ModelBase.objects.filter(id=obj.id).count() == 0

    @pytest.mark.django_db
    def test_soft_deleted_aparece_em_dm_objects(self):
        """Testa que objetos soft-deleted aparecem em dm_objects."""
        obj = ModelBase.objects.create(nome="Teste")
        obj.delete()

        assert ModelBase.dm_objects.filter(id=obj.id).count() == 1

    @pytest.mark.django_db
    def test_delete_atualiza_deletado_em(self):
        """Testa que o corpo de delete() atualiza o campo deletado_em."""
        obj = ModelBase.objects.create(nome="Teste")
        before_delete = timezone.now()

        obj.delete()

        obj.refresh_from_db()
        assert obj.deletado_em is not None
        assert obj.deletado_em >= before_delete

    @pytest.mark.django_db
    def test_restore_limpa_deletado_em(self):
        """Testa que o corpo de restore() limpa o campo deletado_em."""
        obj = ModelBase.objects.create(nome="Teste")
        obj.delete()
        obj.refresh_from_db()
        assert obj.deletado_em is not None

        obj.restore()

        obj.refresh_from_db()
        assert obj.deletado_em is None
