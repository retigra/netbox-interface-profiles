"""
ProfileSync models for netbox interface profiles.

A ProfileSync records one synchronization run of an InterfaceProfile, and a ProfileSyncChange
records the state of one interface before and after that run (in the same format NetBox uses
for changelog pre/post-change data). Dry runs are recorded as well, so users can review the
changes a synchronization would make before committing them.
"""

from typing import Any, cast

from core.choices import JobStatusChoices
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.urls import reverse
from utilities.querysets import RestrictedQuerySet

# Serialized attributes which differ between snapshots without being an interface change
DIFF_EXCLUDE_FIELDS = {"created", "last_updated"}


class ProfileSync(models.Model):
    """A single (dry-run or committed) synchronization run of an InterfaceProfile."""

    interface_profile = models.ForeignKey(
        to="netbox_interface_profiles.InterfaceProfile",
        on_delete=models.CASCADE,
        related_name="syncs",
    )
    job = models.OneToOneField(
        to="core.Job",
        on_delete=models.CASCADE,
        related_name="interface_profile_sync",
    )
    dry_run = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    interface_count = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Number of interfaces assigned to the profile when the synchronization ran.",
    )

    objects = cast(Any, RestrictedQuerySet).as_manager()

    class Meta:
        ordering = ("-created",)
        verbose_name = "Profile Synchronization"
        verbose_name_plural = "Profile Synchronizations"

    def __str__(self) -> str:
        return f"{self.interface_profile} #{self.pk}"

    def get_absolute_url(self) -> str:
        return reverse("plugins:netbox_interface_profiles:profilesync", args=[self.pk])

    # The sync's status is that of its job

    @property
    def status(self) -> str:
        return cast(Any, self.job).status

    def get_status_display(self) -> str:
        return cast(Any, self.job).get_status_display()

    def get_status_color(self) -> str:
        return cast(Any, self.job).get_status_color()

    @property
    def is_finished(self) -> bool:
        return self.status in JobStatusChoices.TERMINAL_STATE_CHOICES

    @property
    def is_completed(self) -> bool:
        return self.status == JobStatusChoices.STATUS_COMPLETED


class ProfileSyncChange(models.Model):
    """The state of one interface before and after a ProfileSync."""

    sync = models.ForeignKey(
        to="netbox_interface_profiles.ProfileSync",
        on_delete=models.CASCADE,
        related_name="changes",
    )
    interface = models.ForeignKey(
        to="dcim.Interface",
        on_delete=models.SET_NULL,
        related_name="+",
        blank=True,
        null=True,
    )
    # Names are kept so the record stays readable after the interface is renamed or deleted
    device_name = models.CharField(max_length=100, blank=True)
    interface_name = models.CharField(max_length=100)
    prechange_data = models.JSONField(encoder=DjangoJSONEncoder)
    postchange_data = models.JSONField(encoder=DjangoJSONEncoder)

    objects = cast(Any, RestrictedQuerySet).as_manager()

    class Meta:
        ordering = ("sync", "pk")
        verbose_name = "Profile Synchronization Change"
        verbose_name_plural = "Profile Synchronization Changes"

    def __str__(self) -> str:
        return f"{self.device_name} {self.interface_name}"

    def diff(self) -> dict[str, tuple]:
        """Return the (pre, post) values of every serialized attribute that changed."""

        def normalize(value):
            # Many-to-many relations serialize as lists of primary keys in no guaranteed order
            return sorted(value, key=str) if isinstance(value, list) else value

        pre, post = cast(dict, self.prechange_data), cast(dict, self.postchange_data)
        return {
            key: (pre.get(key), post.get(key))
            for key in sorted(pre.keys() | post.keys())
            if key not in DIFF_EXCLUDE_FIELDS
            and not key.startswith("_")
            and normalize(pre.get(key)) != normalize(post.get(key))
        }
