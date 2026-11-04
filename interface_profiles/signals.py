"""Signal handlers for interface role assignments."""

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import InterfaceRoleAssignment
from .services import sync_assignment


@receiver(post_save, sender=InterfaceRoleAssignment)
def apply_interface_template_on_assignment(
    sender,
    instance: InterfaceRoleAssignment,
    created: bool,
    **kwargs,
) -> None:
    """Apply a matching template whenever a role assignment is created/updated."""
    if not created and kwargs.get("update_fields") == {"last_updated"}:
        return

    assignment = (
        InterfaceRoleAssignment.objects.select_related(
            "interface__device__site",
            "interface_role",
        )
        .prefetch_related("interface__tagged_vlans")
        .get(pk=instance.pk)
    )

    sync_assignment(assignment=assignment, commit=True)
