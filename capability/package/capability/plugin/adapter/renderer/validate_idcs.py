from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


class ValidateIdcsRenderer:
    def render(self, console: Console, result: dict, format: str = "rich"):
        passed = result.get("org.local.domain.idcs.validation.passed")
        summary = result.get("org.local.domain.idcs.validation.summary", {}) or {}

        if format == "json":
            import json

            print(json.dumps(result, indent=2))
            return

        status_text = Text("PASSED", style="bold green") if passed else Text("FAILED", style="bold red")

        idcs_path = str(summary.get("idcs_path", "") or "")
        ifc_path = str(summary.get("ifc_path", "") or "")

        header = Text()
        header.append("IDCS Validation: ", style="bold")
        header.append(status_text)
        if idcs_path:
            header.append("\nIDCS: ", style="bold")
            header.append(idcs_path, style="cyan")
        if ifc_path:
            header.append("\nIFC: ", style="bold")
            header.append(ifc_path, style="cyan")

        target_width = max(len(line) for line in header.plain.splitlines()) + 4
        console.print(Panel(header, width=target_width, expand=False))

        totals = Text()
        totals.append("Constraints — Total: ", style="bold")
        totals.append(str(summary.get("constraints_total", 0)))
        totals.append("  Passed: ", style="bold")
        totals.append(str(summary.get("constraints_passed", 0)), style="green")
        totals.append("  Failed: ", style="bold")
        totals.append(str(summary.get("constraints_failed", 0)), style="red")
        totals.append("  Unknown: ", style="bold")
        totals.append(str(summary.get("constraints_unknown", 0)), style="yellow")
        console.print(totals)

        inst = Text()
        inst.append("Instances  — Total: ", style="bold")
        inst.append(str(summary.get("objects_total", 0)))
        inst.append("  Passed: ", style="bold")
        inst.append(str(summary.get("objects_passed", 0)), style="green")
        inst.append("  Failed: ", style="bold")
        inst.append(str(summary.get("objects_failed", 0)), style="red")
        inst.append("  Unknown: ", style="bold")
        inst.append(str(summary.get("objects_unknown", 0)), style="yellow")
        console.print(inst)

        table = Table(title="Constraints", expand=True, show_lines=False)
        table.add_column("Name", style="cyan", overflow="fold")
        table.add_column("Status", overflow="fold")
        table.add_column("IFC Class", style="magenta", overflow="fold")
        table.add_column("Applicable", justify="right", overflow="fold")
        table.add_column("Passed", justify="right", style="green", overflow="fold")
        table.add_column("Failed", justify="right", style="red", overflow="fold")
        table.add_column("Unknown", justify="right", style="yellow", overflow="fold")

        for c in summary.get("constraints", []) or []:
            status = c.get("status", "unknown")
            if status == "passed":
                status_txt = Text("passed", style="green")
            elif status == "failed":
                status_txt = Text("failed", style="red")
            else:
                status_txt = Text("unknown", style="yellow")

            table.add_row(
                str(c.get("constraintName", "")),
                status_txt,
                str(c.get("ifcClass", "")),
                str(c.get("applicable_entities", 0)),
                str(c.get("passed_entities", 0)),
                str(c.get("failed_entities", 0)),
                str(c.get("unknown_entities", 0)),
            )

        console.print(table)

        examples = []
        for c in summary.get("constraints", []) or []:
            for ex in c.get("examples", []) or []:
                examples.append(
                    {
                        "constraintName": c.get("constraintName", ""),
                        "entity": ex.get("entity", ""),
                        "status": ex.get("status", ""),
                        "expr": ex.get("expr", ""),
                        "values": ex.get("values", {}),
                    }
                )

        if examples:
            status_order = {"failed": 0, "unknown": 1, "passed": 2}
            examples.sort(key=lambda x: (status_order.get(x.get("status", "unknown"), 1), x.get("constraintName", ""), x.get("entity", "")))
            et = Table(title="Details", expand=True, show_lines=True)
            et.add_column("Constraint", style="cyan", overflow="fold")
            et.add_column("Entity", style="magenta", overflow="fold")
            et.add_column("Status", overflow="fold")
            et.add_column("Expr", style="dim", overflow="fold")
            et.add_column("Values", overflow="fold")
            for ex in examples:
                status = ex.get("status", "unknown")
                if status == "passed":
                    s_txt = Text("passed", style="green")
                elif status == "failed":
                    s_txt = Text("failed", style="red")
                else:
                    s_txt = Text("unknown", style="yellow")
                vals_map = ex.get("values") or {}
                vm_text = Text()
                if vals_map:
                    first = True
                    for k in sorted(vals_map.keys()):
                        if not first:
                            vm_text.append(", ")
                        first = False
                        vm_text.append(k, style="bold")
                        vm_text.append("=")
                        entry = vals_map[k]
                        if isinstance(entry, dict) and entry.get("missing"):
                            vm_text.append("missing", style="yellow")
                        else:
                            val = entry.get("value") if isinstance(entry, dict) else entry
                            vm_text.append(str(val))
                et.add_row(
                    str(ex.get("constraintName", "")),
                    str(ex.get("entity", "")),
                    s_txt,
                    str(ex.get("expr", "")),
                    vm_text,
                )
            console.print(et)
