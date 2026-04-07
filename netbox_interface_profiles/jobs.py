"""Background jobs for netbox interface profiles."""

from __future__ import annotations

from core.exceptions import JobFailed
from netbox.jobs import JobRunner

from .models import InterfaceProfile
from .services import format_diff_value, sync_assignments_for_profile


class SyncInterfaceProfileJob(JobRunner):
    """Synchronize all interfaces assigned to an interface profile."""

    class Meta:
        name = "Synchronize Interface Profile"

    def run(self, dry_run: bool = True, profile_id: int | None = None, *args, **kwargs) -> None:
        """Synchronize assignments for the related profile and log diffs."""
        if profile_id is None:
            raise JobFailed("No interface profile ID was provided for this job run.")

        profile = InterfaceProfile.objects.get(pk=profile_id)
        self.logger.info(
            "Starting interface profile synchronization for %s (dry_run=%s)",
            profile,
            dry_run,
        )

        try:
            rows = sync_assignments_for_profile(profile=profile, dry_run=dry_run)
        except Exception as exc:
            raise JobFailed(f"Synchronization failed and was rolled back: {exc}") from exc

        if not rows:
            self.logger.info("No interface attribute changes were required.")
            return

        self.logger.info("Detected %d changed field value(s).", len(rows))
        self.logger.info("| Interface | Attribute | Old Value | New Value |")
        self.logger.info("|---|---|---|---|")
        for row in rows:
            interface = str(row["interface"]).replace("|", "\\|")
            field = str(row["field"]).replace("|", "\\|")
            old_value = format_diff_value(row["old"]).replace("|", "\\|")
            new_value = format_diff_value(row["new"]).replace("|", "\\|")
            self.logger.info(f"| {interface} | {field} | {old_value} | {new_value} |")

        if dry_run:
            self.logger.info("Dry-run complete. All computed changes were rolled back.")
        else:
            self.logger.info("Synchronization complete. Changes were committed.")
