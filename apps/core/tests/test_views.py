from rest_framework.test import APIRequestFactory, APITestCase

from apps.core.api.views import HealthCheckView


class HealthCheckViewTests(APITestCase):
    def test_healthcheck_view_returns_status_ok(self):
        factory = APIRequestFactory()
        request = factory.get("/api/v1/health/")

        response = HealthCheckView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"status": "ok"})
