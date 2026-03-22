import re
import json
from pathlib import Path
from typing import Any, Dict, List
from zipfile import BadZipFile, ZipFile

from ontobdc.run.core.capability import Capability, CapabilityMetadata
from ontobdc.run.core.port.contex import CliContextPort


class ConvertIcddOntologyCapability(Capability):
    METADATA = CapabilityMetadata(
        id="org.local.domain.icdd.capability.ontology.convert",
        version="0.1.0",
        name="Convert ICDD Ontology Mapping",
        description="Converts data using ontology-based mappings contained in an ICDD container.",
        author="local",
        tags=["icdd", "ontology", "mapping", "conversion"],
        supported_languages=["en", "pt_BR"],
        input_schema={
            "type": "object",
            "properties": {
                "icdd_path": {
                    "type": "string",
                    "uri": "org.local.domain.icdd.input.path",
                    "required": True,
                    "description": "Path to the .icdd container (ZIP).",
                },
                "ifc_path": {
                    "type": "string",
                    "uri": "org.infobim.domain.ifc.input.path",
                    "required": True,
                    "description": "Path to the IFC file when the mapping targets IFC entities.",
                },
            },
        },
        output_schema={
            "type": "object",
            "properties": {
                "org.local.domain.icdd.output.normalized_ifc_path": {
                    "type": "string",
                    "description": "Normalized IFC path.",
                },
            },
        },
        raises=[],
    )

    def execute(self, context: CliContextPort) -> Dict[str, Any]:
        icdd_path_raw = self._get_required_str(context, "icdd_path")
        ifc_path_raw = self._get_required_str(context, "ifc_path")

        icdd_path = self._normalize_existing_file(icdd_path_raw, "icdd_path")
        ifc_path = self._normalize_existing_file(ifc_path_raw, "ifc_path")

        self._validate_icdd_container(icdd_path)

        normalized_ifc_path = self._ensure_normalized_ifc_file(ifc_path)

        self._convert_icdd_ontology(icdd_path, ifc_path, normalized_ifc_path)

        return {
            "org.local.domain.icdd.output.normalized_ifc_path": normalized_ifc_path
        }

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

    def _ensure_normalized_ifc_file(self, ifc_path: str) -> str:
        src = Path(ifc_path)
        dst = self._derive_normalized_ifc_path(src)

        dst.parent.mkdir(parents=True, exist_ok=True)
        return str(dst)

    def _derive_normalized_ifc_path(self, src: Path) -> Path:
        suffix = src.suffix if src.suffix else ".ifc"
        return src.with_name(f"{src.stem}.norm{suffix}")

    def _convert_icdd_ontology(self, icdd_path: str, ifc_path: str, normalized_ifc_path: str) -> None:
        import ifcopenshell

        if Path(ifc_path).resolve() == Path(normalized_ifc_path).resolve():
            raise ValueError("normalized_ifc_path must be different from ifc_path")

        mappings = self._read_icdd_mapping(icdd_path)
        ids_requirements = self._read_icdd_ids_requirements(icdd_path)
        dictionaries = self._read_icdd_dictionaries(icdd_path)
        rules = self._compile_rules(mappings, ids_requirements, dictionaries)

        model = ifcopenshell.open(ifc_path)
        self._apply_rules_to_ifc(model, rules)
        model.write(normalized_ifc_path)

    def _read_icdd_mapping(self, icdd_path: str) -> List[Dict[str, str]]:
        with ZipFile(icdd_path, "r") as zf:
            mapping_files = [
                n
                for n in zf.namelist()
                if n and not n.endswith("/") and n.endswith(".ttl") and "/mappings/" in f"/{n}"
            ]

            mappings: List[Dict[str, str]] = []
            for name in mapping_files:
                raw = zf.read(name)
                text = raw.decode("utf-8", errors="replace")
                mappings.extend(self._parse_ttl_equivalent_properties(text, mapping_file=name))

        return mappings

    def _read_icdd_ids_requirements(self, icdd_path: str) -> List[Dict[str, str]]:
        import xml.etree.ElementTree as ET

        with ZipFile(icdd_path, "r") as zf:
            ids_files = [
                n
                for n in zf.namelist()
                if n and not n.endswith("/") and n.endswith(".ids") and "/ids/" in f"/{n}"
            ]

            requirements: List[Dict[str, str]] = []
            for name in ids_files:
                raw = zf.read(name)
                root = ET.fromstring(raw)

                ns = {"ids": root.tag.split("}")[0].strip("{")} if "}" in root.tag else {}
                spec_path = ".//ids:specification" if ns else ".//specification"
                entity_path = ".//ids:entity" if ns else ".//entity"
                prop_path = ".//ids:property" if ns else ".//property"

                for spec in root.findall(spec_path, namespaces=ns):
                    entity_el = spec.find(entity_path, namespaces=ns)
                    entity_name = (entity_el.get("name") if entity_el is not None else "") or ""
                    if not entity_name:
                        continue

                    for prop_el in spec.findall(prop_path, namespaces=ns):
                        prop_name = (prop_el.get("name") or "").strip()
                        prop_uri = (prop_el.get("uri") or "").strip()
                        if prop_name and prop_uri:
                            requirements.append(
                                {
                                    "ids_file": name,
                                    "entity": entity_name,
                                    "property_name": prop_name,
                                    "property_uri": prop_uri,
                                }
                            )

            return requirements

    def _read_icdd_dictionaries(self, icdd_path: str) -> Dict[str, Dict[str, str]]:
        with ZipFile(icdd_path, "r") as zf:
            dict_files = [
                n
                for n in zf.namelist()
                if n
                and not n.endswith("/")
                and (n.endswith(".jsonld") or n.endswith(".json"))
                and "/dictionaries/" in f"/{n}"
            ]

            dictionaries: Dict[str, Dict[str, str]] = {}
            for name in dict_files:
                raw = zf.read(name)
                text = raw.decode("utf-8", errors="replace")
                try:
                    data = json.loads(text)
                except Exception:
                    continue

                if isinstance(data, list):
                    for item in data:
                        self._index_dictionary_item(dictionaries, item)
                else:
                    self._index_dictionary_item(dictionaries, data)

            return dictionaries

    def _index_dictionary_item(self, dictionaries: Dict[str, Dict[str, str]], data: Any) -> None:
        if not isinstance(data, dict):
            return
        uri = data.get("@id")
        if not isinstance(uri, str) or not uri.strip():
            return

        name = data.get("name")
        property_set = data.get("propertySet")
        dictionaries[uri] = {
            "name": name if isinstance(name, str) else "",
            "propertySet": property_set if isinstance(property_set, str) else "",
        }

    def _compile_rules(
        self,
        mappings: List[Dict[str, str]],
        ids_requirements: List[Dict[str, str]],
        dictionaries: Dict[str, Dict[str, str]],
    ) -> List[Dict[str, str]]:
        ids_by_uri: Dict[str, Dict[str, str]] = {}
        for r in ids_requirements:
            uri = r.get("property_uri", "")
            if uri and uri not in ids_by_uri:
                ids_by_uri[uri] = r

        rules: List[Dict[str, str]] = []
        for m in mappings:
            source_uri = m.get("source", "")
            target_iri = m.get("target", "")

            parsed = self._parse_ifcowl_attribute_iri(target_iri)
            if not parsed:
                continue

            ids_req = ids_by_uri.get(source_uri, {})
            entity = ids_req.get("entity", "")

            dict_entry = dictionaries.get(source_uri, {})
            prop_name = dict_entry.get("name") or ids_req.get("property_name") or ""
            prop_set = dict_entry.get("propertySet") or ""

            rules.append(
                {
                    "source_uri": source_uri,
                    "source_property_set": prop_set,
                    "source_property_name": prop_name,
                    "target": target_iri,
                    "target_entity": parsed[0],
                    "target_attribute": parsed[1],
                    "entity": entity,
                }
            )

        return rules

    def _parse_ifcowl_attribute_iri(self, iri: str) -> tuple[str, str] | None:
        fragment = iri.split("#", 1)[-1] if "#" in iri else ""
        if not fragment or "_" not in fragment:
            return None
        entity, attr = fragment.split("_", 1)
        if not entity or not attr:
            return None
        if not entity.startswith("Ifc"):
            return None
        return entity, attr

    def _apply_rules_to_ifc(self, model: Any, rules: List[Dict[str, str]]) -> None:
        for rule in rules:
            entity = rule.get("entity") or rule.get("target_entity")
            if not entity:
                continue

            for el in model.by_type(entity):
                attr = rule.get("target_attribute", "")
                if not attr:
                    continue

                current = getattr(el, attr, None)
                current_str = str(current).strip() if current is not None else ""

                value = self._extract_value_from_ifc_element(el, rule)
                if not value:
                    continue
                if value == current_str:
                    continue

                try:
                    setattr(el, attr, value)
                except Exception:
                    pass

    def _extract_value_from_ifc_element(self, el: Any, rule: Dict[str, str]) -> str:
        try:
            import ifcopenshell.util.element

            psets = ifcopenshell.util.element.get_psets(el) or {}
        except Exception:
            return ""

        prop_name = (rule.get("source_property_name") or "").strip()
        prop_set = (rule.get("source_property_set") or "").strip()

        if prop_set and prop_name:
            v = self._get_pset_property(psets, prop_set, prop_name)
            if v:
                return v

        if prop_name:
            for _, props in psets.items():
                if not isinstance(props, dict):
                    continue
                v = self._coerce_to_str(props.get(prop_name))
                if v:
                    return v

        return ""

    def _get_pset_property(self, psets: Any, pset_name: str, prop_name: str) -> str:
        if not isinstance(psets, dict):
            return ""
        props = psets.get(pset_name)
        if not isinstance(props, dict):
            return ""
        return self._coerce_to_str(props.get(prop_name))

    def _coerce_to_str(self, value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, str):
            return value.strip()
        if isinstance(value, dict):
            for key in ("NominalValue", "nominal_value", "value", "wrappedValue"):
                if key in value:
                    return self._coerce_to_str(value.get(key))
        try:
            return str(value).strip()
        except Exception:
            return ""

    def _parse_ttl_equivalent_properties(self, ttl_text: str, mapping_file: str) -> List[Dict[str, str]]:
        prefixes = self._parse_ttl_prefixes(ttl_text)

        results: List[Dict[str, str]] = []
        pattern = re.compile(r"(?P<s>\S+)\s+owl:equivalentProperty\s+(?P<o>\S+)\s*\.", re.MULTILINE)
        for match in pattern.finditer(ttl_text):
            s_raw = match.group("s")
            o_raw = match.group("o")

            results.append(
                {
                    "mapping_file": mapping_file,
                    "predicate": self._resolve_ttl_term("owl:equivalentProperty", prefixes),
                    "source": self._resolve_ttl_term(s_raw, prefixes),
                    "target": self._resolve_ttl_term(o_raw, prefixes),
                }
            )

        return results

    def _parse_ttl_prefixes(self, ttl_text: str) -> Dict[str, str]:
        prefixes: Dict[str, str] = {
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "owl": "http://www.w3.org/2002/07/owl#",
            "xsd": "http://www.w3.org/2001/XMLSchema#",
        }

        for line in ttl_text.splitlines():
            stripped = line.strip()
            if not stripped.startswith("@prefix"):
                continue
            m = re.match(r"@prefix\s+([A-Za-z_][A-Za-z0-9_-]*)\:\s*<([^>]+)>\s*\.", stripped)
            if not m:
                continue
            prefixes[m.group(1)] = m.group(2)

        return prefixes

    def _resolve_ttl_term(self, term: str, prefixes: Dict[str, str]) -> str:
        cleaned = term.strip().rstrip(";").rstrip(".").strip()
        if cleaned.startswith("<") and cleaned.endswith(">"):
            return cleaned[1:-1]
        if cleaned.startswith("_:"):
            return cleaned
        if ":" in cleaned and not cleaned.startswith("http://") and not cleaned.startswith("https://"):
            prefix, local = cleaned.split(":", 1)
            base = prefixes.get(prefix)
            if base:
                return f"{base}{local}"
        return cleaned

    def _validate_icdd_container(self, icdd_path: str) -> None:
        try:
            with ZipFile(icdd_path, "r") as zf:
                names = [n for n in zf.namelist() if n and not n.endswith("/")]
        except BadZipFile as e:
            raise ValueError(f"icdd_path is not a valid ZIP: {icdd_path}") from e

        required_folders = ("dictionaries", "mappings", "ids")
        missing = [f for f in required_folders if not self._has_folder(names, f)]
        if missing:
            raise ValueError(f"ICDD container missing folders: {', '.join(missing)}")

    def _has_folder(self, names: list[str], folder: str) -> bool:
        direct_prefix = f"{folder}/"
        nested_prefix = f"/{folder}/"

        for n in names:
            if n.startswith(direct_prefix):
                return True
            if nested_prefix in f"/{n}":
                if f"/{folder}/" in f"/{n}":
                    parts = n.split("/", 1)
                    if len(parts) == 2 and parts[1].startswith(direct_prefix):
                        return True

        return False
