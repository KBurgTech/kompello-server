from django.urls import reverse
from rest_framework import status

from kompello.core.models.auth_models import KompelloUser
from kompello.core.tests.helpers import BaseTestCase, USER_PASSWORD


class UserViewModelTest(BaseTestCase):
    def setUp(self):
        self.admin_users = self._create_admin_user(1)
        self.users = self._create_user(5)

    def test_create(self):
        """
        Test case for creating a new user.

        This test verifies that a new user can be created successfully by sending a POST request to the 'core:users-list' endpoint.
        It checks that the response status code is 201 (Created) and that the returned user data matches the input data, except for the password field.
        It also verifies that the 'uuid' field is present in the response data.

        Additionally, it checks that the user object is created in the database and that the password is not equal to the input password.

        """
        data = {
            "first_name": "Firstname",
            "last_name": "Lastname",
            "email": "user@example.com",
            "password": USER_PASSWORD
        }
        create_user_resp = self.client.post(reverse("core:users-list"), data, format='json')
        self.assertEqual(create_user_resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(create_user_resp.data['first_name'], data['first_name'])
        self.assertEqual(create_user_resp.data['last_name'], data['last_name'])
        self.assertEqual(create_user_resp.data['email'], data['email'])
        self.assertNotIn("password", create_user_resp.data)
        self.assertIn("uuid", create_user_resp.data)

        user = KompelloUser.objects.get(uuid=create_user_resp.data['uuid'])
        self.assertIsNotNone(user)
        self.assertNotEquals(user.password, data['password'])

    def test_list(self):
        """
        Test the list functionality of the user API view.

        This test case verifies that:
        - Non-admin users cannot list users and receive a 401 Unauthorized status code.
        - Admin users can list users and receive a 200 OK status code.
        - The number of users returned in the response is correct.

        """
        # Test Non-Admin cannot list
        list_not_auth_resp = self.client.get(reverse("core:users-list"), format='json')
        self.assertEqual(list_not_auth_resp.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test Admin can list
        self._login(email=self.admin_users[0].email, password=USER_PASSWORD)
        list_auth_resp = self.client.get(reverse("core:users-list"), format='json')
        self.assertEqual(list_auth_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_auth_resp.data), 6)

    def test_get(self):
         """
         Test the GET request for retrieving user details.

         This test method verifies the behavior of the GET request for retrieving user details.
         It performs the following steps:
         1. Retrieves an admin user and a regular user from the database.
         2. Sends a GET request to retrieve the details of the regular user without authentication.
             - Asserts that the response status code is 401 (Unauthorized).
         3. Logs in as the regular user.
         4. Sends a GET request to retrieve the details of the regular user with authentication.
             - Asserts that the response status code is 200 (OK).
         5. Sends a GET request to retrieve the details of the admin user with authentication.
             - Asserts that the response status code is 403 (Forbidden).
         6. Logs out.
         7. Logs in as the admin user.
         8. Sends a GET request to retrieve the details of the regular user with authentication.
             - Asserts that the response status code is 200 (OK).

         This test ensures that the API endpoint for retrieving user details behaves correctly
         in terms of authentication and authorization.
         """
         adminuser = KompelloUser.objects.filter(is_superuser=True).first()
         user = KompelloUser.objects.filter(is_superuser=False).first()

         get_not_auth_resp = self.client.get(reverse("core:users-detail", args=[f"{user.uuid}"]))
         self.assertEqual(get_not_auth_resp.status_code, status.HTTP_401_UNAUTHORIZED)
         self._login(email=user.email, password=USER_PASSWORD)
         get_auth_resp = self.client.get(reverse("core:users-detail", args=[f"{user.uuid}"]))
         self.assertEqual(get_auth_resp.status_code, status.HTTP_200_OK)
         get_auth_resp_not_user = self.client.get(reverse("core:users-detail", args=[f"{adminuser.uuid}"]))
         self.assertEqual(get_auth_resp_not_user.status_code, status.HTTP_403_FORBIDDEN)

         self._logout()
         self._login(email=adminuser.email, password=USER_PASSWORD)
         get_auth_resp_not_self = self.client.get(reverse("core:users-detail", args=[f"{user.uuid}"]))
         self.assertEqual(get_auth_resp_not_self.status_code, status.HTTP_200_OK)

    def test_put(self):
         """
         Test case for the PUT request on the users-detail endpoint.

         This test verifies that a user can update their information by sending a PUT request
         to the users-detail endpoint. It checks that the request returns the expected status
         codes and that the user's information is updated correctly in the database.

         Steps:
         1. Create a dictionary with the updated user information.
         2. Retrieve a non-superuser user from the database.
         3. Send a PUT request to the users-detail endpoint without authentication and verify
             that it returns a 401 Unauthorized status code.
         4. Log in as the user with the default password.
         5. Send a PUT request to the users-detail endpoint with authentication and verify
             that it returns a 200 OK status code.
         6. Retrieve the updated user from the database and verify that their information
             matches the updated data.
         7. Log out of the user account.
         8. Log in as the updated user using the new email and password and verify that the
             login is successful.

         """
         data = {
              "first_name": "NewFirst",
              "last_name": "NewLast",
              "email": "newemail@example.com",
              "password": "1234567890abc!NEW"
         }
         user = KompelloUser.objects.filter(is_superuser=False).first()

         get_not_auth_resp = self.client.put(reverse("core:users-detail", args=[f"{user.uuid}"]), data, format='json')
         self.assertEqual(get_not_auth_resp.status_code, status.HTTP_401_UNAUTHORIZED)

         self._login(email=user.email, password=USER_PASSWORD)
         get_auth_resp = self.client.put(reverse("core:users-detail", args=[f"{user.uuid}"]), data, format='json')
         self.assertEqual(get_auth_resp.status_code, status.HTTP_200_OK)

         updated_user = KompelloUser.objects.get(uuid=user.uuid)
         self.assertEqual(updated_user.first_name, data['first_name'])
         self.assertEqual(updated_user.last_name, data['last_name'])
         self.assertEqual(updated_user.email, data['email'])

         self._logout()
         self.assertTrue(self._login(email=data['email'], password=data['password']))

    def test_patch(self):
        """
        Test case for patching user data.

        This method tests the patch functionality of the user API view. It verifies that a user's first name and last name can be updated successfully.

        Steps:
        1. Create a dictionary `data` with the new first name and last name.
        2. Retrieve a non-superuser user from the database.
        3. Send a PATCH request to the user detail endpoint with the updated data, without authentication.
        4. Verify that the response status code is 401 UNAUTHORIZED.
        5. Log in as the user using the `_login` method.
        6. Send a PATCH request to the user detail endpoint with the updated data, with authentication.
        7. Verify that the response status code is 200 OK.
        8. Retrieve the updated user from the database.
        9. Verify that the user's first name and last name have been updated correctly.

        """
        data = {
            "first_name": "NewFirst",
            "last_name": "NewLast",
        }
        user = KompelloUser.objects.filter(is_superuser=False).first()

        get_not_auth_resp = self.client.patch(reverse("core:users-detail", args=[f"{user.uuid}"]), data, format='json')
        self.assertEqual(get_not_auth_resp.status_code, status.HTTP_401_UNAUTHORIZED)

        self._login(email=user.email, password=USER_PASSWORD)
        get_auth_resp = self.client.patch(reverse("core:users-detail", args=[f"{user.uuid}"]), data, format='json')
        self.assertEqual(get_auth_resp.status_code, status.HTTP_200_OK)

        updated_user = KompelloUser.objects.get(uuid=user.uuid)
        self.assertEqual(updated_user.first_name, data['first_name'])
        self.assertEqual(updated_user.last_name, data['last_name'])

    def test_delete(self):
        """
        Test case for deleting a user.

        This method tests the deletion of a user by sending a DELETE request to the user detail endpoint.
        It first checks if the request is unauthorized when the user is not authenticated.
        Then, it logs in the user and sends another DELETE request to delete the user.
        Finally, it asserts that the response status code is 204 (NO CONTENT) indicating successful deletion.
        """
        user = KompelloUser.objects.filter(is_superuser=False).first()
        get_not_auth_resp = self.client.delete(reverse("core:users-detail", args=[f"{user.uuid}"]), format='json')
        self.assertEqual(get_not_auth_resp.status_code, status.HTTP_401_UNAUTHORIZED)

        self._login(email=user.email, password=USER_PASSWORD)
        get_auth_resp = self.client.delete(reverse("core:users-detail", args=[f"{user.uuid}"]), format='json')
        self.assertEqual(get_auth_resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_set_password(self):
        """
        Test case for setting a user's password.

        This test verifies that a user's password can be successfully set by making a POST request to the
        'core:users-set-password' endpoint. It checks the response status codes and ensures that the user
        can log in with the new password.

        Steps:
        1. Create a dictionary containing the new password.
        2. Retrieve a non-superuser user from the database.
        3. Perform authentication tests with and without authentication.
        4. Verify that the response status codes are as expected.
        5. Verify that the user can log in with the new password.

        """
        data = {
            "password": "NewPassword"
        }
        user = KompelloUser.objects.filter(is_superuser=False).first()

        no_auth, auth = self._test_auth_not_auth(
            user,
            {
                "path": reverse("core:users-set-password", args=[f"{user.uuid}"]),
                "data": data,
                "format": "json"
            },
            "post"
        )
        self.assertEqual(no_auth.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(auth.status_code, status.HTTP_200_OK)
        self.assertTrue(self._login(email=user.email, password="NewPassword"))
