from pathlib import Path
from typing import Any, Dict, Optional

from ontobdc.run.core.capability import Capability, CapabilityMetadata
from ontobdc.run.core.port.contex import CliContextPort


class ValidateIdsCapability(Capability):
    METADATA = CapabilityMetadata(
        id="org.local.domain.ids.capability.validate",
        version="0.1.0",
        name="Validate IDS",
        description="Validates an IFC model against an IDS specification using ifctester.",
        author="local",
        tags=["ids", "validation", "ifc", "ifctester"],
        supported_languages=["en", "pt_BR"],
        input_schema={
            "type": "object",
            "properties": {
                "ids_path": {
                    "type": "string",
                    "uri": "org.local.domain.ids.input.path",
                    "required": True,
                    "description": "Path to the IDS file.",
                },
                "ifc_path": {
                    "type": "string",
                    "uri": "org.infobim.domain.ifc.input.path",
                    "required": True,
                    "description": "Path to the IFC file.",
                },
            },
        },
        output_schema={
            "type": "object",
            "properties": {
                "org.local.domain.ids.validation.passed": {
                    "type": "boolean",
                    "description": "True if all specifications passed.",
                },
                "org.local.domain.ids.validation.summary": {
                    "type": "object",
                    "description": "Validation summary.",
                },
            },
        },
        raises=[],
    )

    def execute(self, context: CliContextPort) -> Dict[str, Any]:
        ids_path = self._normalize_existing_file(
            self._get_required_str(context, "ids_path"), "ids_path"
        )
        ifc_path = self._normalize_existing_file(
            self._get_required_str(context, "ifc_path"), "ifc_path"
        )

        try:
            ids_doc = self._load_ids(ids_path)
        except Exception as e:
            summary = {
                "passed": False,
                "ids_path": ids_path,
                "ifc_path": ifc_path,
                "error": str(e),
                "specifications_total": 0,
                "specifications_passed": 0,
                "specifications_failed": 0,
                "specifications": [],
            }
            return {
                "org.local.domain.ids.validation.passed": False,
                "org.local.domain.ids.validation.summary": summary,
            }

        summary = self._validate_ids(ids_doc, ifc_path, ids_path)

        return {
            "org.local.domain.ids.validation.passed": summary["passed"],
            "org.local.domain.ids.validation.summary": summary,
        }

    def get_default_cli_renderer(self) -> Optional[Any]:
        from ..adapter.renderer.validate_ids import ValidateIdsRenderer

        return ValidateIdsRenderer()

    def _get_required_str(self, context: CliContextPort, key: str) -> str:
        val = context.get_parameter_value(key)
        if not isinstance(val, str) or not val.strip():
            raise ValueError(f"Missing required input: {key}")
        return val

    def _normalize_existing_file(self, raw_path: str, label: str) -> str:
        resolved = Path(raw_path).expanduser().resolve()
        if not resolved.exists() or not resolved.is_file():
            raise FileNotFoundError(f"{label} not found: {resolved}")
        return str(resolved)

    def _load_ids(self, ids_path: str) -> Any:
        from ifctester import ids

        return ids.open(ids_path, validate=True)

    def _validate_ids(self, ids_doc: Any, ifc_path: str, ids_path: str) -> Dict[str, Any]:
        import ifcopenshell

        ifc_file = ifcopenshell.open(ifc_path)
        ids_doc.validate(ifc_file, filepath=ids_path)

        specs = []
        passed_count = 0
        failed_count = 0
        unknown_count = 0

        for spec in getattr(ids_doc, "specifications", []) or []:
            status = getattr(spec, "status", None)
            is_pass = status is True
            is_fail = status is False
            if is_pass:
                passed_count += 1
            elif is_fail:
                failed_count += 1
            else:
                unknown_count += 1

            failures = 0
            for facet in getattr(spec, "requirements", []) or []:
                failures += len(getattr(facet, "failures", []) or [])

            specs.append(
                {
                    "name": getattr(spec, "name", ""),
                    "status": "passed" if is_pass else "failed" if is_fail else "unknown",
                    "applicable_entities": len(getattr(spec, "applicable_entities", []) or []),
                    "passed_entities": len(getattr(spec, "passed_entities", []) or []),
                    "failed_entities": len(getattr(spec, "failed_entities", []) or []),
                    "requirement_failures": failures,
                }
            )

        summary = {
            "passed": failed_count == 0,
            "ids_path": ids_path,
            "ifc_path": ifc_path,
            "specifications_total": len(specs),
            "specifications_passed": passed_count,
            "specifications_failed": failed_count,
            "specifications_unknown": unknown_count,
            "specifications": specs,
        }

        return summary
