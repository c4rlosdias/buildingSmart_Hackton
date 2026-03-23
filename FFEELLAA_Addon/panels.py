import bpy
import os


class IFC_PT_PainelPrincipal(bpy.types.Panel):
    bl_label = "Determinist IA IFC"
    bl_idname = "IFC_PT_painel_principal"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "IFC"

    def draw(self, context):
        layout = self.layout
        props = context.scene.ifc_props

        if hasattr(context.scene, "BIMProperties"):
            bim_path = context.scene.BIMProperties.ifc_file
            if bim_path:
                layout.label(text="IFC carregado:", icon="CHECKMARK")
                layout.label(text=os.path.basename(bim_path))
            else:
                layout.label(text="No IFC loaded in Bonsai", icon="ERROR")
                layout.label(text="Select manually:")
                layout.prop(props, "filepath", text="")
        else:
            layout.label(text="Select manually:")
            layout.prop(props, "filepath", text="")

        layout.prop(props, "filepath", text="")
        layout.separator()
        layout.label(text="Select infobim capability:")
        layout.prop(props, "capabilities", text="")

        layout.separator()
        layout.operator("ifc.executar_externo", icon="PLAY")

        layout.separator()
        box = layout.box()
        box.label(text="Resultado da última execução:", icon="INFO")
        if len(props.elements) > 0:
            for elem in props.elements:
                row = box.row(align=True)
                row.label(text=f"Name:{elem.name} | GlobalId: {elem.global_id}")
                row.label(text=elem.info)
        
        else:
            box.label(text="(sem resultado ainda)", icon="BLANK1")
