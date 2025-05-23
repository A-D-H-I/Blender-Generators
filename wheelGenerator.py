bl_info = {
    "name": "Wheel Generator",
    "author": "Your Name",
    "version": (1, 1),
    "blender": (2, 80, 0),
    "description": "Generate wheels with rims, tires, and aligned spokes with textured tire surface and metallic rim/spokes.",
    "category": "Object",
}

import bpy
import math
from mathutils import Vector

# === Update Handler ===
def update_wheel(self, context):
    bpy.ops.mesh.generate_wheel('INVOKE_DEFAULT')

# === Add-on Properties ===
class WHEELGEN_Props(bpy.types.PropertyGroup):
    rim_radius: bpy.props.FloatProperty(name="Rim Radius", default=0.5, update=update_wheel)
    rim_width: bpy.props.FloatProperty(name="Rim Width", default=0.2, update=update_wheel)
    tire_thickness: bpy.props.FloatProperty(name="Tire Thickness", default=0.1, update=update_wheel)
    spoke_count: bpy.props.IntProperty(name="Spoke Count", default=6, min=1, max=100, update=update_wheel)
    apply_materials: bpy.props.BoolProperty(name="Apply Materials", default=True, update=update_wheel)

# === UI Panel ===
class WHEELGEN_PT_Panel(bpy.types.Panel):
    bl_label = "Wheel Generator"
    bl_idname = "WHEELGEN_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "WheelGen"

    def draw(self, context):
        layout = self.layout
        props = context.scene.wheel_gen_props

        layout.prop(props, "rim_radius")
        layout.prop(props, "rim_width")
        layout.prop(props, "tire_thickness")
        layout.prop(props, "spoke_count")
        layout.prop(props, "apply_materials")
        layout.operator("mesh.generate_wheel", text="Generate Wheel")

# === Operator ===
class GenerateWheelOperator(bpy.types.Operator):
    bl_idname = "mesh.generate_wheel"
    bl_label = "Generate Wheel"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.wheel_gen_props

        # Clear previous wheel objects
        for obj in bpy.context.scene.objects:
            if obj.name.startswith(("Rim", "Tire", "Spoke_")):
                bpy.data.objects.remove(obj, do_unlink=True)

        # Create rim (a cylinder)
        rim = self.create_rim(props.rim_radius, props.rim_width)
        # Create tire (a torus scaled in Z to simulate tire width)
        tire = self.create_tire(props.rim_radius + props.tire_thickness, props.rim_width + 0.05)
        # Create spokes (each spanning from the rim outer edge to the inner tire boundary)
        spokes = self.create_spokes(props.rim_radius, props.tire_thickness, props.spoke_count)

        all_parts = [rim, tire] + spokes

        if props.apply_materials:
            metal_mat = self.create_rim_material()
            rim.data.materials.append(metal_mat)
            for spoke in spokes:
                spoke.data.materials.append(metal_mat)
            tire.data.materials.append(self.create_tire_material())

        bpy.ops.object.select_all(action='DESELECT')
        for obj in all_parts:
            obj.select_set(True)
        context.view_layer.objects.active = rim
        bpy.ops.object.join()
        bpy.context.active_object.location = (0, 0, 0)
        return {'FINISHED'}

    def create_rim(self, radius, width):
        bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=radius, depth=width)
        rim = bpy.context.active_object
        rim.name = "Rim"
        return rim

    def create_tire(self, radius, width):
        bpy.ops.mesh.primitive_torus_add(major_radius=radius, minor_radius=0.05, major_segments=64)
        tire = bpy.context.active_object
        tire.name = "Tire"
        tire.scale = (1, 1, width / 0.1)
        return tire

    def create_spokes(self, rim_radius, tire_thickness, count):
        spokes = []
        inner_tire_radius = rim_radius + tire_thickness - 0.05
        spoke_length = inner_tire_radius - rim_radius

        for i in range(count):
            angle = math.radians((360 / count) * i)
            bpy.ops.mesh.primitive_cylinder_add(radius=0.01, depth=spoke_length)
            spoke = bpy.context.active_object
            spoke.name = f"Spoke_{i}"
            spoke.rotation_euler[1] = math.radians(90)
            spoke.rotation_euler[2] = angle
            spoke.location = Vector((
                (rim_radius + spoke_length / 2) * math.cos(angle),
                (rim_radius + spoke_length / 2) * math.sin(angle),
                0
            ))
            spokes.append(spoke)
        return spokes

    def create_rim_material(self):
        mat = bpy.data.materials.get("RimMaterial")
        if not mat:
            mat = bpy.data.materials.new(name="RimMaterial")
            mat.use_nodes = True
            nodes = mat.node_tree.nodes
            bsdf = nodes.get("Principled BSDF")
            if bsdf:
                bsdf.inputs["Metallic"].default_value = 1.0
                bsdf.inputs["Roughness"].default_value = 0.3
        return mat

    def create_tire_material(self):
        mat = bpy.data.materials.get("TireMaterial")
        if not mat:
            mat = bpy.data.materials.new(name="TireMaterial")
            mat.use_nodes = True
            nodes = mat.node_tree.nodes
            links = mat.node_tree.links
            for node in nodes:
                nodes.remove(node)
            output = nodes.new(type='ShaderNodeOutputMaterial')
            output.location = (400, 0)
            bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
            bsdf.location = (0, 0)
            bsdf.inputs["Base Color"].default_value = (0.02, 0.02, 0.02, 1)
            bsdf.inputs["Roughness"].default_value = 0.7
            noise = nodes.new(type='ShaderNodeTexNoise')
            noise.location = (-400, 100)
            noise.inputs["Scale"].default_value = 5.0
            noise.inputs["Detail"].default_value = 2.0
            bump = nodes.new(type='ShaderNodeBump')
            bump.location = (-200, 0)
            bump.inputs["Strength"].default_value = 0.3
            links.new(noise.outputs["Fac"], bump.inputs["Height"])
            links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
            links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
        return mat

# === Registration ===
classes = [
    WHEELGEN_Props,
    WHEELGEN_PT_Panel,
    GenerateWheelOperator,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.wheel_gen_props = bpy.props.PointerProperty(type=WHEELGEN_Props)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.wheel_gen_props

if __name__ == "__main__":
    register()
