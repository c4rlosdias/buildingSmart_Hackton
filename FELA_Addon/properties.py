import bpy
class Element(bpy.types.PropertyGroup):
    name      : bpy.props.StringProperty(name="Name")
    global_id : bpy.props.StringProperty(name="GlobalId")
    info      : bpy.props.StringProperty(name="Info")

class IFC_PG_Propriedades(bpy.types.PropertyGroup):
    specfilepath: bpy.props.StringProperty(
        name="Caminho IFC",
        description="Specification file",
        subtype="FILE_PATH",
        default="",
    )
    capabilities: bpy.props.EnumProperty(
        name="Capability",
        description="Selecione a capability do infobim para executar",
        items=[
            ("LIST_BUILDINGS", "Listar Edifícios", "Lista os edifícios e pavimentos do arquivo IFC"),
            ("LIST_ELEMENTS", "Listar Elementos", "Lista os elementos de uma classe IFC específica"),
            ("INSPECT_ELEMENT", "Inspecionar Elemento", "Inspeciona um elemento pelo GlobalId"),
            ("LIST_PROPERTY_SETS", "Listar Property Sets", "Lista os property sets de um elemento específico"),
        ],
        default="LIST_BUILDINGS",
    )
    elements: bpy.props.CollectionProperty(name="Elements", type=Element)