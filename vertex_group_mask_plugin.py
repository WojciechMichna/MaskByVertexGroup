bl_info = {
    "name": "Mask by vertex group",
    "blender": (4, 0, 0),
    "category": "Object",
    "version": (0, 0, 1),
    "author": "Wojciech Michna",
    "description": "A Blender plugin that applies a mask based on vertex groups in sculpt mode, allowing for targeted sculpting on specific areas of the model.",
}


import bpy
import bmesh
import numpy as np


def mask_by_group_tab_function(vertex_group_name):
    obj = bpy.context.object
    if obj is None or obj.type != 'MESH':
        print("No valid mesh object selected.")
        return

    # Get the vertex group by name
    vgroup = obj.vertex_groups.get(vertex_group_name)
    if vgroup is None:
        print(f"Vertex group '{vertex_group_name}' not found.")
        return

    # Create an empty list to store vertex indices
    vertex_indices = []

    # Iterate over the vertices of the mesh
    for vert in obj.data.vertices:
        for group in vert.groups:
            if group.group == vgroup.index:
                vertex_indices.append(vert.index)  # Add the vertex index to the list

    bm = bmesh.new()
    bm.from_mesh(obj.data)

    mask_layer = bm.verts.layers.paint_mask.verify()
    bm.verts.ensure_lookup_table()

    mask_value = 1.0
    for idx in np.array(vertex_indices, dtype=np.int64):
        bm.verts[idx][mask_layer] = mask_value

    bm.to_mesh(obj.data)

    # Update the object and force a redraw
    obj.data.update()  # Update the mesh data
    bpy.context.view_layer.objects.active.update_tag()  # Tag the object for update
    bpy.context.view_layer.update()  # Update the scene/view layer
    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)  # Force viewport redraw


# Create a new tab in the sidebar (next to "View" and "Tool")
class VIEW3D_PT_mask_by_group_tab(bpy.types.Panel):
    bl_label = "Mask by group"
    bl_idname = "VIEW3D_PT_mask_by_group_tab"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Mask by group'  # This will add a new tab next to "View" and "Tool"

    @classmethod
    def poll(cls, context):
        # Panel will only show up if a mesh object is active and in Edit or Sculpt mode
        return (context.object is not None and context.object.type == 'MESH'
                and context.mode in {'EDIT_MESH', 'SCULPT'})

    def draw(self, context):
        layout = self.layout
        obj = context.object

        # Check if the active object has vertex groups
        if obj and obj.type == 'MESH' and obj.vertex_groups:
            # Create a dropdown menu for vertex groups
            layout.prop(context.scene, "custom_vertex_group", text="Vertex Group")
        else:
            layout.label(text="No Vertex Groups Found")

        # Add the button to trigger function foo
        layout.operator("object.mask_by_group_button", text="Mask by group")


# Define an operator to trigger the foo function
class OBJECT_OT_mask_by_group_button(bpy.types.Operator):
    bl_label = "Mask By Group"
    bl_idname = "object.mask_by_group_button"

    def execute(self, context):
        vertex_group_name = context.scene.custom_vertex_group  # Get the chosen vertex group name
        mask_by_group_tab_function(vertex_group_name)
        return {'FINISHED'}


# Property to hold the vertex group name selection
def update_vertex_group_list(self, context):
    obj = context.object
    if obj and obj.type == 'MESH' and obj.vertex_groups:
        return [(vg.name, vg.name, "") for vg in obj.vertex_groups]
    return []


# Register and Unregister classes
def register():
    bpy.utils.register_class(VIEW3D_PT_mask_by_group_tab)
    bpy.utils.register_class(OBJECT_OT_mask_by_group_button)

    # Define custom property for vertex group selection in the scene
    bpy.types.Scene.custom_vertex_group = bpy.props.EnumProperty(
        items=update_vertex_group_list,
        name="Vertex Group",
        description="Choose a vertex group"
    )


def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_mask_by_group_tab)
    bpy.utils.unregister_class(OBJECT_OT_mask_by_group_button)

    del bpy.types.Scene.custom_vertex_group


if __name__ == "__main__":
    register()
