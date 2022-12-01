import bpy

import json
import os

class DataCapture(object):
    def __init__(self, config):
        if isinstance(config, str) and os.path.isfile(config):
            with open(config, "r") as config_file:
                config = json.load(config_file)
                
        assert isinstance(config, dict)
        
        for key, value in config.items():
            setattr(self, key, value)
            
        # Set active engine
        self.engine = self.engine.upper()
        if self.engine in ("CYCLES", "BLENDER_WORKBENCH", "BLENDER_EEVEE"):
            bpy.context.scene.render.engine = self.engine
        else:
            AttributeError(f"{self.engine} is not a valid render engine in blender.")
            
        # Creates new layer
        self.old_view_layer = bpy.context.view_layer
        bpy.ops.scene.view_layer_add(type="NEW")
        self.active_view_layer = bpy.context.view_layer
        
        # Set attributes for output layers        
        for attr in self.passes:
            try:
                setattr(self.active_view_layer, f"use_pass_{attr}", True)
            except AttributeError as e:
                raise AttributeError(f"The pass {attr} is not a valid render pass in {self.engine} engine.") from e

    def render(self, path):
        old_file_path = bpy.context.scene.render.filepath
        bpy.context.scene.render.filepath = os.path.join(os.path.dirname(bpy.data.filepath ), "./renders/" + path.rsplit(".")[0])
        print("Rendering single image to ", bpy.context.scene.render.filepath)
        
        bpy.context.scene.render.image_settings.file_format = "OPEN_EXR_MULTILAYER"
        bpy.ops.render.render(animation=False, layer=self.active_view_layer.name, write_still=True)
        bpy.context.scene.render.image_settings.file_format = "PNG"
        bpy.ops.render.render(animation=False, layer=self.active_view_layer.name, write_still=True)
        
        bpy.context.scene.render.filepath = old_file_path
    
    def render_multiple(self, path):
        old_file_path = bpy.context.scene.render.filepath
        bpy.context.scene.render.filepath = os.path.join(os.path.dirname(bpy.data.filepath ), "./renders/" + path.rsplit(".")[0] + "_")
        print("Rendering multiple images to ", bpy.context.scene.render.filepath + "***.exr")
        
        bpy.context.scene.render.image_settings.file_format = "OPEN_EXR_MULTILAYER"
        bpy.context.scene.render.image_settings.use_preview = True # Stores jpg preview files additionally
        bpy.ops.render.render(animation=True, layer=self.active_view_layer.name)
        
        bpy.context.scene.render.filepath = old_file_path

    def __del__(self):
        try:
            bpy.ops.scene.view_layer_remove()
            bpy.context.view_layer = self.old_view_layer
        except: pass
