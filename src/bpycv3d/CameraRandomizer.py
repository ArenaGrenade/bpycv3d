import bpy

import json
import os
import math
import random

class CameraFollowPath(object):
    def __init__(self, config):
        if isinstance(config, str) and os.path.isfile(config):
            with open(config, "r") as config_file:
                config = json.load(config_file)
                
        assert isinstance(config, dict)
        
        # Defaults
        self.num_samples = 10
        self.current_frame = 0
        self.forward_axis = "TRACK_NEGATIVE_Z"
        self.up_axis = "UP_Y"
        self.track_axis = "TRACK_NEGATIVE_Z"
        
        for key, value in config.items():
            setattr(self, key, value)
            
        bpy.context.scene.frame_end = self.num_samples
            
        if not hasattr(self, "follow_path"): raise ValueError("follow_path attribute was not provided.")
        if not hasattr(self, "target"): raise ValueError("target attribute was not provided.")
        
        if not hasattr(self, "camera"):
            camera_data = bpy.data.cameras.new(name='Follow Cam')
            camera_object = bpy.data.objects.new('Follow Cam', camera_data)
            bpy.context.scene.collection.objects.link(camera_object)
            self.camera = bpy.context.scene.objects.get("Follow Cam")
        else:
            self.camera = bpy.context.scene.objects.get(self.camera)
        
        self.old_camera = bpy.context.scene.camera
        bpy.context.scene.camera = self.camera
        
        fp_constraint = self.camera.constraints.new('FOLLOW_PATH')
        fp_constraint.target = bpy.context.scene.objects.get(self.follow_path)
        fp_constraint.forward_axis = self.forward_axis
        fp_constraint.up_axis = self.up_axis
        fp_constraint.use_fixed_location = True
        
        if hasattr(self, "target"):
            tt_constraint = self.camera.constraints.new('TRACK_TO')
            tt_constraint.target = bpy.context.scene.objects.get(self.target)
            tt_constraint.up_axis = self.up_axis
            tt_constraint.track_axis = self.track_axis
            
        bpy.context.scene.frame_set(bpy.context.scene.frame_start)
        fp_constraint.offset_factor = 0.0
        fp_constraint.keyframe_insert(data_path='offset_factor')
        
        bpy.context.scene.frame_set(bpy.context.scene.frame_end)
        fp_constraint.offset_factor = 1.0
        fp_constraint.keyframe_insert(data_path='offset_factor')
        
        fcurves = self.camera.animation_data.action.fcurves
        for fcurve in fcurves:
            for kf in fcurve.keyframe_points:
                kf.interpolation = 'LINEAR'
                kf.easing = 'AUTO'
                
    def step(self):
        bpy.context.scene.frame_set(self.current_frame)
        self.current_frame += 1
        
        # This following will allow frames to loop over.
        if self.current_frame >= self.num_samples:
            self.current_frame = 0
        
        if self.randomly_orient_camera:
            self.camera.rotation_euler[2] += math.radians(random.randrange(-90, 90))

    def __del__(self):
        try:
            bpy.data.objects.remove(self.camera, do_unlink=True)
            bpy.context.scene.camera = self.old_camera
        except: pass
