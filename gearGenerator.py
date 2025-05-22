bl_info = {
    "name": "Interactive Gear Generator",
    "author": "Your Name",
    "version": (1, 2),
    "blender": (2, 83, 0),
    "location": "3D View > Sidebar > Create",
    "description": "Generates gears with live preview",
    "warning": "",
    "doc_url": "",
    "category": "Object",
}

import bpy
import math
from mathutils import Vector
from bpy.app.handlers import persistent

# Global variable to track the active gear
active_gear = None

def create_gear_mesh(teeth, radius, depth, tooth_height, bevel):
    verts = []
    faces = []
    angle_step = 2 * math.pi / teeth
    inner_radius = radius - tooth_height

    # Generate vertices
    for i in range(teeth):
        angle1 = i * angle_step
        angle2 = (i + 0.5) * angle_step

        verts.append(Vector((
            radius * math.cos(angle1),
            radius * math.sin(angle1),
            0
        )))
        verts.append(Vector((
            inner_radius * math.cos(angle2),
            inner_radius * math.sin(angle2),
            0
        )))

    # Create faces
    for i in range(teeth):
        next_i = (i + 1) % teeth
        faces.append((
            2 * i,
            2 * next_i,
            2 * next_i + 1,
            2 * i + 1
        ))

    # Extrude depth
    verts += [Vector((v.x, v.y, -depth)) for v in verts[:2 * teeth]]
    
    # Side faces
    for i in range(teeth):
        next_i = (i + 1) % teeth
        faces.append((
            2 * i,
            2 * next_i,
            2 * next_i + 2 * teeth,
            2 * i + 2 * teeth
        ))
        faces.append((
            2 * i + 1,
            2 * next_i + 1,
            2 * next_i + 1 + 2 * teeth,
            2 * i + 1 + 2 * teeth
        ))

    # Bottom face
    faces.append([2 * teeth + i for i in reversed(range(2 * teeth))])

    return verts, faces

def update_gear(self, context):
    global active_gear
    
    if not active_gear:
        return
        
    scene = context.scene
    gear_settings = scene.gear_settings
    
    verts, faces = create_gear_mesh(
        gear_settings.teeth,
        gear_settings.radius,
        gear_settings.depth,
        gear_settings.tooth_height,
        gear_settings.bevel
    )
    
    # Update mesh data
    mesh = active_gear.data
    mesh.clear_geometry()
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    
    # Update bevel modifier
    if "Bevel" in active_gear.modifiers:
        active_gear.modifiers["Bevel"].width = gear_settings.bevel

class GearSettings(bpy.types.PropertyGroup):
    teeth: bpy.props.IntProperty(
        name="Teeth",
        default=12,
        min=3,
        max=100,
        update=update_gear
    )
    radius: bpy.props.FloatProperty(
        name="Radius",
        default=1.0,
        min=0.1,
        max=10.0,
        unit='LENGTH',
        update=update_gear
    )
    depth: bpy.props.FloatProperty(
        name="Thickness",
        default=0.2,
        min=0.01,
        max=2.0,
        unit='LENGTH',
        update=update_gear
    )
    tooth_height: bpy.props.FloatProperty(
        name="Tooth Height",
        default=0.3,
        min=0.01,
        max=1.0,
        unit='LENGTH',
        update=update_gear
    )
    bevel: bpy.props.FloatProperty(
        name="Bevel",
        default=0.05,
        min=0.0,
        max=0.5,
        unit='LENGTH',
        update=update_gear
    )

class GEAR_OT_add_gear(bpy.types.Operator):
    """Create a gear mesh"""
    bl_idname = "object.add_gear"
    bl_label = "Add Gear"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        global active_gear
        
        scene = context.scene
        gear_settings = scene.gear_settings
        
        verts, faces = create_gear_mesh(
            gear_settings.teeth,
            gear_settings.radius,
            gear_settings.depth,
            gear_settings.tooth_height,
            gear_settings.bevel
        )
        
        # Create mesh
        mesh = bpy.data.meshes.new("Gear")
        mesh.from_pydata(verts, [], faces)
        mesh.update()

        # Create object
        active_gear = bpy.data.objects.new("Gear", mesh)
        context.collection.objects.link(active_gear)
        context.view_layer.objects.active = active_gear
        active_gear.select_set(True)

        # Add bevel modifier
        bevel = active_gear.modifiers.new("Bevel", 'BEVEL')
        bevel.width = gear_settings.bevel
        bevel.segments = 2

        # Shade smooth
        bpy.ops.object.shade_smooth()

        return {'FINISHED'}

class GEAR_PT_panel(bpy.types.Panel):
    """Creates a Panel in the 3D Viewport sidebar"""
    bl_label = "Gear Generator"
    bl_idname = "VIEW3D_PT_gear_generator"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Create"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        gear_settings = scene.gear_settings

        # Input parameters
        layout.prop(gear_settings, "teeth")
        layout.prop(gear_settings, "radius")
        layout.prop(gear_settings, "depth")
        layout.prop(gear_settings, "tooth_height")
        layout.prop(gear_settings, "bevel")

        # Generate button
        layout.operator("object.add_gear")

classes = (
    GearSettings,
    GEAR_OT_add_gear,
    GEAR_PT_panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.gear_settings = bpy.props.PointerProperty(type=GearSettings)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    del bpy.types.Scene.gear_settings

if __name__ == "__main__":
    register()