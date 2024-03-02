from django.urls import reverse
from rest_framework import status

from kompello.core.models.auth_models import Tenant
from kompello.core.tests.helpers import BaseTestCase


class TenantViewModelTest(BaseTestCase):

    def setUp(self):
        self.admin_users = self._create_admin_user(1)
        self.users = self._create_user(5)

    def test_create(self):
        """
        Test case for creating a new tenant using the API.

        This test verifies that a new tenant can be created by sending a POST request to the appropriate endpoint.
        It checks that the request is authenticated and unauthorized if no authentication is provided.
        It also checks that the request is successful and returns a status code of 201 (Created) when authentication is provided.
        Finally, it verifies that the created tenant exists in the database and is associated with the user who made the request.
        """
        data = {
            "slug": "slugcreate",
            "name": "Tenant from API",
        }

        no_auth, auth = self._test_auth_not_auth(
            self.users[0],
            {
                "path": reverse("core:tenants-list"),
                "data": data,
                "format": "json"
            },
            "post"
        )

        self.assertEqual(no_auth.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(auth.status_code, status.HTTP_201_CREATED)

        tenant = Tenant.objects.get(uuid=auth.data["uuid"])
        self.assertIsNotNone(tenant)
        self.assertIn(self.users[0], tenant.users.all())

    def test_list(self):
        """
        Test case for listing tenants.

        This test case verifies the behavior of the `list` endpoint of the `Tenant` API view.
        It checks that the endpoint returns the correct response and status code for different scenarios.

        Steps:
        1. Create 3 tenants.
        2. Add users to the first two tenants.
        3. Test the endpoint with different authentication scenarios:
            a. Test with a non-authenticated user.
            b. Test with an authenticated user.
        4. Verify the response and status code for each scenario.

        Expected Results:
        - For a non-authenticated user, the endpoint should return a 401 UNAUTHORIZED status code.
        - For an authenticated user, the endpoint should return a 200 OK status code.
        - The number of tenants returned in the response should match the expected count.

        """
        tenants = self._create_tenant(3)

        tenants[0].users.add(self.users[0])
        tenants[0].save()
        tenants[1].users.add(self.users[0], self.users[1])
        tenants[1].save()

        no_auth, auth = self._test_auth_not_auth(
            self.users[1],
            {
                "path": reverse("core:tenants-list"),
                "data": None,
                "format": "json"
            },
            "get"
        )
        self.assertEqual(no_auth.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(auth.status_code, status.HTTP_200_OK)
        self.assertEqual(len(auth.data), 1)

        no_auth, auth = self._test_auth_not_auth(
            self.admin_users[0],
            {
                "path": reverse("core:tenants-list"),
                "data": None,
                "format": "json"
            },
            "get"
        )
        self.assertEqual(no_auth.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(auth.status_code, status.HTTP_200_OK)
        self.assertEqual(len(auth.data), 3)

    def test_get(self):
        """
        Test case for the GET method of the tenants API view.

        This test verifies the behavior of the GET method when retrieving tenant details.

        Steps:
        1. Create two tenants.
        2. Add users to the tenants.
        3. Test authentication and authorization for accessing tenant details.
        4. Verify the status codes of the API responses.

        Expected results:
        - For unauthorized users, the status code should be 401 UNAUTHORIZED.
        - For authorized users not in a Tenant, the status code should be 403 FORBIDDEN.
        - For authorized users, the status code should be 200 OK.

        """
        tenants = self._create_tenant(2)

        tenants[0].users.add(self.users[0])
        tenants[0].save()
        tenants[1].users.add(self.users[0], self.users[1])
        tenants[1].save()

        no_auth, auth = self._test_auth_not_auth(
            self.users[1],
            {
                "path": reverse("core:tenants-detail", args=[f"{tenants[0].uuid}"]),
                "data": "",
                "format": "json"
            },
            "get"
        )
        self.assertEqual(no_auth.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(auth.status_code, status.HTTP_403_FORBIDDEN)

        no_auth, auth = self._test_auth_not_auth(
            self.users[1],
            {
                "path": reverse("core:tenants-detail", args=[f"{tenants[1].uuid}"]),
                "data": "",
                "format": "json"
            },
            "get"
        )
        self.assertEqual(no_auth.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(auth.status_code, status.HTTP_200_OK)

        no_auth, auth = self._test_auth_not_auth(
            self.admin_users[0],
            {
                "path": reverse("core:tenants-detail", args=[f"{tenants[1].uuid}"]),
                "data": None,
                "format": "json"
            },
            "get"
        )
        self.assertEqual(no_auth.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(auth.status_code, status.HTTP_200_OK)

    def test_put(self):
        """
        Test case for the PUT method of the tenant API view.

        This test verifies the behavior of the PUT method when updating a tenant's information.
        It performs the following steps:
        1. Creates two tenants and adds users to them.
        2. Sends a PUT request with updated data for the first tenant, using different authentication scenarios.
        3. Verifies the response status codes and the updated data in the response.

        """
        tenants = self._create_tenant(2)
        tenants[0].users.add(self.users[0])
        tenants[0].save()
        tenants[1].users.add(self.users[0], self.users[1])
        tenants[1].save()

        data = {
            "slug": "newslug",
            "name": "newname",
        }
        no_auth, auth = self._test_auth_not_auth(
            self.users[0],
            {
                "path": reverse("core:tenants-detail", args=[f"{tenants[0].uuid}"]),
                "data": data,
                "format": "json"
            },
            "put"
        )

        self.assertEqual(no_auth.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(auth.status_code, status.HTTP_200_OK)
        self.assertEqual(auth.data["slug"], data["slug"])
        self.assertEqual(auth.data["name"], data["name"])

        resp = self._request(
            self.users[1],
            {
                "path": reverse("core:tenants-detail", args=[f"{tenants[0].uuid}"]),
                "data": data,
                "format": "json"
            },
            "put"
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        resp = self._request(
            self.admin_users[0],
            {
                "path": reverse("core:tenants-detail", args=[f"{tenants[0].uuid}"]),
                "data": data,
                "format": "json"
            },
            "put"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_patch(self):
        """
        Test case for patching a tenant.

        This method tests the patch functionality of the tenant API view. It verifies that the patch request
        returns the expected status codes and data for different user roles.

        Steps:
        1. Create two tenants and add users to them.
        2. Send a patch request with authentication as a non-authenticated user and verify that it returns
           HTTP 401 Unauthorized.
        3. Send a patch request with authentication as a user who is not associated with the tenant and verify
           that it returns HTTP 403 Forbidden.
        4. Send a patch request with authentication as an admin user and verify that it returns HTTP 200 OK
           and the tenant's slug is updated.

        Returns:
            None
        """
        tenants = self._create_tenant(2)
        tenants[0].users.add(self.users[0])
        tenants[0].save()
        tenants[1].users.add(self.users[0], self.users[1])
        tenants[1].save()

        data = {
            "slug": "newslug",
        }
        no_auth, auth = self._test_auth_not_auth(
            self.users[0],
            {
                "path": reverse("core:tenants-detail", args=[f"{tenants[0].uuid}"]),
                "data": data,
                "format": "json"
            },
            "patch"
        )

        self.assertEqual(no_auth.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(auth.status_code, status.HTTP_200_OK)
        self.assertEqual(auth.data["slug"], data["slug"])

        resp = self._request(
            self.users[1],
            {
                "path": reverse("core:tenants-detail", args=[f"{tenants[0].uuid}"]),
                "data": data,
                "format": "json"
            },
            "patch"
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        resp = self._request(
            self.admin_users[0],
            {
                "path": reverse("core:tenants-detail", args=[f"{tenants[0].uuid}"]),
                "data": data,
                "format": "json"
            },
            "patch"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_delete(self):
        """
        Test case for deleting a tenant.

        This test verifies the behavior of the delete method in the tenant API view.
        It performs the following steps:
        1. Creates a tenant and adds a user to it.
        2. Tests the authentication and authorization for a user who is not authenticated.
        3. Tests the authentication and authorization for a user who is authenticated.
        4. Verifies the status code of the responses.

        """
        tenants = self._create_tenant(1)
        tenants[0].users.add(self.users[0])
        tenants[0].save()

        no_auth, auth = self._test_auth_not_auth(
            self.users[0],
            {
                "path": reverse("core:tenants-detail", args=[f"{tenants[0].uuid}"]),
                "data": None,
                "format": "json"
            },
            "delete"
        )

        self.assertEqual(no_auth.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(auth.status_code, status.HTTP_204_NO_CONTENT)

        tenants = self._create_tenant(1)
        resp = self._request(
            self.admin_users[0],
            {
                "path": reverse("core:tenants-detail", args=[f"{tenants[0].uuid}"]),
                "data": None,
                "format": "json"
            },
            "delete"
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_users(self):
        """
        Test case for retrieving users of a tenant.

        This method tests the functionality of retrieving the users associated with a specific tenant.
        It performs the following steps:
        1. Creates a tenant.
        2. Adds multiple users to the tenant.
        3. Tests the authentication and authorization for retrieving the users without authentication and with authentication.
        4. Verifies the response status codes and the number of retrieved users.

        """
        tenants = self._create_tenant(1)
        tenants[0].users.add(self.users[0])
        tenants[0].users.add(self.users[1])
        tenants[0].users.add(self.users[2])
        tenants[0].save()

        no_auth, auth = self._test_auth_not_auth(
            self.users[0],
            {
                "path": reverse("core:tenants-users", args=[f"{tenants[0].uuid}"]),
                "data": None,
                "format": "json"
            },
            "get"
        )
        self.assertEqual(no_auth.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(auth.status_code, status.HTTP_200_OK)
        self.assertEqual(len(auth.data), 3)

        resp = self._request(
            self.admin_users[0],
            {
                "path": reverse("core:tenants-users", args=[f"{tenants[0].uuid}"]),
                "data": None,
                "format": "json"
            },
            "get"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 3)

    def test_add_users(self):
        """
        Test case for adding users to a tenant.

        This method tests the functionality of adding users to a tenant by making a POST request to the
        'core:tenants-add-users' endpoint with the required data. It verifies that the request is
        authenticated and returns the expected response status code. It also checks that the number of
        users associated with the tenant is updated correctly.

        """
        tenants = self._create_tenant(1)
        tenants[0].users.add(self.users[0])
        tenants[0].save()
        no_auth, auth = self._test_auth_not_auth(
            self.users[0],
            {
                "path": reverse("core:tenants-add-users", args=[f"{tenants[0].uuid}"]),
                "data": {'uuids': [user.uuid for user in self.users]},
                "format": "json"
            },
            "post"
        )
        self.assertEqual(no_auth.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(auth.status_code, status.HTTP_200_OK)
        self.assertEqual(Tenant.objects.get(uuid=tenants[0].uuid).users.count(), len(self.users))

    def test_remove_users(self):
        """
        Test case for removing users from a tenant.

        This test case verifies that users can be successfully removed from a tenant.
        It performs the following steps:
        1. Creates a tenant.
        2. Adds users to the tenant.
        3. Sends a request to remove the users from the tenant.
        4. Verifies that the request returns the expected status codes.
        5. Verifies that the users have been successfully removed from the tenant.

        """
        tenants = self._create_tenant(1)
        tenants[0].users.add(*self.users)
        tenants[0].save()
        no_auth, auth = self._test_auth_not_auth(
            self.users[0],
            {
                "path": reverse("core:tenants-remove-users", args=[f"{tenants[0].uuid}"]),
                "data": {'uuids': [user.uuid for user in self.users]},
                "format": "json"
            },
            "post"
        )
        self.assertEqual(no_auth.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(auth.status_code, status.HTTP_200_OK)
        self.assertEqual(Tenant.objects.get(uuid=tenants[0].uuid).users.count(), 0)


