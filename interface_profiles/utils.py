"""Utility helpers for interface profiles."""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.contenttypes.models import ContentType
from django.db.models import Case, IntegerField, Q, Value, When
from ipam.models import VLAN

if TYPE_CHECKING:
    from dcim.models import Site


def _site_vlan_scope_query(site: Site) -> Q:
    """Build a query for VLANs relevant to the provided site."""
    site_ct = ContentType.objects.get_for_model(site.__class__)

    query = Q(site=site)
    query |= Q(group__scope_type=site_ct, group__scope_id=site.pk)

    site_group_id = getattr(site, "group_id", None)
    if site_group_id:
        from dcim.models import SiteGroup

        site_group_ct = ContentType.objects.get_for_model(SiteGroup)
        query |= Q(group__scope_type=site_group_ct, group__scope_id=site_group_id)

    return query


def resolve_vlan_by_vid(site: Site, vid: int | None, qinq_role: str | None = None) -> VLAN | None:
    """
    Resolve a single VLAN object by VID for a site context, optionally limited to VLANs with a Q-in-Q role.

    Resolution priority:
    1. VLAN explicitly assigned to the site
    2. VLAN in a VLANGroup scoped to the site
    3. VLAN in a VLANGroup scoped to the site's SiteGroup
    """
    if not site or not vid:
        return None

    queryset = VLAN.objects.filter(vid=vid).filter(_site_vlan_scope_query(site))
    if qinq_role is not None:
        queryset = queryset.filter(qinq_role=qinq_role)
    return queryset.order_by(
        Case(
            When(site=site, then=Value(0)),
            default=Value(1),
            output_field=IntegerField(),
        ),
        "pk",
    ).first()


def resolve_vlans_by_vids(site: Site, vids: list[int]) -> list[VLAN]:
    """Resolve multiple VLAN objects by VID for a site context."""
    if not site:
        return []

    filtered_vids = sorted({vid for vid in vids if vid})
    if not filtered_vids:
        return []

    vlan_map: dict[int, VLAN] = {}
    queryset = (
        VLAN.objects.filter(vid__in=filtered_vids)
        .filter(_site_vlan_scope_query(site))
        .order_by(
            Case(
                When(site=site, then=Value(0)),
                default=Value(1),
                output_field=IntegerField(),
            ),
            "pk",
        )
    )

    for vlan in queryset:
        vlan_map.setdefault(vlan.vid, vlan)

    return [vlan_map[vid] for vid in filtered_vids if vid in vlan_map]
