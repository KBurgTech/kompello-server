from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from kompello.core.models.auth_models import KompelloUser, Tenant


USER_PASSWORD = "123456789!ABC"


class BaseTestCase(APITestCase):

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)

    @staticmethod
    def _create_tenant(count):
        tenants = []
        for i in range(1, count + 1):
            tenants.append(Tenant.objects.create(slug=f"slug{i}", name=f"Tenant {i}"))

        return tenants

    @staticmethod
    def _create_admin_user(count):
        admin_users = []
        for i in range(1, count + 1):
            admin_users.append(
                KompelloUser.objects.create_superuser(f"admin{i}", f"admin{i}@email.com", USER_PASSWORD))
        return admin_users

    @staticmethod
    def _create_user(count):
        users = []
        for i in range(1, count + 1):
            users.append(
                KompelloUser.objects.create_user(f"user{i}", f"user{i}@email.com", USER_PASSWORD, first_name=f"Test{i}",
                                              last_name=f"User{i}"))
        return users

    def _login(self, email, password):
        token = self.client.post(reverse("core:auth.standard"), {"username": email, "password": password}, format='json')
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.data['access_token']}")
        return token.status_code == 200

    def _logout(self):
        self.client.credentials(HTTP_AUTHORIZATION=None)

    def _request(self, user, request, mode):
        func = getattr(self.client, mode)
        self.assertIsNotNone(func)
        if user is not None:
            self.assertTrue(self._login(email=user.email, password=USER_PASSWORD))
        auth_resp = func(**request)
        self._logout()
        return auth_resp

    def _test_auth_not_auth(self, user, request, mode):
        func = getattr(self.client, mode)
        self.assertIsNotNone(func)

        non_auth_resp = func(**request)
        self.assertTrue(self._login(email=user.email, password=USER_PASSWORD))
        auth_resp = func(**request)
        self._logout()

        return non_auth_resp, auth_resp
