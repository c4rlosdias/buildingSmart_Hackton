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
    "name": "Deterministic IA IFC",
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

addon_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(addon_dir, "Lib", "site-packages"))

from .properties import IFC_PG_Propriedades, Element
from .operators import IFC_OT_ExecutarExterno
from .panels import IFC_PT_PainelPrincipal

# ------------------------------------------------------------------
# Registro
# ------------------------------------------------------------------
classes = (
    Element,
    IFC_PG_Propriedades,
    IFC_OT_ExecutarExterno,
    IFC_PT_PainelPrincipal,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.ifc_props = bpy.props.PointerProperty(type=IFC_PG_Propriedades)
    print("[Deterministic IA IFC] Addon registrado com sucesso! Abra o N-panel (tecla N) na Viewport 3D e clique na aba 'IFC'.")


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    if hasattr(bpy.types.Scene, "ifc_props"):
        del bpy.types.Scene.ifc_props
    print("[Deterministic IA IFC] Addon desregistrado.")



