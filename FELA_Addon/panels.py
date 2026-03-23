import bpy
import os


class IFC_PT_PainelPrincipal(bpy.types.Panel):
    bl_label = "Determinist IA IFC"
    bl_idname = "IFC_PT_painel_principal"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Deterministic IA IFC"

    def draw(self, context):
        layout = self.layout
        props = context.scene.ifc_props

        if hasattr(context.scene, "BIMProperties"):
            bim_path = context.scene.BIMProperties.ifc_file
            if bim_path:
                layout.label(text="IFC carregado:", icon="CHECKMARK")
                layout.label(text=os.path.basename(bim_path))
                layout.label(text="Select specification file:")
                layout.prop(props, "specfilepath", text="")
                layout.separator()
                layout.label(text="Select infobim capability:")
                layout.prop(props, "capabilities", text="")

                layout.separator()
                layout.operator("ifc.executar_externo", icon="PLAY")

                layout.separator()
                self.layout.template_list(
                    "IFC_UL_ElementList",
                    "",
                    props,
                    "elements",
                    props,
                    "element_index"
                )
                box = layout.box()
                box.label(text="Resultado da última execução:", icon="INFO")

            else:
                layout.label(text="No IFC loaded in Bonsai", icon="ERROR")


class IFC_UL_ElementList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if item:
            layout.label(text=f"Name: {item.name} | GlobalId: {item.global_id}")


