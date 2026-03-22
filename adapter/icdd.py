from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from zipfile import ZIP_DEFLATED, ZipFile


@dataclass(frozen=True)
class IcddFileSpec:
    source: Path
    archive_path: str


def build_icdd_container(
    *,
    source_root: str | Path,
    output_file: str | Path,
    container_root_dir: str | None = None,
    overwrite: bool = True,
) -> Path:
    src_root = Path(source_root).resolve()
    out_file = Path(output_file).resolve()

    if not src_root.exists() or not src_root.is_dir():
        raise FileNotFoundError(f"source_root not found or not a directory: {src_root}")

    out_file.parent.mkdir(parents=True, exist_ok=True)
    if out_file.exists():
        if overwrite:
            out_file.unlink()
        else:
            raise FileExistsError(f"output_file already exists: {out_file}")

    icdd_root = container_root_dir or out_file.name
    icdd_root = icdd_root.strip("/")
    if not icdd_root:
        raise ValueError("container_root_dir cannot be empty")

    file_specs = _fnde_file_specs(src_root=src_root, icdd_root=icdd_root)
    _validate_file_specs(file_specs)

    with ZipFile(out_file, mode="w", compression=ZIP_DEFLATED) as zf:
        for spec in file_specs:
            zf.write(spec.source, spec.archive_path)

    return out_file


def _fnde_file_specs(*, src_root: Path, icdd_root: str) -> list[IcddFileSpec]:
    dictionaries_dir = src_root / "code" / "dictionaries"
    mappings_dir = src_root / "code" / "mappings"
    ids_dir = src_root / "code" / "ids"

    files = [
        IcddFileSpec(
            source=dictionaries_dir / "FNDE-Ambiente.jsonld",
            archive_path=f"{icdd_root}/dictionaries/FNDE-Ambiente.jsonld",
        ),
        IcddFileSpec(
            source=mappings_dir / "mapping-FNDE-to-IFC.ttl",
            archive_path=f"{icdd_root}/mappings/mapping-FNDE-to-IFC.ttl",
        ),
        IcddFileSpec(
            source=ids_dir / "FNDE-Space.ids",
            archive_path=f"{icdd_root}/ids/FNDE-Space.ids",
        ),
    ]

    return files


def _validate_file_specs(file_specs: Iterable[IcddFileSpec]) -> None:
    missing: list[Path] = []
    for spec in file_specs:
        if not spec.source.exists() or not spec.source.is_file():
            missing.append(spec.source)

    if missing:
        missing_list = "\n".join(str(p) for p in missing)
        raise FileNotFoundError(f"ICDD input files not found:\n{missing_list}")

