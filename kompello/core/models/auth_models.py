from django.contrib.auth.models import AbstractUser
from django.db import models
from kompello.core.models.base_models import BaseModel, HistoryModel


class KompelloUser(BaseModel, HistoryModel, AbstractUser):
    email = models.EmailField(unique=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

class KompelloUserSocialAuths(BaseModel):
    user = models.ForeignKey(KompelloUser, on_delete=models.CASCADE, related_name="social_auths")
    provider = models.CharField(max_length=255, null=False, blank=False)
    sub = models.CharField(max_length=255, null=False, blank=False)

    class Meta:
        unique_together = [["provider", "sub", "user"]]

class Tenant(BaseModel, HistoryModel):
    slug = models.CharField(max_length=255, null=False, blank=False)
    name = models.CharField(max_length=255, null=False, blank=False)
    users = models.ManyToManyField(KompelloUser, related_name="tenants")
