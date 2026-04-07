"""Signal handlers for interface profile assignments."""

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import InterfaceProfileAssignment
from .services import sync_assignment


@receiver(post_save, sender=InterfaceProfileAssignment)
def apply_interface_template_on_assignment(
    sender,
    instance: InterfaceProfileAssignment,
    created: bool,
    **kwargs,
) -> None:
    """Apply a matching template whenever a profile assignment is created/updated."""
    if not created and kwargs.get("update_fields") == {"last_updated"}:
        return

    assignment = (
        InterfaceProfileAssignment.objects.select_related(
            "interface__device__site",
            "interface_profile",
        )
        .prefetch_related("interface__tagged_vlans")
        .get(pk=instance.pk)
    )

    sync_assignment(assignment=assignment, commit=True)
