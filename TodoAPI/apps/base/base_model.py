import uuid

from django.conf import settings
from django.db import models


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="%(class)s_created",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="%(class)s_updated",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True
