import os
import json
import logging
import datetime

from infobim.module.ifc.plugin.capability.list_buildings import ListIfcBuildingsCapability
# from infobim.module.ifc.plugin.capability.list_elements import ListIfcElementsCapability
# from infobim.module.ifc.plugin.capability.inspect_element import InspectIfcElementCapability
# from infobim.module.ifc.plugin.capability.list_property_sets import ListIfcPropertySetsCapability
from ontobdc.run.core.capability import CapabilityExecutor
from ontobdc.run.adapter.contex import CliContextAdapter

addon_dir = os.path.dirname(os.path.realpath(__file__))

logger = logging.getLogger("infobim_addon")
logger.setLevel(logging.DEBUG)

# Ensure we only add handlers once
if not logger.handlers:
    # File handler — audit entries (INFO and above), one JSON line per record
    _file_handler = logging.FileHandler(
        os.path.join(addon_dir, "audit.log"), encoding="utf-8"
    )
    _file_handler.setLevel(logging.INFO)
    _file_handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(_file_handler)

    # Console handler — debug output visible in Blender's system console
    _console_handler = logging.StreamHandler()
    _console_handler.setLevel(logging.DEBUG)
    _console_handler.setFormatter(logging.Formatter("[infobim] %(levelname)s: %(message)s"))
    logger.addHandler(_console_handler)

# ------------------------------------------------------------------
# Add utility functions for running capabilities and adding elements to the panel here
# ------------------------------------------------------------------
def add_elements(context, resultado):
    """Adds elements to the panel property."""
    props = context.scene.ifc_props
    props.elements.clear()  # Clear previous elements
    if isinstance(resultado, dict):
        for key, values in resultado.items():
            for value in values:
                elem = props.elements.add()
                elem.name = value.get("Name", "")
                elem.global_id = value.get("GlobalId", "")

    elif isinstance(resultado, list):
        for value in resultado:
            elem = props.elements.add()
            elem.name = value.get("Name", "")
            elem.global_id = value.get("GlobalId", "")
    else:
        print(f"[add_elements] Unexpected result: {resultado}")
        
# ------------------------------------------------------------------
# Function to run any infobim capability with given parameters and log the execution
# ------------------------------------------------------------------
def run_infobim_capability(capability, **params) -> dict:
    """run any capability of infobim with the provided parameters."""
    context = CliContextAdapter([])
    for key, value in params.items():
        context.add_parameter(key, {"value": value})

    resultado = CapabilityExecutor.execute(capability, context)
    logger.debug(f"{capability.__class__.__name__}: {resultado}")

    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "capability": capability.__class__.__name__,
        "params": {k: v for k, v in params.items() if k != "ifc_path"},
        "ifc_file": os.path.basename(params.get("ifc_path", "")),
    }
    logger.info(json.dumps(entry, ensure_ascii=False))

    return resultado
