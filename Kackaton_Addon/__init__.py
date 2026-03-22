# -*- coding: utf-8 -*-
"""
Hello World – Blender + IfcOpenShell  (com Painel UI)
=======================================================
Cole este script no Text Editor do Blender e pressione "Run Script" (Alt+P).
O painel aparecerá na aba "IFC" do N-panel (tecla N na viewport 3D).
Requer o addon BlenderBIM instalado (inclui ifcopenshell automaticamente).

Site: https://blenderbim.org/
"""

bl_info = {
    "name": "IFC Hello World",
    "author": "Hackathon buildingSMART",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > IFC",
    "description": "Abre e analisa arquivos IFC com IfcOpenShell",
    "category": "Import-Export",
}

import bpy
import sys
import os
import json
import datetime
import ifcopenshell
import ifcopenshell.util.element as util
import bonsai.tool as tool

addon_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(addon_dir, "Lib", "site-packages"))

from infobim.module.ifc.plugin.capability.list_buildings import ListIfcBuildingsCapability
from infobim.module.ifc.plugin.capability.list_elements import ListIfcElementsCapability
from infobim.module.ifc.plugin.capability.inspect_element import InspectIfcElementCapability
from infobim.module.ifc.plugin.capability.list_property_sets import ListIfcPropertySetsCapability
from ontobdc.run.core.capability import CapabilityExecutor  
from ontobdc.run.adapter.contex import CliContextAdapter


def run_infobim_capability(capability, **params) -> dict:
    """Executa qualquer capability do infobim com os parâmetros fornecidos.

    Exemplos:
        # Listar edifícios e pavimentos
        run_infobim_capability(ListIfcBuildingsCapability(), ifc_path="/path/to/file.ifc")

        # Listar elementos de uma classe IFC
        run_infobim_capability(ListIfcElementsCapability(), ifc_path="/path/to/file.ifc", ifc_class="IfcWall")

        # Inspecionar um elemento pelo GlobalId
        run_infobim_capability(InspectIfcElementCapability(), ifc_path="/path/to/file.ifc", global_id="2HXbP...")

        # Listar property sets de um elemento
        run_infobim_capability(ListIfcPropertySetsCapability(), ifc_path="/path/to/file.ifc", global_id="2HXbP...")
    """
    context = CliContextAdapter([])
    for key, value in params.items():
        context.add_parameter(key, {"value": value})

    resultado = CapabilityExecutor.execute(capability, context)
    print(f"[infobim] {capability.__class__.__name__}: {resultado}")

    # Audit log
    log_path = os.path.join(addon_dir, "audit.log")
    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "capability": capability.__class__.__name__,
        "params": {k: v for k, v in params.items() if k != "ifc_path"},
        "ifc_file": os.path.basename(params.get("ifc_path", "")),
    }
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return resultado

# ------------------------------------------------------------------
# Propriedades do addon (PropertyGroup)
# ------------------------------------------------------------------
class IFC_PG_Propriedades(bpy.types.PropertyGroup):
    filepath: bpy.props.StringProperty(
        name="Caminho IFC",
        description="Specification file",
        subtype="FILE_PATH",
    )
    result: bpy.props.StringProperty(
        name="Resultado",
        description="Resultado da análise",
        default="", 
    )
    capabilities: bpy.props.EnumProperty(
        name="Capability",
        description="Selecione a capability do infobim para executar",
        items=[("LIST_BUILDINGS", "Listar Edifícios", "Lista os edifícios e pavimentos do arquivo IFC"),
               ("LIST_ELEMENTS", "Listar Elementos", "Lista os elementos de uma classe IFC específica"),
               ("INSPECT_ELEMENT", "Inspecionar Elemento", "Inspeciona um elemento pelo GlobalId"),
               ("LIST_PROPERTY_SETS", "Listar Property Sets", "Lista os property sets de um elemento específico")],
        default="LIST_BUILDINGS",
    )

# ------------------------------------------------------------------
# Operador – abre o resultado em uma nova janela (Text Editor)
# ------------------------------------------------------------------
class IFC_OT_MostrarResultado(bpy.types.Operator):
    bl_idname = "ifc.mostrar_resultado"
    bl_label = "Resultado infobim"
    bl_description = "Exibe o resultado da última execução"

    def draw(self, context):
        layout = self.layout
        props = context.scene.ifc_props

        if not props.result:
            layout.label(text="Resultado inválido ou vazio.", icon="ERROR")
            return

        box = layout.box()
        col = box.column(align=True)
        for linha in props.result.splitlines():
            col.label(text=linha)

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=600)

    def execute(self, context):
        return {"FINISHED"}


# ------------------------------------------------------------------
# Operador – executa infobim run --ifc-path <filepath>
# ------------------------------------------------------------------
class IFC_OT_ExecutarExterno(bpy.types.Operator):
    bl_idname = "ifc.executar_externo"
    bl_label = "Run infobim"
    bl_description = "Executa: infobim run --ifc-path <arquivo IFC>"

    def execute(self, context):
        # Tenta pegar o arquivo IFC carregado no BlenderBIM
        filepath = ""
        props = context.scene.ifc_props
        if hasattr(context.scene, "BIMProperties"):
            filepath = bpy.path.abspath(context.scene.BIMProperties.ifc_file)

        # Fallback: campo manual do addon
        if not filepath or not os.path.isfile(filepath):
            filepath = bpy.path.abspath(props.filepath)

        if not filepath:
            self.report({"ERROR"}, "Nenhum arquivo IFC encontrado. Abra um arquivo IFC no BlenderBIM ou selecione manualmente.")
            return {"CANCELLED"}

        if not os.path.isfile(filepath):
            self.report({"ERROR"}, f"Arquivo IFC não encontrado: {filepath}")
            return {"CANCELLED"}


        try:
            obj = bpy.context.selected_objects[0] if bpy.context.selected_objects else None
            if props.capabilities == "LIST_BUILDINGS":
                resultado = run_infobim_capability(
                    ListIfcBuildingsCapability(),
                    ifc_path=filepath,
                )
            elif props.capabilities == "LIST_ELEMENTS":
                resultado = run_infobim_capability(
                    ListIfcElementsCapability(),
                    ifc_path=filepath,
                    ifc_class="IfcWall",  # Exemplo: listar apenas paredes
                )
            elif props.capabilities == "INSPECT_ELEMENT":
                
                if obj:
                    global_id = tool.Ifc.get_entity(obj).GlobalId
                    resultado = run_infobim_capability(
                        InspectIfcElementCapability(),
                        ifc_path=filepath,
                        global_id=global_id,  # Exemplo: GlobalId de um elemento específico
                    )
                    print(resultado)
                else:
                    self.report({"ERROR"}, "Selecione um objeto com GlobalId para inspecionar.")
                    return {"CANCELLED"}
            elif props.capabilities == "LIST_PROPERTY_SETS":
                if obj:
                    global_id = tool.Ifc.get_entity(obj).GlobalId
                    resultado = run_infobim_capability(
                        ListIfcPropertySetsCapability(),
                        ifc_path=filepath,
                        global_id=global_id,  # Exemplo: GlobalId de um elemento específico
                    )
                else:
                    self.report({"ERROR"}, "Selecione um objeto com GlobalId para listar seus property sets.")
                    return {"CANCELLED"}
            else:
                self.report({"ERROR"}, "Capability selecionada inválida.")
                return {"CANCELLED"}
            
            self.report({"INFO"}, f"Results: {resultado} ")
            props.result = json.dumps(resultado, indent=2, ensure_ascii=False)

        except Exception as e:
            self.report({"ERROR"}, f"Falha ao executar infobim: {e}")
            return {"CANCELLED"}

        return {"FINISHED"}


# ------------------------------------------------------------------
# Painel – aparece no N-panel da viewport 3D
# ------------------------------------------------------------------
class IFC_PT_PainelPrincipal(bpy.types.Panel):
    bl_label = "Determinist IA IFC"
    bl_idname = "IFC_PT_painel_principal"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "IFC"

    def draw(self, context):
        layout = self.layout
        props = context.scene.ifc_props

        # Mostra o arquivo IFC ativo no BlenderBIM
        if hasattr(context.scene, "BIMProperties"):
            bim_path = context.scene.BIMProperties.ifc_file
            if bim_path:
                layout.label(text="IFC carregado:", icon="CHECKMARK")
                layout.label(text=os.path.basename(bim_path))
            else:
                layout.label(text="Nenhum IFC no BlenderBIM", icon="ERROR")
                layout.label(text="Selecione manualmente:")
                layout.prop(props, "filepath", text="")
        else:
            layout.label(text="Selecione manualmente:")
            layout.prop(props, "filepath", text="")

        layout.separator()
        layout.label(text="Selecione a capability do infobim:")
        layout.prop(props, "capabilities", text="") 
        
        layout.separator()
        layout.operator("ifc.executar_externo", icon="PLAY")

        layout.separator()
        box = layout.box()
        box.label(text="Resultado da última execução:", icon="INFO")
        if props.result:
            box.operator("ifc.mostrar_resultado", icon="WINDOW", text="Abrir em nova janela")
        else:
            box.label(text="(sem resultado ainda)", icon="BLANK1")


# ------------------------------------------------------------------
# Registro
# ------------------------------------------------------------------
classes = (
    IFC_PG_Propriedades,
    IFC_OT_MostrarResultado,
    IFC_OT_ExecutarExterno,
    IFC_PT_PainelPrincipal,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.ifc_props = bpy.props.PointerProperty(type=IFC_PG_Propriedades)
    print("[Determinist IA IFC] Addon registrado com sucesso! Abra o N-panel (tecla N) na Viewport 3D e clique na aba 'IFC'.")


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    if hasattr(bpy.types.Scene, "ifc_props"):
        del bpy.types.Scene.ifc_props
    print("[IFC Hello World] Addon desregistrado.")



