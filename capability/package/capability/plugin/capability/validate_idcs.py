
from pathlib import Path
from typing import Any, Dict, Optional
from ontobdc.run.core.port.contex import CliContextPort
from ontobdc.run.core.capability import Capability, CapabilityMetadata


class ValidateIdcsCapability(Capability):
    METADATA = CapabilityMetadata(
        id="org.local.domain.idcs.capability.validate",
        version="0.1.0",
        name="Validate IDCS",
        description="Validates an IFC model against an IDCS specification.",
        author="local",
        tags=["validation", "ifc", "idcs"],
        supported_languages=["en", "pt_BR"],
        input_schema={
            "type": "object",
            "properties": {
                "idcs_path": {
                    "type": "string",
                    "uri": "org.local.domain.idcs.input.path",
                    "required": True,
                    "description": "Path to the IDCS file.",
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
                "org.local.domain.idcs.validation.passed": {
                    "type": "boolean",
                    "description": "True if all specifications passed.",
                },
                "org.local.domain.idcs.validation.summary": {
                    "type": "object",
                    "description": "Validation summary.",
                },
            },
        },
        raises=[],
    )

    def execute(self, context: CliContextPort) -> Dict[str, Any]:
        idcs_path: str = context.get_parameter_value("idcs_path")
        ifc_path: str = context.get_parameter_value("ifc_path")
        constraints: Dict[str, Any] = {}
        objects: Dict[str, Any] = {}
        idcs_doc: Dict[str, Any] = {}

        try:
            idcs_doc = self._load_idcs(idcs_path)
        except Exception as e:
            raise ValueError(f"Failed to load IDCS file: {idcs_path}. Error: {e}")

        for first_level_child in idcs_doc["children"]:
            if first_level_child["tag"] == "constraints":
                for child in first_level_child["children"]:
                    if child["tag"] == "constraint":
                        constraints[child["attrs"]["name"]] = child

        if not constraints:
            raise ValueError(f"IDCS file {idcs_path} does not contain any constraints.")

        for constraint_name, constraint in constraints.items():
            # print(f"Constraint: {constraint_name}")
            for child in constraint["children"]:
                if child["tag"] == "appliesTo":
                    objects[constraint_name] = {
                        'constraintName': constraint_name,
                        'ifcClass': child['children'][0]['text'],
                        'conditions': {
                            'propertySet': {},
                        },
                    }

            for child in constraint["children"]:
                if child["tag"] == "condition":
                    for condition in child["children"]:
                        for attr_name, attr_value in condition["attrs"].items():
                            if attr_name == "propertySet":
                                if not attr_value in objects[constraint_name]['conditions']['propertySet'].keys():
                                    objects[constraint_name]['conditions']['propertySet'][attr_value] = {'properties': {}}

                                objects[constraint_name]['conditions']['propertySet'][attr_value]['properties'][condition["attrs"]["property"]] = condition["attrs"]["value"]

        if not objects:
            raise ValueError(f"IDCS file {idcs_path} does not contain any objects.")

        print(f"Objects: {objects}")


    def _load_idcs(self, idcs_path: str) -> Dict[str, Any]:
        from xml.etree import ElementTree as ET
        p = Path(idcs_path).expanduser().resolve()
        if not p.exists() or not p.is_file():
            raise FileNotFoundError(f"IDCS file not found: {p}")
        tree = ET.parse(str(p))
        root = tree.getroot()

        def strip_ns(tag: str) -> str:
            return tag.rsplit("}", 1)[-1] if "}" in tag else tag

        def elem_to_dict(el) -> Dict[str, Any]:
            d: Dict[str, Any] = {"tag": strip_ns(el.tag)}
            if el.attrib:
                d["attrs"] = {strip_ns(k): v for k, v in el.attrib.items()}
            txt = (el.text or "").strip()
            if txt:
                d["text"] = txt
            children = [elem_to_dict(c) for c in list(el)]
            if children:
                d["children"] = children
            return d

        return elem_to_dict(root)
