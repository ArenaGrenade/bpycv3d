import bpy

bl_info = {
    "name": "bpycv3d",
    "description": "A simple and intuitive UI for the functionality provided by the bpycv3d library.",
    "author": "Rohan Asokan",
    "license": "MIT",
    "deps": "",
    "version": (1, 1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Tools > BPYCV3D",
    "warning": "",
    "wiki_url": "https://bpycv3d.readthedocs.io/en/latest/",
    "tracker_url": "https://github.com/ArenaGrenade/bpycv3d/issues",
    "link": "https://github.com/ArenaGrenade/bpycv3d",
    "support": "COMMUNITY",
    "category": "Object"
}

import bpy
from bpycv3d import DataCapture, CameraRandomizer

valid_passes = [
    "diffuse_color", "diffuse_indirect", "diffuse_direct",
    "glossy_color", "glossy_indirect", "glossy_direct",
    "emit", "normal", "position", "object_index"
]

class PluginSettings(bpy.types.PropertyGroup):
    engine_type: bpy.props.EnumProperty(items=[
        ("CYCLES", "Cycles", "Cycles Engine", 0),
        ("BLENDER_WORKBENCH", "Workbench", "Workbench Engine", 1),
        ("BLENDER_EEVEE", "Eevee", "Eevee Engine", 2),
    ], name="Engine")
    
    diffuse_color: bpy.props.BoolProperty(name="Diffuse Color")
    diffuse_indirect: bpy.props.BoolProperty(name="Diffuse Indirect")
    diffuse_direct: bpy.props.BoolProperty(name="Diffuse Direct")
    glossy_color: bpy.props.BoolProperty(name="Glossy Color")
    glossy_indirect: bpy.props.BoolProperty(name="Glossy Indirect")
    glossy_direct: bpy.props.BoolProperty(name="Glossy Direct")
    emit: bpy.props.BoolProperty(name="Emit")
    normal: bpy.props.BoolProperty(name="Normal")
    position: bpy.props.BoolProperty(name="Position")
    object_index: bpy.props.BoolProperty(name="Object Index")
    
    camera_follow_path: bpy.props.StringProperty(name="Camera Follow Path")
    camera_target: bpy.props.StringProperty(name="Camera Target")
    camera_num_samples: bpy.props.IntProperty(name="Number of Samples", default=10, min=1)

class BPYCV3DOperator(bpy.types.Operator):
    bl_idname = "bpycv3d.capture_samples_operator"
    bl_label = "Capture Data"
    
    def execute(self, context):
        settings = context.scene.plugin_settings
        dc_config = {
            "engine": settings.engine_type,
            "passes": [
                active_pass
                for active_pass in valid_passes
                if settings.get(active_pass) == True
            ]
        }
        dc = DataCapture.DataCapture(dc_config)
        
        cfp_config = {
            "follow_path": settings.camera_follow_path,
            "target": settings.camera_target,
            "num_samples": settings.camera_num_samples
        }
        cfp = CameraRandomizer.CameraFollowPath(cfp_config)
        
        for i in range(cfp_config["num_samples"]):
            cfp.step()
        
        # dc.render_multiple("frame")
        
        return {"FINISHED"}

class BPYCV3DPanel(bpy.types.Panel):
    bl_label = "BPYCV3D"
    bl_idname = 'OBJECT_PT_testing_panel'
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BPYCV3D"
    
    def draw(self, context):
        self.layout.prop(context.scene.plugin_settings, 'engine_type')
        col = self.layout.column(heading="Passes")
        col.prop(context.scene.plugin_settings, 'diffuse_color')
        col.prop(context.scene.plugin_settings, 'diffuse_indirect')
        col.prop(context.scene.plugin_settings, 'diffuse_direct')
        col.prop(context.scene.plugin_settings, 'glossy_color')
        col.prop(context.scene.plugin_settings, 'glossy_indirect')
        col.prop(context.scene.plugin_settings, 'glossy_direct')
        col.prop(context.scene.plugin_settings, 'emit')
        col.prop(context.scene.plugin_settings, 'normal')
        col.prop(context.scene.plugin_settings, 'position')
        col.prop(context.scene.plugin_settings, 'object_index')
        
        self.layout.prop(context.scene.plugin_settings, 'camera_follow_path')
        self.layout.prop(context.scene.plugin_settings, 'camera_target')
        self.layout.prop(context.scene.plugin_settings, 'camera_num_samples')
        
        self.layout.operator(BPYCV3DOperator.bl_idname, text="Capture Data")

CLASSES = [
    PluginSettings,
    BPYCV3DOperator,
    BPYCV3DPanel
]

def register():
    for c in CLASSES:
        bpy.utils.register_class(c)
    bpy.types.Scene.plugin_settings = bpy.props.PointerProperty(type=PluginSettings)

def unregister():
    for c in CLASSES:
        bpy.utils.unregister_class(c)
    del bpy.types.Scene.plugin_settings
    
if __name__ == "__main__":
    register()
