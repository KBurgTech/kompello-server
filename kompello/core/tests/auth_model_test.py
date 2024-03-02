from django.db import IntegrityError
from kompello.core.models.auth_models import KompelloUser, Tenant, KompelloUserSocialAuths
from kompello.core.tests.helpers import BaseTestCase


class AuthModelTest(BaseTestCase):
    def setUp(self):
        self.admin_users = self._create_admin_user(1)
        self.users = self._create_user(5)
        self.tenants = self._create_tenant(5)

        KompelloUserSocialAuths.objects.create(user=self.users[0], provider="providerY-oauth2", sub="1234")
        KompelloUserSocialAuths.objects.create(user=self.users[1], provider="providerX-oauth2", sub="5678")
        KompelloUserSocialAuths.objects.create(user=self.users[2], provider="providerZ-oauth2", sub="9012")

    def test_user_has_uuid(self):
        """
        Test that each user and admin user has a non-null UUID.

        This test iterates over the list of users and admin users, retrieves the corresponding
        KompelloUser object from the database using their email, and asserts that the UUID
        attribute of the object is not None.
        """
        for user in self.users:
            obj = KompelloUser.objects.get(email=user.email)
            self.assertIsNotNone(obj.uuid)

        for user in self.admin_users:
            obj = KompelloUser.objects.get(email=user.email)
            self.assertIsNotNone(obj.uuid)

    def test_user_has_social(self):
        """
        Test that a user has a social authentication.

        This test verifies that a user has a social authentication by checking the count of social_auths
        associated with the user and asserting that the first social_auth has the expected provider and sub values.
        """
        user = KompelloUser.objects.get(email=self.users[0].email)
        self.assertEqual(user.social_auths.count(), 1)
        self.assertEqual(user.social_auths.first().provider, "providerY-oauth2")
        self.assertEqual(user.social_auths.first().sub, "1234")

    def test_same_social_provider(self):
        """
        Test case to verify that creating a new KompelloUserSocialAuths with the same social provider raises an IntegrityError.
        """
        with self.assertRaises(IntegrityError):
            KompelloUserSocialAuths.objects.create(user=self.users[0], provider="providerY-oauth2", sub="1234")

    def test_tenant_has_uuid(self):
        """
        Test case to verify that a Tenant object has a non-null UUID.
        """
        obj = Tenant.objects.get(slug="slug1")
        self.assertIsNotNone(obj.uuid)
