"""
Hello World – Blender + IfcOpenShell  (com Painel UI)
=======================================================
Cole este script no Text Editor do Blender e pressione "Run Script" (Alt+P).
O painel aparecerá na aba "IFC" do N-panel (tecla N na viewport 3D).
Requer o addon BlenderBIM instalado (inclui ifcopenshell automaticamente).

Site: https://blenderbim.org/
"""

import bpy
import ifcopenshell
import ifcopenshell.util.element as util

# ------------------------------------------------------------------
# Propriedades de cena
# ------------------------------------------------------------------
IFC_PATH_DEFAULT = r"C:\Users\c4rlo\OneDrive\Documentos\TRABALHO\CERTI\SUMMITS\Hackaton\buildingSmart_Hackton\IFC_files\TIPO1-ARQ-MOD_R03.ifc"


# ------------------------------------------------------------------
# Operador – executa a análise IFC
# ------------------------------------------------------------------
class IFC_OT_AnalisarModelo(bpy.types.Operator):
    bl_idname = "ifc.analisar_modelo"
    bl_label = "Analisar Modelo IFC"
    bl_description = "Abre o arquivo IFC e exibe informações no console"

    def execute(self, context):
        ifc_path = context.scene.ifc_path

        print("\n" + "=" * 60)
        print("  HELLO WORLD – Blender + IfcOpenShell")
        print("=" * 60)

        try:
            model = ifcopenshell.open(ifc_path)
        except Exception as e:
            self.report({"ERROR"}, f"Falha ao abrir o IFC: {e}")
            return {"CANCELLED"}

        print(f"\n Modelo carregado: {ifc_path}")

        # Informações básicas do projeto
        projetos = model.by_type("IfcProject")
        if projetos:
            projeto = projetos[0]
            print(f"\n Projeto : {projeto.Name}")
            print(f"   GlobalId : {projeto.GlobalId}")
            print(f"   Schema   : {model.schema}")

        # Edifícios e pavimentos
        print("\n Edificios encontrados:")
        for edificio in model.by_type("IfcBuilding"):
            print(f"   • {edificio.Name or '(sem nome)'}")

        print("\n Pavimentos encontrados:")
        for andar in model.by_type("IfcBuildingStorey"):
            print(f"   • {andar.Name or '(sem nome)'}")

        # Contagem de elementos por tipo
        tipos_interesse = [
            "IfcWall", "IfcSlab", "IfcDoor", "IfcWindow",
            "IfcColumn", "IfcBeam", "IfcFireSuppressionTerminal",
            "IfcBuildingElementProxy",
        ]
        print("\n Contagem de elementos:")
        for tipo in tipos_interesse:
            elementos = model.by_type(tipo)
            if elementos:
                print(f"   {tipo:<35} -> {len(elementos):>4} elemento(s)")

        # Extintores
        extintores = model.by_type("IfcFireSuppressionTerminal")
        proxies_extintor = [
            e for e in model.by_type("IfcBuildingElementProxy")
            if e.Name and "extintor" in e.Name.lower()
        ]
        total_extintores = extintores + proxies_extintor

        print(f"\n Extintores encontrados: {len(total_extintores)}")
        for ext in total_extintores[:5]:
            psets = util.get_psets(ext)
            pset_nbr = psets.get("Pset_FireExtinguisher_NBR15808", {})
            capacidade = pset_nbr.get("ExtinguishingCapacity", "N/D")
            container = util.get_container(ext)
            local = container.Name if container else "N/D"
            print(f"   • {ext.Name or ext.GlobalId} | Cap: {capacidade} | Local: {local}")

        print("\n" + "=" * 60)
        print("  Script concluído com sucesso!")
        print("=" * 60 + "\n")

        self.report({"INFO"}, f"IFC analisado! {len(total_extintores)} extintor(es) encontrado(s). Veja o console.")
        return {"FINISHED"}


# ------------------------------------------------------------------
# Painel – aparece no N-panel da viewport 3D
# ------------------------------------------------------------------
class IFC_PT_PainelPrincipal(bpy.types.Panel):
    bl_label = "IFC – Hello World"
    bl_idname = "IFC_PT_painel_principal"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "IFC"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.label(text="Arquivo IFC:")
        layout.prop(scene, "ifc_path", text="")

        layout.separator()
        layout.operator("ifc.analisar_modelo", icon="VIEWZOOM")

        layout.separator()
        layout.label(text="Resultado no console (Alt+F4 →")
        layout.label(text="Window > Toggle System Console)")


# ------------------------------------------------------------------
# Registro
# ------------------------------------------------------------------
classes = (
    IFC_OT_AnalisarModelo,
    IFC_PT_PainelPrincipal,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.ifc_path = bpy.props.StringProperty(
        name="Caminho IFC",
        description="Caminho completo para o arquivo .ifc",
        default=IFC_PATH_DEFAULT,
        subtype="FILE_PATH",
    )


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.ifc_path


# Permite rodar diretamente pelo Text Editor do Blender
if __name__ == "__main__":
    register()
