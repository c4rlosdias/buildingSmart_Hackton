import bpy
import os
import json

import bonsai.tool as tool
from capability.plugin.capability.validate_ids import ValidateIdsCapability
# from infobim.module.ifc.plugin.capability.list_elements import ListIfcElementsCapability
# from infobim.module.ifc.plugin.capability.inspect_element import InspectIfcElementCapability
# from infobim.module.ifc.plugin.capability.list_property_sets import ListIfcPropertySetsCapability
from ontobdc.run.core.capability import CapabilityExecutor
from ontobdc.run.adapter.contex import CliContextAdapter

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

