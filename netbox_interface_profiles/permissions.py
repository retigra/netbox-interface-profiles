"""
Object permission helpers for interface profile assignments.

Who may assign which profile is controlled by regular NetBox object permissions on Interface Profile
Assignment. Their constraints usually reference the profile group, for example::

    {"interface_profile__group__slug": "access"}

NetBox's generic views and REST API enforce these constraints on their own. The plugin's device tab and HTMX
actions write assignments directly, so they go through `assign_profile()`, which applies the same checks, and
use `restrict_assignable_profiles()` to only offer profiles the user is allowed to assign.
"""

from dcim.models import Interface
from django.core.exceptions import FieldDoesNotExist
from django.db import transaction
from django.db.models import Q
from users.constants import CONSTRAINT_TOKEN_USER
from utilities.exceptions import PermissionsViolation
from utilities.permissions import get_permission_for_model, qs_filter_from_constraints

from .models import InterfaceProfile, InterfaceProfileAssignment

__all__ = (
    "assign_profile",
    "restrict_assignable_profiles",
)


def _get_constraints(user, action: str) -> list[dict] | None:
    """
    Return the user's constraint sets for an assignment action.

    Returns None when the user is unrestricted and an empty list when the user lacks the permission entirely.
    """
    if user.is_active and user.is_superuser:
        return None

    permission = get_permission_for_model(InterfaceProfileAssignment, action)
    if not user.is_authenticated or permission not in user.get_all_permissions():
        return []

    # Populated by get_all_permissions(); this mirrors RestrictedQuerySet.restrict()
    constraints = user._object_perm_cache[permission]
    if not constraints or not all(constraints):
        return None
    return constraints


def _relocate_lookup(key: str, field: str, model) -> str | None:
    """
    Rewrite an assignment lookup on `field` so it applies to `model` directly.

    e.g. `interface_profile__group__slug` -> `group__slug` and `interface_profile__in` -> `pk__in`.
    Returns None when the lookup does not traverse `field`.
    """
    head, _, rest = key.partition("__")
    if head == f"{field}_id":
        return f"pk__{rest}" if rest else "pk"
    if head != field:
        return None
    if not rest:
        return "pk"
    try:
        model._meta.get_field(rest.split("__")[0])
    except FieldDoesNotExist:
        # A lookup such as __in or __exact on the relation itself
        return f"pk__{rest}"
    return rest


def _profile_filter(user, constraints: list[dict], interface: Interface | None) -> Q | None:
    """
    Translate assignment constraints into a filter on InterfaceProfile, or None when no filter applies.

    Interface lookups are evaluated against `interface`; without one they are assumed to match. Lookups on other
    assignment attributes cannot be evaluated before the assignment exists and are left to `assign_profile()`.
    """
    profile_filter = Q(pk__in=[])
    for constraint in constraints:
        profile_lookups, interface_lookups = {}, {}
        for key, value in constraint.items():
            if (lookup := _relocate_lookup(key, "interface_profile", InterfaceProfile)) is not None:
                profile_lookups[lookup] = value
            elif (lookup := _relocate_lookup(key, "interface", Interface)) is not None:
                interface_lookups[lookup] = value

        if interface is not None and interface_lookups:
            interface_q = qs_filter_from_constraints([interface_lookups], {CONSTRAINT_TOKEN_USER: user})
            if not Interface.objects.filter(interface_q, pk=interface.pk).exists():
                continue

        if not profile_lookups:
            return None
        profile_filter |= qs_filter_from_constraints([profile_lookups], {CONSTRAINT_TOKEN_USER: user})

    return profile_filter


def restrict_assignable_profiles(queryset, user, interface: Interface | None = None):
    """
    Narrow an InterfaceProfile queryset to the profiles the user may assign.

    With an interface, its current assignment decides whether add or change permission applies, and a user who
    may not change that assignment gets no profiles at all. Without one (bulk assignment) both are required.
    """
    if interface is None:
        actions = ("add", "change")
    elif assignment := getattr(interface, "profile_assignment", None):
        if not InterfaceProfileAssignment.objects.restrict(user, "change").filter(pk=assignment.pk).exists():
            return queryset.none()
        actions = ("change",)
    else:
        actions = ("add",)

    for action in actions:
        constraints = _get_constraints(user, action)
        if constraints is None:
            continue
        if (profile_filter := _profile_filter(user, constraints, interface)) is not None:
            queryset = queryset.filter(profile_filter)
    return queryset


def assign_profile(user, interface: Interface, profile: InterfaceProfile) -> tuple[InterfaceProfileAssignment, bool]:
    """
    Create or update the interface's profile assignment within the user's object permissions.

    The existing assignment must be changeable by the user, and the saved result must satisfy their add or change
    constraints. Otherwise PermissionsViolation is raised and the save, including the interface changes made by
    the post_save sync, is rolled back.

    Returns the assignment and whether it was created.
    """
    with transaction.atomic():
        assignment = InterfaceProfileAssignment.objects.filter(interface=interface).first()
        created = assignment is None
        if created:
            assignment = InterfaceProfileAssignment(interface=interface)
        else:
            if not InterfaceProfileAssignment.objects.restrict(user, "change").filter(pk=assignment.pk).exists():
                raise PermissionsViolation()
            assignment.snapshot()

        assignment.interface_profile = profile
        assignment.save()

        action = "add" if created else "change"
        if not InterfaceProfileAssignment.objects.restrict(user, action).filter(pk=assignment.pk).exists():
            raise PermissionsViolation()

    return assignment, created
