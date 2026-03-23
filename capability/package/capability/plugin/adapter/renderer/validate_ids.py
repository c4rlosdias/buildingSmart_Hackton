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

        ids_path = str(summary.get("ids_path", "") or "")
        ifc_path = str(summary.get("ifc_path", "") or "")

        header = Text()
        header.append("IDS Validation: ", style="bold")
        header.append(status_text)
        if ids_path:
            header.append("\nIDS: ", style="bold")
            header.append(ids_path, style="cyan")
        if ifc_path:
            header.append("\nIFC: ", style="bold")
            header.append(ifc_path, style="cyan")

        target_width = max(len(line) for line in header.plain.splitlines()) + 4
        console.print(Panel(header, width=target_width, expand=False))

        if "error" in summary:
            error_lines = Text()
            error_lines.append(str(summary.get("error_type", "Error")), style="bold red")
            error_lines.append("\n")
            error_lines.append(str(summary.get("error", "")))
            if summary.get("xml_error"):
                error_lines.append("\n\n")
                error_lines.append(str(summary.get("xml_error")), style="dim")
            console.print(Panel(error_lines, title="IDS Load Error", border_style="red"))
            return

        totals = Text()
        totals.append("Specifications — Total: ", style="bold")
        totals.append(str(summary.get("specifications_total", 0)))
        totals.append("  Passed: ", style="bold")
        totals.append(str(summary.get("specifications_passed", 0)), style="green")
        totals.append("  Failed: ", style="bold")
        totals.append(str(summary.get("specifications_failed", 0)), style="red")
        totals.append("  Unknown: ", style="bold")
        totals.append(str(summary.get("specifications_unknown", 0)), style="yellow")
        console.print(totals)

        inst = Text()
        inst.append("Instances      — Total: ", style="bold")
        inst.append(str(summary.get("objects_total", 0)))
        inst.append("  Passed: ", style="bold")
        inst.append(str(summary.get("objects_passed", 0)), style="green")
        inst.append("  Failed: ", style="bold")
        inst.append(str(summary.get("objects_failed", 0)), style="red")
        inst.append("  Unknown: ", style="bold")
        inst.append(str(summary.get("objects_unknown", 0)), style="yellow")
        console.print(inst)

        table = Table(title="Specifications", expand=True, show_lines=False)
        table.add_column("Name", style="cyan", overflow="fold")
        table.add_column("Status", overflow="fold")
        table.add_column("Applicable", justify="right", overflow="fold")
        table.add_column("Passed", justify="right", style="green", overflow="fold")
        table.add_column("Failed", justify="right", style="red", overflow="fold")
        table.add_column("Unknown", justify="right", style="yellow", overflow="fold")
        table.add_column("Failures", justify="right", style="yellow", overflow="fold")

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
                str(spec.get("unknown_entities", 0)),
                str(spec.get("requirement_failures", 0)),
            )

        console.print(table)

        examples = []
        for spec in summary.get("specifications", []) or []:
            for ex in spec.get("examples", []) or []:
                examples.append(
                    {
                        "specification": spec.get("name", ""),
                        "entity": ex.get("entity", ""),
                        "status": ex.get("status", ""),
                    }
                )

        if examples:
            status_order = {"failed": 0, "unknown": 1, "passed": 2}
            examples.sort(
                key=lambda x: (
                    status_order.get(x.get("status", "unknown"), 1),
                    x.get("specification", ""),
                    x.get("entity", ""),
                )
            )
            et = Table(title="Details", expand=True, show_lines=True)
            et.add_column("Specification", style="cyan", overflow="fold")
            et.add_column("Entity", style="magenta", overflow="fold")
            et.add_column("Status", overflow="fold")
            for ex in examples:
                status = ex.get("status", "unknown")
                if status == "passed":
                    s_txt = Text("passed", style="green")
                elif status == "failed":
                    s_txt = Text("failed", style="red")
                else:
                    s_txt = Text("unknown", style="yellow")
                et.add_row(
                    str(ex.get("specification", "")),
                    str(ex.get("entity", "")),
                    s_txt,
                )
            console.print(et)
