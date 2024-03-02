import uuid as uuid

from auditlog.models import AuditlogHistoryField
from django.db import models


class BaseModel(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    modified_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class HistoryModel(models.Model):
    history = AuditlogHistoryField()

    class Meta:
        abstract = True
