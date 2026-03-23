import bpy
import os
import json

import bonsai.tool as tool

from infobim.module.ifc.plugin.capability.list_buildings import ListIfcBuildingsCapability
from infobim.module.ifc.plugin.capability.list_elements import ListIfcElementsCapability
from infobim.module.ifc.plugin.capability.inspect_element import InspectIfcElementCapability
from infobim.module.ifc.plugin.capability.list_property_sets import ListIfcPropertySetsCapability

from .utils import run_infobim_capability, add_elements



class IFC_OT_ExecutarExterno(bpy.types.Operator):
    bl_idname = "ifc.executar_externo"
    bl_label = "Run infobim"
    bl_description = "Executa: infobim run --ifc-path <arquivo IFC>"

    def execute(self, context):
        filepath = ""
        props = context.scene.ifc_props
        if hasattr(context.scene, "BIMProperties"):
            filepath = bpy.path.abspath(context.scene.BIMProperties.ifc_file)

        if not filepath or not os.path.isfile(filepath):
            filepath = bpy.path.abspath(props.filepath)

        if not filepath:
            self.report({"ERROR"}, "No IFC file found. Open an IFC file in BlenderBIM or select one manually.")
            return {"CANCELLED"}

        if not os.path.isfile(filepath):
            self.report({"ERROR"}, f"IFC file not found: {filepath}")
            return {"CANCELLED"}

        try:
            cap = props.capabilities

            # Resolve global_id once for capabilities that require a selected object
            global_id = None
            if cap in ("INSPECT_ELEMENT", "LIST_PROPERTY_SETS"):
                obj = bpy.context.selected_objects[0] if bpy.context.selected_objects else None
                if not obj:
                    self.report({"ERROR"}, "Select an object with GlobalId.")
                    return {"CANCELLED"}
                global_id = tool.Ifc.get_entity(obj).GlobalId

            if cap == "LIST_BUILDINGS":
                resultado = run_infobim_capability(
                    ListIfcBuildingsCapability(),
                    ifc_path=filepath,
                )

            elif cap == "LIST_ELEMENTS":
                resultado = run_infobim_capability(
                    ListIfcElementsCapability(),
                    ifc_path=filepath,
                    ifc_class="IfcWall",
                )['org.infobim.domain.ifc.element.list.content']

            elif cap == "INSPECT_ELEMENT":
                resultado = run_infobim_capability(
                    InspectIfcElementCapability(),
                    ifc_path=filepath,
                    global_id=global_id,
                )

            elif cap == "LIST_PROPERTY_SETS":
                resultado = run_infobim_capability(
                    ListIfcPropertySetsCapability(),
                    ifc_path=filepath,
                    global_id=global_id,
                )

            else:
                self.report({"ERROR"}, "Invalid capability selected.")
                return {"CANCELLED"}

            with open("resultado.json", "w", encoding="utf-8") as f:
                json.dump(resultado, f, ensure_ascii=False, indent=4)

            add_elements(context, resultado)

        except Exception as e:
            self.report({"ERROR"}, f"Failed to execute infobim: {e}")
            return {"CANCELLED"}

        return {"FINISHED"}
