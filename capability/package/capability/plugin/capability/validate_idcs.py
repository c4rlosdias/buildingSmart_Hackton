
from pathlib import Path
from typing import Any, Dict
from ontobdc.run.core.port.contex import CliContextPort
from ontobdc.run.core.capability import Capability, CapabilityMetadata


class ValidateIdcsCapability(Capability):
    """
    Capability de validação de IDCS (regras "não expressíveis em IDS") contra um IFC.

    Fluxo (alto nível):
    1) Lê o XML do IDCS e converte para um dicionário simples (tag/attrs/text/children).
    2) Extrai constraints do IDCS e monta um dicionário "objects" com:
       - ifcClass: classe IFC alvo
       - conditions: filtros (por Pset/Property == Value)
       - expression: AST (dicionário) da expressão booleana/matemática
       - annotation: metadados de texto (normativeText, etc.)
    3) Valida no IFC usando SymPy:
       - compila AST -> SymPy
       - resolve propertyRef -> valores do IFC (via psets)
       - avalia a expressão por entidade aplicável
    """
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
        # Entradas vindas do CLI (populadas pelas strategies):
        # - idcs_path: caminho do arquivo .idcs (XML)
        # - ifc_path: caminho do IFC (ou IFC normalizado)
        idcs_path: str = context.get_parameter_value("idcs_path")
        ifc_path: str = context.get_parameter_value("ifc_path")

        # Estruturas intermediárias:
        # - constraints: nós XML "constraint", indexados por nome
        # - objects: estrutura já "orientada a validação" que junta appliesTo + conditions + expression
        constraints: Dict[str, Any] = {}
        objects: Dict[str, Any] = {}
        idcs_doc: Dict[str, Any] = {}

        # Normaliza caminhos (absolutos), para report/erro ficar consistente.
        resolved_idcs_path = str(Path(idcs_path).expanduser().resolve())
        resolved_ifc_path = str(Path(ifc_path).expanduser().resolve())

        try:
            # Lê o XML e converte para um dict genérico.
            idcs_doc = self._load_idcs(resolved_idcs_path)
        except Exception as e:
            raise ValueError(f"Failed to load IDCS file: {resolved_idcs_path}. Error: {e}")

        # O arquivo IDCS tem um bloco <constraints> que contém <constraint name="...">.
        # Aqui localizamos e indexamos por constraintName.
        for first_level_child in idcs_doc["children"]:
            if first_level_child["tag"] == "constraints":
                for child in first_level_child["children"]:
                    if child["tag"] == "constraint":
                        constraints[child["attrs"]["name"]] = child

        if not constraints:
            raise ValueError(f"IDCS file {idcs_path} does not contain any constraints.")

        # Monta o dicionário de "objects" (um por constraint) com o que precisamos para validar:
        # - appliesTo: mapeia para o ifcClass
        # - condition: mapeia para filtro por Pset/Property/Value
        # - expression: AST para avaliação (SymPy)
        # - annotation: textos que podem ir para o relatório
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
                    # No IDCS atual usamos apenas <equals ...>, que vira filtro:
                    # Pset_Foo.Prop == Value
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
                    # Converte a árvore de expressão (XML) para um AST em dict/list.
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
                    # Extrai textos (normativeText, description, etc.) para facilitar o relatório no terminal.
                    objects[constraint_name]["annotation"] = self._annotation_to_dict(child)

        if not objects:
            raise ValueError(f"IDCS file {resolved_idcs_path} does not contain any objects.")

        # Executa a validação matemática:
        # - encontra entidades aplicáveis no IFC
        # - resolve propertyRef -> valores
        # - avalia a expressão com SymPy
        result: Dict[str, Any] = self._validate(objects, resolved_ifc_path)
        return {
            "org.local.domain.idcs.validation.passed": result.get("passed", False),
            "org.local.domain.idcs.validation.summary": {
                "idcs_path": resolved_idcs_path,
                "ifc_path": resolved_ifc_path,
                **result,
            },
        }

    def _annotation_to_dict(self, annotation_node: Dict[str, Any]) -> Dict[str, str]:
        # O "annotation_node" é um dict no formato {tag/attrs/text/children}.
        # Essa função só colhe os textos de interesse e ignora o resto.
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
        # Converte a expressão do XML (já em dict genérico) para um AST próprio,
        # mais fácil de compilar para SymPy.
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
        # Lê XML e produz um dict com:
        # - tag: nome sem namespace
        # - attrs: atributos sem namespace
        # - text: texto (trim)
        # - children: lista de filhos no mesmo formato
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
        # Faz a validação "de verdade" usando SymPy + IfcOpenShell:
        # - compila AST -> SymPy
        # - resolve variáveis (propertyRef) via Psets no IFC
        # - substitui valores e avalia booleans
        import sympy as sp
        import ifcopenshell
        import ifcopenshell.util.element

        ifc_file = ifcopenshell.open(ifc_path)

        result: Dict[str, Any] = {
            "passed": True,
            "constraints_total": len(objects),
            "constraints_passed": 0,
            "constraints_failed": 0,
            "constraints_unknown": 0,
            "objects_total": 0,
            "objects_passed": 0,
            "objects_failed": 0,
            "objects_unknown": 0,
            "constraints": [],
        }

        for constraint_name, constraint in objects.items():
            try:
                # 1) AST -> SymPy (Ge/And/multiply/etc.)
                sympy_expr = self._ast_to_sympy(constraint.get("expression"))
            except Exception as e:
                result["passed"] = False
                result["constraints_unknown"] += 1
                result["constraints"].append(
                    {
                        "constraintName": constraint_name,
                        "status": "unknown",
                        "reason": f"compile_error: {type(e).__name__}: {e}",
                    }
                )
                continue

            # 2) Descobre variáveis usadas (Symbols), assumindo naming "Pset.Property"
            symbols = sorted([s for s in getattr(sympy_expr, "free_symbols", set())], key=lambda x: str(x))
            symbol_refs: list[tuple[sp.Symbol, str, str]] = []
            for s in symbols:
                name = str(s)
                if "." not in name:
                    continue
                pset, prop = name.split(".", 1)
                symbol_refs.append((s, pset, prop))

            # 3) Seleciona o tipo IFC alvo para essa constraint.
            entity_type = constraint.get("ifcClass", "")
            if not entity_type:
                result["passed"] = False
                result["constraints_unknown"] += 1
                result["constraints"].append(
                    {"constraintName": constraint_name, "status": "unknown", "reason": "missing_ifcClass"}
                )
                continue

            # 4) Encontra entidades aplicáveis, considerando também constraints definidas no *Type* (IfcRelDefinesByType).
            applicable = list(self._iter_entities_matching(ifc_file, entity_type, constraint.get("conditions", {})))

            passed_entities = 0
            failed_entities = 0
            unknown_entities = 0
            examples: list[Dict[str, Any]] = []

            for el in applicable:
                # 5) Monta o dicionário de substituição SymPy (Symbol -> valor numérico).
                # Também guarda um "values_map" que serve como memória de cálculo para o renderer.
                subs: Dict[sp.Symbol, Any] = {}
                missing: list[str] = []
                values_map: Dict[str, Any] = {}
                for sym, pset, prop in symbol_refs:
                    # Aqui buscamos o valor em Psets. Observação: hoje usamos get_psets(el) diretamente.
                    # (Na filtragem de conditions usamos _collect_psets para mesclar occurrence+type.)
                    raw = self._get_pset_prop_value(el, pset, prop)
                    num = self._coerce_number(raw)
                    key = f"{pset}.{prop}"
                    if num is None:
                        missing.append(f"{pset}.{prop}")
                        values_map[key] = {"missing": True}
                    else:
                        subs[sym] = num
                        values_map[key] = {"value": float(num)}

                if missing:
                    # Se faltar qualquer variável, não dá para avaliar o booleano com segurança.
                    # Marcamos como unknown e registramos a memória de cálculo parcial.
                    unknown_entities += 1
                    if len(examples) < 3:
                        examples.append(
                            {
                                "entity": str(getattr(el, "GlobalId", "")) or str(el),
                                "status": "unknown",
                                "expr": str(sympy_expr),
                                "values": values_map,
                            }
                        )
                    continue

                # 6) Avalia a expressão booleana depois do "subs".
                evaluated = sympy_expr.subs(subs)
                try:
                    ok = bool(evaluated)
                except Exception:
                    ok = False

                if ok:
                    passed_entities += 1
                else:
                    # Falha: registra exemplos com GUID e valores usados para demonstrar a conta.
                    failed_entities += 1
                    if len(examples) < 3:
                        examples.append(
                            {
                                "entity": str(getattr(el, "GlobalId", "")) or str(el),
                                "status": "failed",
                                "expr": str(sympy_expr),
                                "values": values_map,
                            }
                        )

            # 7) Define status global da constraint.
            # Se não houver nenhum aplicável, não faz sentido dizer "passou"; marcamos como unknown.
            if len(applicable) == 0:
                status = "unknown"
            else:
                status = "passed" if failed_entities == 0 and unknown_entities == 0 else "failed" if failed_entities else "unknown"
            if status == "passed":
                result["constraints_passed"] += 1
            elif status == "failed":
                result["constraints_failed"] += 1
                result["passed"] = False
            else:
                result["constraints_unknown"] += 1
                result["passed"] = False
            # Acumula contagens globais de instâncias
            result["objects_total"] += len(applicable)
            result["objects_passed"] += passed_entities
            result["objects_failed"] += failed_entities
            result["objects_unknown"] += unknown_entities

            # 8) Anexa o resultado por constraint, com contagens e exemplos para o renderer.
            result["constraints"].append(
                {
                    "constraintName": constraint_name,
                    "status": status,
                    "ifcClass": entity_type,
                    "applicable_entities": len(applicable),
                    "passed_entities": passed_entities,
                    "failed_entities": failed_entities,
                    "unknown_entities": unknown_entities,
                    "sympy": str(sympy_expr),
                    "examples": examples,
                }
            )

        return result

    def _ast_to_sympy(self, ast: Any) -> Any:
        # Compila o AST (dict/list) para uma expressão SymPy.
        # Isso evita reinventar lógica/precedência e nos dá "free_symbols" e "subs".
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

    def _iter_entities_matching(self, ifc_file: Any, entity_type: str, conditions: Dict[str, Any]):
        base_type = entity_type.rstrip()  # guard

        # Case 1: o IDCS aponta diretamente para uma ocorrência (ex.: IfcFireSuppressionTerminal).
        if not base_type.endswith("Type"):
            for el in ifc_file.by_type(base_type):
                if self._matches_conditions(el, conditions):
                    yield el
            return

        # Case 2: o IDCS aponta para um Type (ex.: IfcFireSuppressionTerminalType).
        # Nesse caso, achamos as ocorrências via IfcRelDefinesByType.
        try:
            rels = ifc_file.by_type("IfcRelDefinesByType")
        except Exception:
            rels = []

        for rel in rels or []:
            try:
                t = rel.RelatingType
            except Exception:
                t = None
            if not t or not getattr(t, "is_a", lambda *_: False)(base_type):
                continue
            for el in rel.RelatedObjects or []:
                if self._matches_conditions(el, conditions, type_hint=t):
                    yield el

    def _matches_conditions(self, el: Any, conditions: Dict[str, Any]) -> bool:
        # Aplica o filtro "conditions" do IDCS:
        # conditions.propertySet[PsetName].properties[PropName] == expectedValue
        # try:
        #     import ifcopenshell.util.element

        #     psets = self._collect_psets(el) or {}
        # except Exception:
        #     return False

        pset_conditions = conditions.get("propertySet", {}) if isinstance(conditions, dict) else {}
        for pset_name, pset_rule in (pset_conditions or {}).items():
            expected_props = (pset_rule or {}).get("properties", {})

            if not isinstance(expected_props, dict):
                continue

            for prop_name, expected in expected_props.items():
                actual = self._get_pset_prop_value(el, pset_name, prop_name)
                if str(actual).strip() != str(expected).strip():
                    return False
        return True

    def _collect_psets(self, el: Any) -> Dict[str, Any]:
        """
        Merge occurrence and type Psets into a single dict: { PsetName: { PropName: value, ... }, ... }
        """
        try:
            import ifcopenshell.util.element
            merged: Dict[str, Any] = {}
            occ_psets = ifcopenshell.util.element.get_psets(el) or {}
            if isinstance(occ_psets, dict):
                merged.update(occ_psets)
            # Pull type property sets via IsDefinedBy -> RelDefinesByType -> RelatingType.HasPropertySets
            for rel in getattr(el, "IsDefinedBy", []) or []:
                try:
                    if not getattr(rel, "is_a", lambda *_: False)("IfcRelDefinesByType"):
                        continue
                    t = rel.RelatingType
                    for pset in getattr(t, "HasPropertySets", []) or []:
                        if getattr(pset, "is_a", lambda *_: False)("IfcPropertySet"):
                            props: Dict[str, Any] = {}
                            for ip in getattr(pset, "HasProperties", []) or []:
                                name = getattr(ip, "Name", None)
                                val = getattr(ip, "NominalValue", None)
                                if name:
                                    props[str(name)] = val
                            merged[str(getattr(pset, "Name", ""))] = props
                except Exception:
                    continue
            return merged
        except Exception:
            return {}

    def _get_pset_prop_value(self, el: Any, pset_name: str, prop_name: str) -> Any:
        # Acesso simples ao valor do property dentro do Pset.
        props = self._collect_psets(el).get(pset_name)
        if props is not None:
            print(f'Pset: {pset_name}')
            print(f'Prop: {prop_name}')
            print(props)

        if isinstance(props, dict):
            return props.get(prop_name)

        return None

    def _coerce_number(self, value: Any) -> float | None:
        # Converte valores IFC (que podem vir como wrapper, string, dict, etc.) para float.
        # Retorna None quando não é possível interpretar como número.
        if value is None:
            return None
        if isinstance(value, bool):
            return 1.0 if value else 0.0
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, dict):
            for k in ("NominalValue", "nominal_value", "value", "wrappedValue"):
                if k in value:
                    return self._coerce_number(value.get(k))
        try:
            s = str(value).strip()
            if not s:
                return None
            return float(s)
        except Exception:
            return None

    def get_default_cli_renderer(self) -> Any:
        # Renderer Rich para imprimir o relatório no terminal.
        from ..adapter.renderer.validate_idcs import ValidateIdcsRenderer
        return ValidateIdcsRenderer()
