"""
Abstract base model inherited by every model in this project.
Provides UUID primary key and automatic timestamps.
"""
import uuid
from django.db import models


class BaseModel(models.Model):
    """
    Abstract model that provides:
    - UUID primary key (safe to expose in URLs, not guessable)
    - created_at (set once when record is created, never changes)
    - updated_at (automatically updated every time the record is saved)
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for this record."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when this record was created."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when this record was last updated."
    )

    class Meta:
        # abstract=True means Django will NOT create a database table for
        # BaseModel itself. It only adds these fields to models that inherit it.
        abstract = True
        ordering = ['-created_at']  # Newest records first by default