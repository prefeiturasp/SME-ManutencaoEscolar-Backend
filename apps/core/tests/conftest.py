import pytest
from rest_framework.test import APIRequestFactory


@pytest.fixture
def api_factory():
    """Fixture que fornece uma instância do APIRequestFactory do DRF."""
    return APIRequestFactory()
