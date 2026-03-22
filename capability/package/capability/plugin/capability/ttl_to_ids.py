from pathlib import Path
import re
from typing import Any, Dict, List
from ifctester import ids
from ontobdc.run.core.capability import Capability, CapabilityMetadata
from ontobdc.run.core.port.contex import CliContextPort


class TtlToIdsCapability(Capability):
    METADATA = CapabilityMetadata(
        id="org.local.domain.ids.capability.ttl.to_ids",
        version="0.1.0",
        name="Ontology to IDS",
        description="Transforms one or more ontology files into a buildingSMART IDS document.",
        author="local",
        tags=["ontology", "ttl", "ids", "bim", "rules", "conversion"],
        supported_languages=["en", "pt_BR"],
        input_schema={
            "type": "object",
            "properties": {
                "onto_path": {
                    "type": list,
                    "uri": "org.local.domain.ontology.input.path",
                    "required": True,
                    "description": "List of ontology file paths.",
                },
                "ids_output_path": {
                    "type": "string",
                    "uri": "org.local.domain.ids.output.path",
                    "required": True,
                    "description": "Path where the generated IDS should be written.",
                },
            },
        },
        output_schema={
            "type": "object",
            "properties": {
                "org.local.domain.ids.output.path": {
                    "type": "string",
                    "description": "Path to the generated IDS file.",
                }
            },
        },
        raises=[],
    )

    def execute(self, context: CliContextPort) -> Dict[str, Any]:
        onto_path = context.get_parameter_value("onto_path")
        onto_paths: List[str]
        if isinstance(onto_path, str) and onto_path.strip():
            onto_paths = [onto_path]
        elif isinstance(onto_path, list) and onto_path:
            onto_paths = [p for p in onto_path if isinstance(p, str) and p.strip()]
        else:
            raise ValueError("Missing required input: onto_path")

        resolved_onto_paths: List[Path] = []
        for p in onto_paths:
            resolved = Path(p).expanduser().resolve()
            if not resolved.exists() or not resolved.is_file():
                raise FileNotFoundError(f"onto_path not found: {resolved}")
            resolved_onto_paths.append(resolved)

        ids_output_path = context.get_parameter_value("ids_output_path")
        if not isinstance(ids_output_path, str) or not ids_output_path.strip():
            raise ValueError("Missing required input: ids_output_path")
        resolved_ids_output_path = Path(ids_output_path).expanduser().resolve()

        self._create_ids(resolved_onto_paths, resolved_ids_output_path)
        return {"org.local.domain.ids.output.path": str(resolved_ids_output_path)}

    def _create_ids(self, onto_paths: List[Path], ids_output_path: Path) -> None:
        ids_doc = ids.Ids(title="Generated IDS")

        for onto_path in onto_paths:
            self._add_ontology_to_ids(ids_doc, onto_path)

        if not ids_doc.specifications:
            ids_doc.specifications.append(ids.Specification(name="No computable rules"))

        ids_output_path.parent.mkdir(parents=True, exist_ok=True)
        ids_doc.to_xml(str(ids_output_path))

    def _add_ontology_to_ids(self, ids_doc: ids.Ids, onto_path: Path) -> None:
        if onto_path.suffix.lower() != ".ttl":
            return

        computable_rules = self._read_ttl_feso_computable_rules(onto_path)
        for rule in computable_rules:
            name = rule.get("label") or self._compact_iri(rule.get("subject", "")) or "Unnamed"
            spec = ids.Specification(
                name=name,
                description=rule.get("requirement_text") or rule.get("condition_text") or None,
                instructions=rule.get("formula") or None,
            )
            ids_doc.specifications.append(spec)

    def _read_ttl_feso_computable_rules(self, onto_path: Path) -> List[Dict[str, str]]:
        try:
            from rdflib import Graph, Namespace
        except Exception as e:
            raise ImportError("rdflib is required to parse Turtle (.ttl) files") from e

        g = Graph()
        g.parse(str(onto_path), format="turtle")

        feso = Namespace("https://example.org/feso#")
        fr = Namespace("https://example.org/feso-rules#")
        rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")

        results: List[Dict[str, str]] = []

        subjects: set[Any] = set()
        subjects |= set(self._subjects_with_true(g, fr.isExpressibleInIDS))
        if not subjects:
            subjects |= set(self._subjects_with_true(g, feso.isComputableByIDS))

        for subject in subjects:
            label = next(g.objects(subject, rdfs.label), None)
            applies_to_class = next(g.objects(subject, feso.appliesToClass), None)
            requirement_text = next(g.objects(subject, feso.hasRequirementText), None)
            formula = next(g.objects(subject, feso.hasFormula), None)
            condition_text = next(g.objects(subject, feso.hasConditionText), None)

            results.append(
                {
                    "subject": str(subject),
                    "applies_to_class": str(applies_to_class) if applies_to_class is not None else "",
                    "label": str(label) if label is not None else "",
                    "requirement_text": str(requirement_text) if requirement_text is not None else "",
                    "formula": str(formula) if formula is not None else "",
                    "condition_text": str(condition_text) if condition_text is not None else "",
                }
            )

        return results

    def _subjects_with_true(self, g: Any, predicate: Any) -> List[Any]:
        subjects: List[Any] = []
        for s, o in g.subject_objects(predicate):
            try:
                py = o.toPython()
            except Exception:
                py = None
            is_true = py is True or str(o).strip().lower() in {"true", "1"}
            if is_true:
                subjects.append(s)
        return subjects

    def _compact_iri(self, iri: str) -> str:
        if not iri:
            return ""
        if "#" in iri:
            return iri.rsplit("#", 1)[-1].strip()
        return iri.rstrip("/").rsplit("/", 1)[-1].strip()
