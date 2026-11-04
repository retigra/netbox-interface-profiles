"""
ProfileConfigTemplate model for interface profiles.
"""

from typing import Any, cast

from django.db import models
from django.urls import reverse
from extras.models.mixins import RenderTemplateMixin
from netbox.models import NetBoxModel
from netbox.models.features import SyncedDataMixin
from utilities.querysets import RestrictedQuerySet


class ProfileConfigTemplateQuerySet(RestrictedQuerySet):
    def in_scope(self, interface):
        """
        Return the config templates whose scope matches an interface, regardless of their interface role.

        A template is in scope when its platform matches, its device type is empty or matches, and all of its
        device and interface tags are present on the device and interface respectively.
        """
        device = interface.device

        if device.platform_id is None:
            return self.none()

        return (
            self.filter(platform_id=device.platform_id)
            .filter(models.Q(device_type__isnull=True) | models.Q(device_type_id=device.device_type_id))
            .exclude(device_tags__in=self._missing_tags(device))
            .exclude(interface_tags__in=self._missing_tags(interface))
        )

    def for_interface(self, interface, interface_role=None):
        """
        Return the config templates applicable to an interface, highest weight first.

        A template applies when it is in scope of the interface (see in_scope()) and its interface role matches.
        The interface role defaults to the role assigned to the interface.
        """
        if interface_role is None:
            assignment = getattr(interface, "role_assignment", None)
            interface_role = getattr(assignment, "interface_role", None)
        if interface_role is None:
            return self.none()

        return (
            self.in_scope(interface).filter(interface_role=interface_role).distinct().order_by("-weight", "name", "pk")
        )

    @staticmethod
    def _missing_tags(obj):
        from extras.models import Tag

        return Tag.objects.exclude(pk__in=[tag.pk for tag in obj.tags.all()])


class ProfileConfigTemplate(SyncedDataMixin, RenderTemplateMixin, NetBoxModel):
    """
    A Jinja2 template rendering the configuration of interfaces with an InterfaceRole on a Platform, optionally
    narrowed down by DeviceType and device and interface tags. When multiple templates apply, the highest weight wins.

    Like NetBox config templates, the template code is stored locally or synchronized from a data file.
    """

    interface_role = models.ForeignKey(
        to="interface_profiles.InterfaceRole",
        on_delete=models.CASCADE,
        related_name="config_templates",
    )
    platform = models.ForeignKey(
        to="dcim.Platform",
        on_delete=models.PROTECT,
        related_name="interface_profile_config_templates",
    )
    device_type = models.ForeignKey(
        to="dcim.DeviceType",
        on_delete=models.PROTECT,
        related_name="interface_profile_config_templates",
        null=True,
        blank=True,
    )
    device_tags = models.ManyToManyField(
        to="extras.Tag",
        related_name="+",
        blank=True,
        help_text="If specified, the template only applies to devices with all of these tags.",
    )
    interface_tags = models.ManyToManyField(
        to="extras.Tag",
        related_name="+",
        blank=True,
        help_text="If specified, the template only applies to interfaces with all of these tags.",
    )
    weight = models.PositiveSmallIntegerField(
        default=1000,
        help_text="When multiple templates apply to an interface, the template with the highest weight is used.",
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    debug = models.BooleanField(
        default=False,
        help_text="Enable verbose error output when rendering this template. Not recommended for production use.",
    )

    # Rendered output is embedded in the device configuration, never served as a file
    mime_type = None
    file_name = None
    file_extension = None
    as_attachment = None

    objects = cast(Any, ProfileConfigTemplateQuerySet).as_manager()

    class Meta:
        ordering = ("interface_role", "platform", "-weight", "name")
        verbose_name = "Profile Config Template"
        verbose_name_plural = "Profile Config Templates"
        permissions = (("sync", "Synchronize data from remote source"),)

    def __str__(self) -> str:
        return f"{self.name}"

    def get_absolute_url(self) -> str:
        return reverse("plugins:interface_profiles:profileconfigtemplate", args=[self.pk])

    def sync_data(self):
        """
        Synchronize template content from the designated DataFile (if any).
        """
        self.template_code = self.validate_synced_value("template_code", cast(Any, self.data_file).data_as_string)

    cast(Any, sync_data).alters_data = True

    def format_render_error(self, exc: Exception) -> str:
        """
        Format a rendering error like NetBox config templates do: a full (sanitized) traceback in debug mode,
        otherwise a concise message.
        """
        from extras.models import ConfigTemplate

        return ConfigTemplate.format_render_error(cast(Any, self), exc)

    def get_environment_params(self):
        """
        Interface configuration is plain text, so autoescape is always disabled (as for NetBox config templates).
        """
        params = super().get_environment_params()
        params["autoescape"] = False
        return params
