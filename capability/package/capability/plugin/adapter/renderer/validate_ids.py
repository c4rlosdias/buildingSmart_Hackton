from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


class ValidateIdsRenderer:
    def render(self, console: Console, result: dict, format: str = "rich"):
        passed = result.get("org.local.domain.ids.validation.passed")
        summary = result.get("org.local.domain.ids.validation.summary", {}) or {}

        if format == "json":
            import json

            print(json.dumps(result, indent=2))
            return

        status_text = Text("PASSED", style="bold green") if passed else Text("FAILED", style="bold red")

        subtitle = Text()
        ids_path = summary.get("ids_path", "")
        ifc_path = summary.get("ifc_path", "")
        if ids_path:
            subtitle.append("IDS: ", style="bold")
            subtitle.append(str(ids_path), style="cyan")
        if ifc_path:
            if subtitle.plain:
                subtitle.append("\n")
            subtitle.append("IFC: ", style="bold")
            subtitle.append(str(ifc_path), style="cyan")

        console.print(Panel.fit(Text.assemble("IDS Validation: ", status_text), subtitle=subtitle))

        table = Table(title="Specifications")
        table.add_column("Name", style="cyan")
        table.add_column("Status")
        table.add_column("Applicable", justify="right")
        table.add_column("Passed", justify="right", style="green")
        table.add_column("Failed", justify="right", style="red")
        table.add_column("Failures", justify="right", style="yellow")

        for spec in summary.get("specifications", []) or []:
            spec_status = spec.get("status", "unknown")
            if spec_status == "passed":
                spec_status_txt = Text("passed", style="green")
            elif spec_status == "failed":
                spec_status_txt = Text("failed", style="red")
            else:
                spec_status_txt = Text("unknown", style="yellow")

            table.add_row(
                str(spec.get("name", "")),
                spec_status_txt,
                str(spec.get("applicable_entities", 0)),
                str(spec.get("passed_entities", 0)),
                str(spec.get("failed_entities", 0)),
                str(spec.get("requirement_failures", 0)),
            )

        console.print(table)

        totals = Text()
        totals.append("Total: ", style="bold")
        totals.append(str(summary.get("specifications_total", 0)))
        totals.append("  Passed: ", style="bold")
        totals.append(str(summary.get("specifications_passed", 0)), style="green")
        totals.append("  Failed: ", style="bold")
        totals.append(str(summary.get("specifications_failed", 0)), style="red")
        if "specifications_unknown" in summary:
            totals.append("  Unknown: ", style="bold")
            totals.append(str(summary.get("specifications_unknown", 0)), style="yellow")

        console.print(totals)
