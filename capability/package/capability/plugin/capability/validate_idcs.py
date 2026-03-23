
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
            for child in constraint["children"]:
                if child["tag"] == "appliesTo":
                    objects[constraint_name] = {
                        "constraintName": constraint_name,
                        "ifcClass": child["children"][0]["text"],
                        "conditions": {"propertySet": {}},
                        "annotation": {},
                        "expression": None,
                    }

            for child in constraint["children"]:
                if child["tag"] == "condition":
                    if constraint_name not in objects:
                        objects[constraint_name] = {
                            "constraintName": constraint_name,
                            "ifcClass": "",
                            "conditions": {"propertySet": {}},
                            "annotation": {},
                            "expression": None,
                        }
                    for condition in child["children"]:
                        if condition.get("tag") != "equals":
                            continue
                        attrs = condition.get("attrs", {})
                        pset = attrs.get("propertySet", "")
                        prop = attrs.get("property", "")
                        val = attrs.get("value", "")
                        if not pset or not prop:
                            continue
                        if pset not in objects[constraint_name]["conditions"]["propertySet"]:
                            objects[constraint_name]["conditions"]["propertySet"][pset] = {"properties": {}}
                        objects[constraint_name]["conditions"]["propertySet"][pset]["properties"][prop] = val

                if child["tag"] == "expression":
                    if constraint_name not in objects:
                        objects[constraint_name] = {
                            "constraintName": constraint_name,
                            "ifcClass": "",
                            "conditions": {"propertySet": {}},
                            "annotation": {},
                            "expression": None,
                        }
                    objects[constraint_name]["expression"] = self._expression_to_ast(child)

                if child["tag"] == "annotation":
                    if constraint_name not in objects:
                        objects[constraint_name] = {
                            "constraintName": constraint_name,
                            "ifcClass": "",
                            "conditions": {"propertySet": {}},
                            "annotation": {},
                            "expression": None,
                        }
                    objects[constraint_name]["annotation"] = self._annotation_to_dict(child)

        if not objects:
            raise ValueError(f"IDCS file {idcs_path} does not contain any objects.")

        result: Dict[str, Any] = self._validate(objects, ifc_path)

        return result

        return {
            "org.local.domain.idcs.validation.passed": result.get("passed", False),
            "org.local.domain.idcs.validation.summary": {
                "idcs_path": idcs_path,
                "ifc_path": ifc_path,
                "constraints_total": len(objects),
                "objects": objects,
            },
        }

    def _annotation_to_dict(self, annotation_node: Dict[str, Any]) -> Dict[str, str]:
        def get_text(tag: str) -> str:
            for c in annotation_node.get("children", []) or []:
                if c.get("tag") == tag:
                    return c.get("text", "")
            return ""

        return {
            "normativeText": get_text("normativeText"),
            "description": get_text("description"),
            "source": get_text("source"),
            "clause": get_text("clause"),
            "applicabilityNote": get_text("applicabilityNote"),
        }

    def _expression_to_ast(self, node: Dict[str, Any]) -> Any:
        if node.get("tag") == "expression":
            children = node.get("children", []) or []
            if len(children) == 1:
                return self._expression_to_ast(children[0])
            return [self._expression_to_ast(c) for c in children]

        tag = node.get("tag", "")
        children = node.get("children", []) or []
        attrs = node.get("attrs", {}) or {}
        text = node.get("text", "")

        if tag in {"and", "or"}:
            return {tag: [self._expression_to_ast(c) for c in children]}

        if tag in {"greaterOrEqual", "greaterThan", "lessOrEqual", "lessThan", "equals", "notEqual"}:
            if len(children) >= 2:
                return {tag: [self._expression_to_ast(children[0]), self._expression_to_ast(children[1])]}
            return {tag: [self._expression_to_ast(c) for c in children]}

        if tag in {"multiply", "add", "subtract", "divide"}:
            return {tag: [self._expression_to_ast(c) for c in children]}

        if tag == "propertyRef":
            return {"propertyRef": {"propertySet": attrs.get("propertySet", ""), "property": attrs.get("property", "")}}

        if tag == "literal":
            lit: Dict[str, Any] = {"value": text}
            if "unit" in attrs:
                lit["unit"] = attrs.get("unit")
            return {"literal": lit}

        if children:
            return {tag: [self._expression_to_ast(c) for c in children]}
        if attrs:
            return {tag: attrs}
        return {tag: text}

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

    def _validate(self, objects: Dict[str, Any], ifc_path: str) -> Dict[str, Any]:
        import ifcopenshell

        ifc_file = ifcopenshell.open(ifc_path)

        for constraint_name, constraint in objects.items():
            if "expression" not in constraint.keys():
                continue

            expression = constraint["expression"]
            # print(constraint_name, expression.keys(), expression.values())

        result: Dict[str, Any] = {
            "passed": True,
            "constraints_total": len(objects),
            "constraints_passed": 0,
            "constraints_failed": 0,
            "constraints_unknown": 0,
            "constraints": [],
        }

        for constraint_name, constraint in objects.items():
            expression_ast = constraint.get("expression")
            if not expression_ast:
                result["constraints_unknown"] += 1
                result["constraints"].append(
                    {
                        "constraintName": constraint_name,
                        "status": "unknown",
                        "reason": "missing_expression",
                    }
                )
                continue

            try:
                sympy_expr = self._ast_to_sympy(expression_ast)
                sympy_str = str(sympy_expr)
                status = "compiled"
                reason = ""
            except Exception as e:
                sympy_str = ""
                status = "unknown"
                reason = f"compile_error: {type(e).__name__}: {e}"
                result["passed"] = False
                result["constraints_unknown"] += 1

            result["constraints"].append(
                {
                    "constraintName": constraint_name,
                    "status": status,
                    "sympy": sympy_str,
                    "reason": reason,
                }
            )

        return result

    def _ast_to_sympy(self, ast: Any) -> Any:
        import sympy as sp

        if isinstance(ast, list):
            return [self._ast_to_sympy(x) for x in ast]

        if not isinstance(ast, dict) or len(ast) != 1:
            raise ValueError(f"Invalid AST node: {ast}")

        op, payload = next(iter(ast.items()))

        if op == "and":
            return sp.And(*[self._ast_to_sympy(x) for x in payload])
        if op == "or":
            return sp.Or(*[self._ast_to_sympy(x) for x in payload])

        if op == "greaterOrEqual":
            left = self._ast_to_sympy(payload[0])
            right = self._ast_to_sympy(payload[1])
            return sp.Ge(left, right)
        if op == "greaterThan":
            left = self._ast_to_sympy(payload[0])
            right = self._ast_to_sympy(payload[1])
            return sp.Gt(left, right)
        if op == "lessOrEqual":
            left = self._ast_to_sympy(payload[0])
            right = self._ast_to_sympy(payload[1])
            return sp.Le(left, right)
        if op == "lessThan":
            left = self._ast_to_sympy(payload[0])
            right = self._ast_to_sympy(payload[1])
            return sp.Lt(left, right)
        if op == "equals":
            left = self._ast_to_sympy(payload[0])
            right = self._ast_to_sympy(payload[1])
            return sp.Eq(left, right)
        if op == "notEqual":
            left = self._ast_to_sympy(payload[0])
            right = self._ast_to_sympy(payload[1])
            return sp.Ne(left, right)

        if op == "multiply":
            left = self._ast_to_sympy(payload[0])
            right = self._ast_to_sympy(payload[1])
            return left * right
        if op == "add":
            left = self._ast_to_sympy(payload[0])
            right = self._ast_to_sympy(payload[1])
            return left + right
        if op == "subtract":
            left = self._ast_to_sympy(payload[0])
            right = self._ast_to_sympy(payload[1])
            return left - right
        if op == "divide":
            left = self._ast_to_sympy(payload[0])
            right = self._ast_to_sympy(payload[1])
            return left / right

        if op == "literal":
            value = payload.get("value", "")
            if isinstance(value, str):
                v = value.strip()
                try:
                    if "." in v:
                        return sp.Float(v)
                    return sp.Integer(v)
                except Exception:
                    return sp.Symbol(v)
            return sp.Symbol(str(value))

        if op == "propertyRef":
            pset = payload.get("propertySet", "")
            prop = payload.get("property", "")
            return sp.Symbol(f"{pset}.{prop}")

        raise ValueError(f"Unsupported operator: {op}")
