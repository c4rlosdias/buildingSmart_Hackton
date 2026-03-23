import bpy
class Element(bpy.types.PropertyGroup):
    name      : bpy.props.StringProperty(name="Name")
    global_id : bpy.props.StringProperty(name="GlobalId")
    info      : bpy.props.StringProperty(name="Info")

class IFC_PG_Propriedades(bpy.types.PropertyGroup):
    idsfilepath: bpy.props.StringProperty(
        name="idsfilepath",
        description="ids file",
        subtype="FILE_PATH",
        default="",
    )
    idcsfilepath: bpy.props.StringProperty(
        name="idcsfilepath",
        description="idcs file",
        subtype="FILE_PATH",
        default="",
    )

    elements: bpy.props.CollectionProperty(name="Elements", type=Element)