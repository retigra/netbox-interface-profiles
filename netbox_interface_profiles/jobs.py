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

    @staticmethod
    def _build_ascii_table(rows: list[dict[str, object]]) -> list[str]:
        """Render change rows as a plain text table for job logs."""

        headers = ("Interface", "Attribute", "Old Value", "New Value")
        table_rows = [
            (
                str(row["interface"]),
                str(row["field"]),
                format_diff_value(row["old"]),
                format_diff_value(row["new"]),
            )
            for row in rows
        ]

        widths = [len(header) for header in headers]
        for values in table_rows:
            for i, value in enumerate(values):
                widths[i] = max(widths[i], len(value))

        def render_row(values: tuple[str, str, str, str]) -> str:
            return "| " + " | ".join(value.ljust(widths[i]) for i, value in enumerate(values)) + " |"

        separator = "+-" + "-+-".join("-" * width for width in widths) + "-+"
        lines = [separator, render_row(headers), separator]
        lines.extend(render_row(values) for values in table_rows)
        lines.append(separator)
        return lines

    def run(self, dry_run: bool = True, profile_id: int | None = None, *args, **kwargs) -> None:
        """Synchronize assignments for the related profile and log diffs."""
        if profile_id is None:
            raise JobFailed("No interface profile ID was provided for this job run.")

        profile = InterfaceProfile.objects.get(pk=profile_id)
        self.logger.info(f"Starting interface profile synchronization for {profile} (dry_run={dry_run})")

        try:
            rows = sync_assignments_for_profile(profile=profile, dry_run=dry_run)
        except Exception as exc:
            raise JobFailed(f"Synchronization failed and was rolled back: {exc}") from exc

        if not rows:
            self.logger.info("No interface attribute changes were required.")
            return

        self.logger.info(f"Detected {len(rows)} changed field value(s).")
        for line in self._build_ascii_table(rows):
            self.logger.info(line)

        if dry_run:
            self.logger.info("Dry-run complete. All computed changes were rolled back.")
        else:
            self.logger.info("Synchronization complete. Changes were committed.")
