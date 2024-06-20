# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#    https://github.com/Korchy/1d_planar_edges

import bmesh
import bpy
from bpy.props import EnumProperty, FloatProperty
from bpy.types import Operator, Panel, Scene
from bpy.utils import register_class, unregister_class
from mathutils import Vector
from math import isclose

bl_info = {
    "name": "Planar Edges",
    "description": "Select edges parallel XY/YZ/XZ base scene planes",
    "author": "Nikita Akimov, Paul Kotelevets",
    "version": (1, 0, 0),
    "blender": (2, 79, 0),
    "location": "View3D > Tool panel > 1D > Planar Edges",
    "doc_url": "https://github.com/Korchy/1d_planar_edges",
    "tracker_url": "https://github.com/Korchy/1d_planar_edges",
    "category": "All"
}


# MAIN CLASS

class Planar:

    @classmethod
    def select_edges_perpendicular_vector(cls, context, vector=Vector((0.0, 0.0, 1.0)), threshold=0.0001):
        # select all edges that ara perpendicular specified vector
        src_obj = context.active_object
        # current mode
        mode = src_obj.mode
        # switch to OBJECT mode
        if src_obj.mode == 'EDIT':
            bpy.ops.object.mode_set(mode='OBJECT')
        # switch to "edge selection" mode
        context.tool_settings.mesh_select_mode = (False, True, False)
        # process with bmesh
        bm = bmesh.new()
        bm.from_mesh(src_obj.data)
        bm.edges.ensure_lookup_table()
        # deselect all
        cls._deselect_all(bm=bm)
        # select edges perpendicular to vector (dot product == 0)
        edges = [edge for edge in bm.edges
                 if isclose((edge.verts[1].co - edge.verts[0].co).dot(vector), 0, abs_tol=threshold)]
        for edge in edges:
            edge.select = True
        # save changed data to mesh
        bm.to_mesh(src_obj.data)
        bm.free()
        # return mode back
        bpy.ops.object.mode_set(mode=mode)

    @staticmethod
    def plane_normal(plane='XY'):
        # get normal by plane
        if plane == 'XZ':
            return Vector((0.0, 1.0, 0.0))
        elif plane == 'YZ':
            return Vector((1.0, 0.0, 0.0))
        else:   # 'XY'
            return Vector((0.0, 0.0, 1.0))

    @staticmethod
    def _deselect_all(bm):
        # remove all selection in bmesh
        for face in bm.faces:
            face.select = False
        for edge in bm.edges:
            edge.select = False
        for vertex in bm.verts:
            vertex.select = False

    @staticmethod
    def ui(layout, context):
        # ui panel
        layout.prop(
            data=context.scene,
            property='planar_props_threshold'
        )
        # Select edges
        op = layout.operator(
            operator='planar.select_edges',
            icon='MANIPUL'
        )
        layout.prop(
            data=context.scene,
            property='planar_props_plane',
            expand=True
        )
        op.plane = context.scene.planar_props_plane


# OPERATORS

class Planar_OT_select_edges(Operator):
    bl_idname = 'planar.select_edges'
    bl_label = 'Select Planar Edges'
    bl_description = 'Select Planar Edges'
    bl_options = {'REGISTER', 'UNDO'}

    plane = EnumProperty(
        name='Plane',
        items=[
            ('XY', 'XY', 'XY', '', 0),
            ('YZ', 'YZ', 'YZ', '', 1),
            ('XZ', 'XZ', 'XZ', '', 2)
        ],
        default='XY'
    )

    def execute(self, context):
        # get edges parallel to the self.plane
        #   edges will be parallel if dot product of plane normal and vector formed by edge will be == 0
        #   (plane normal is perpendicular edge vector)
        # get plane normal vector
        plane_normal = Planar.plane_normal(plane=self.plane)
        # select edges perpendicular for this vector
        Planar.select_edges_perpendicular_vector(
            context=context,
            vector=plane_normal,
            threshold=context.scene.planar_props_threshold
        )
        return {'FINISHED'}


# PANELS

class Planar_PT_panel(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = "Select Planar Edges"
    bl_category = '1D'

    def draw(self, context):
        Planar.ui(
            layout=self.layout,
            context=context
        )


# REGISTER

def register(ui=True):
    Scene.planar_props_plane = EnumProperty(
        name='Plane',
        items=[
            ('XY', 'XY', 'XY', '', 0),
            ('YZ', 'YZ', 'YZ', '', 1),
            ('XZ', 'XZ', 'XZ', '', 2)
        ],
        default='XY'
    )
    Scene.planar_props_threshold = FloatProperty(
        name='Threshold',
        default=0.001
    )
    register_class(Planar_OT_select_edges)
    if ui:
        register_class(Planar_PT_panel)


def unregister(ui=True):
    if ui:
        unregister_class(Planar_PT_panel)
    unregister_class(Planar_OT_select_edges)
    del Scene.planar_props_threshold
    del Scene.planar_props_plane


if __name__ == "__main__":
    register()
