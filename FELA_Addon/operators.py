import bpy
import os
import json
import webbrowser
import bonsai.tool as tool
from capability.plugin.capability.validate_ids import ValidateIdsCapability
from .utils import run_infobim_capability, add_elements


class IFC_OT_ExecutarExterno(bpy.types.Operator):
    bl_idname = "ifc.executar_externo"
    bl_label = "Run infobim"
    bl_description = "Executa: infobim run --ifc-path <arquivo IFC>"

    def execute(self, context):
        ifcfilepath = ""
        props = context.scene.ifc_props
        if hasattr(context.scene, "BIMProperties"):
            ifcfilepath = bpy.path.abspath(context.scene.BIMProperties.ifc_file)

        if not ifcfilepath:
            self.report({"ERROR"}, "No IFC file found. Open an IFC file in BlenderBIM or select one manually.")
            return {"CANCELLED"}

        if not os.path.isfile(ifcfilepath):
            self.report({"ERROR"}, f"IFC file not found: {ifcfilepath}")
            return {"CANCELLED"}

        try:
            resultado = run_infobim_capability(
                ValidateIdsCapability(),
                ifc_path=ifcfilepath,
                ids_path=props.specfilepath,
            )
            with open("resultado.json", "w", encoding="utf-8") as f:
                json.dump(resultado, f, ensure_ascii=False, indent=4)

            #add_elements(context, resultado)

        except Exception as e:
            self.report({"ERROR"}, f"Failed to execute infobim: {e}")
            return {"CANCELLED"}

        return {"FINISHED"}

def build_html_report(report_data, ifc_file, spec_file):
    summary = report_data.get("org.local.domain.ids.validation.summary", {})
    overall_passed = report_data.get("org.local.domain.ids.validation.passed", False)

    spec_total = summary.get("specifications_total", 0)
    spec_passed = summary.get("specifications_passed", 0)
    spec_failed = summary.get("specifications_failed", 0)
    spec_unknown = summary.get("specifications_unknown", 0)
    specifications = summary.get("specifications", [])

    overall_badge_color = "#27AE60" if overall_passed else "#E74C3C"
    overall_label = "PASSED" if overall_passed else "FAILED"

    spec_rows = ""
    for spec in specifications:
        name = spec.get("name", "-")
        status = spec.get("status", "-")
        applicable = spec.get("applicable_entities", 0)
        passed_ent = spec.get("passed_entities", 0)
        failed_ent = spec.get("failed_entities", 0)
        req_failures = spec.get("requirement_failures", 0)

        status_color = "#27AE60" if status == "passed" else "#E74C3C"
        pct = round((passed_ent / applicable * 100) if applicable else 0)
        bar_color = "#27AE60" if pct == 100 else ("#F39C12" if pct > 0 else "#E74C3C")

        spec_rows += f"""
                <tr>
                    <td>{name}</td>
                    <td style="text-align:center;">
                        <span style="background:{status_color};color:#fff;padding:3px 10px;border-radius:12px;font-size:0.85em;font-weight:bold;">
                            {status.upper()}
                        </span>
                    </td>
                    <td style="text-align:center;">{applicable}</td>
                    <td style="text-align:center;">{passed_ent}</td>
                    <td style="text-align:center;">{failed_ent}</td>
                    <td style="text-align:center;">{req_failures}</td>
                    <td style="text-align:center;min-width:120px;">
                        <div style="background:#ddd;border-radius:6px;height:14px;width:100%;">
                            <div style="background:{bar_color};width:{pct}%;height:14px;border-radius:6px;"></div>
                        </div>
                        <small>{pct}%</small>
                    </td>
                </tr>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>IDS Validation Report</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #F4F6F9; color: #2C3E50; }}
        .header {{ background: #2E86C1; color: white; padding: 30px 40px; }}
        .header h1 {{ font-size: 1.8em; font-weight: 700; }}
        .header p {{ font-size: 0.95em; opacity: 0.85; margin-top: 4px; }}
        .badge {{ display:inline-block; background:{overall_badge_color}; color:#fff;
                  padding: 6px 20px; border-radius: 20px; font-size:1em;
                  font-weight:bold; margin-top:12px; letter-spacing:1px; }}
        .container {{ padding: 30px 40px; }}
        .info-box {{ background:#fff; border-radius:8px; padding:20px 24px;
                     box-shadow:0 1px 4px rgba(0,0,0,0.08); margin-bottom:24px; }}
        .info-box h2 {{ font-size:1em; color:#7F8C8D; text-transform:uppercase;
                        letter-spacing:1px; margin-bottom:12px; }}
        .info-row {{ display:flex; gap:8px; margin-bottom:6px; font-size:0.95em; }}
        .info-row .label {{ color:#7F8C8D; min-width:160px; }}
        .info-row .value {{ color:#2C3E50; font-weight:500; word-break:break-all; }}
        .stats {{ display:flex; gap:16px; margin-bottom:24px; flex-wrap:wrap; }}
        .stat-card {{ flex:1; min-width:120px; background:#fff; border-radius:8px;
                      padding:18px 20px; text-align:center;
                      box-shadow:0 1px 4px rgba(0,0,0,0.08); }}
        .stat-card .number {{ font-size:2em; font-weight:700; }}
        .stat-card .desc {{ font-size:0.8em; color:#7F8C8D; margin-top:4px; text-transform:uppercase; letter-spacing:0.5px; }}
        .total .number {{ color:#2E86C1; }}
        .ok .number {{ color:#27AE60; }}
        .fail .number {{ color:#E74C3C; }}
        .unk .number {{ color:#F39C12; }}
        table {{ width:100%; border-collapse:collapse; background:#fff;
                 border-radius:8px; overflow:hidden;
                 box-shadow:0 1px 4px rgba(0,0,0,0.08); }}
        thead {{ background:#2E86C1; color:#fff; }}
        thead th {{ padding:12px 14px; font-size:0.85em; text-transform:uppercase;
                    letter-spacing:0.5px; text-align:center; }}
        thead th:first-child {{ text-align:left; }}
        tbody tr {{ border-bottom:1px solid #ECF0F1; }}
        tbody tr:last-child {{ border-bottom:none; }}
        tbody tr:hover {{ background:#F8FAFB; }}
        tbody td {{ padding:12px 14px; font-size:0.92em; vertical-align:middle; }}
        .footer {{ text-align:center; color:#BDC3C7; font-size:0.8em; padding:20px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>IDS Validation Report</h1>
        <p>buildingSMART IFC/IDS Compliance Check</p>
        <div class="badge">{overall_label}</div>
    </div>
    <div class="container">
        <div class="info-box">
            <h2>Files</h2>
            <div class="info-row"><span class="label">IFC File:</span><span class="value">{ifc_file}</span></div>
            <div class="info-row"><span class="label">Specification (IDS):</span><span class="value">{spec_file}</span></div>
        </div>
        <div class="stats">
            <div class="stat-card total"><div class="number">{spec_total}</div><div class="desc">Total Specs</div></div>
            <div class="stat-card ok"><div class="number">{spec_passed}</div><div class="desc">Passed</div></div>
            <div class="stat-card fail"><div class="number">{spec_failed}</div><div class="desc">Failed</div></div>
            <div class="stat-card unk"><div class="number">{spec_unknown}</div><div class="desc">Unknown</div></div>
        </div>
        <table>
            <thead>
                <tr>
                    <th>Specification</th>
                    <th>Status</th>
                    <th>Applicable</th>
                    <th>Passed</th>
                    <th>Failed</th>
                    <th>Req. Failures</th>
                    <th>Pass Rate</th>
                </tr>
            </thead>
            <tbody>
                {spec_rows}
            </tbody>
        </table>
    </div>
    <div class="footer">Generated by FELA Addon &mdash; buildingSMART Hackathon</div>
</body>
</html>"""


class IFC_OT_ShowReport(bpy.types.Operator):
    bl_idname = "ifc.show_report"
    bl_label = "Show Report"
    bl_description = "Show the report of the last execution"

    def execute(self, context):
        with open("resultado.json", "r", encoding="utf-8") as f:
            report_data = json.load(f)

        ifc_file = (
            context.scene.BIMProperties.ifc_file
            if hasattr(context.scene, "BIMProperties")
            else "No IFC loaded"
        )
        spec_file = context.scene.ifc_props.specfilepath

        html_report = build_html_report(report_data, ifc_file, spec_file)

        report_path = os.path.join(os.path.dirname(__file__), "report.html")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(html_report)

        webbrowser.open(report_path)

        return {"FINISHED"}