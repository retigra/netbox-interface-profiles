"""Background jobs for netbox interface profiles."""

from __future__ import annotations

from typing import NoReturn

from core.exceptions import JobFailed
from django.core.exceptions import ObjectDoesNotExist
from netbox.jobs import JobRunner
from utilities.exceptions import AbortRequest

from .models import ProfileSync
from .services import run_profile_sync


class SyncInterfaceProfileJob(JobRunner):
    """Synchronize all interfaces assigned to an interface profile.

    The job runs for a ProfileSync created alongside it; the changed interfaces are recorded on
    that ProfileSync and shown on its detail page.
    """

    class Meta:
        name = "Synchronize Interface Profile"

    def _fail(self, message: str, exc: Exception) -> NoReturn:
        """Fail the job, keeping the reason on the job so the synchronization page can show it."""
        self.logger.error(message)
        self.job.error = message
        raise JobFailed(message) from exc

    def run(self, *args, **kwargs) -> None:
        """Synchronize assignments for the related profile and record the changes."""
        try:
            sync = ProfileSync.objects.select_related("interface_profile").get(job=self.job)
        except ObjectDoesNotExist as exc:
            self._fail("No profile synchronization is linked to this job.", exc)

        self.logger.info(
            f"Starting interface profile synchronization for {sync.interface_profile} (dry_run={sync.dry_run})"
        )

        try:
            changes = run_profile_sync(sync)
        except AbortRequest as exc:
            self._fail(exc.message, exc)
        except Exception as exc:
            self._fail(f"Synchronization failed and was rolled back: {exc}", exc)

        verb = "would change" if sync.dry_run else "changed"
        self.logger.info(f"Synchronization {verb} {len(changes)} of {sync.interface_count} interface(s).")
        self.logger.info(f"Review the changes at {sync.get_absolute_url()}")
