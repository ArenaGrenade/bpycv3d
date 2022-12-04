import bpy

import json
import os

import numpy as np

class DataCapture(object):
    def __init__(self, config, custom_function=None, camera_randomizer=None):
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
        
        self.custom_function = custom_function
        self.camera_randomizer = camera_randomizer
            
    def custom_function_implementation(self, func):
        cam = self.camera_randomizer.camera
        matrix = cam.matrix_world.normalized()
        frame = [matrix @ v for v in cam.data.view_frame()]

        top_line = (frame[-1], frame[0])
        bot_line = (frame[-2], frame[1])
        res_x = bpy.context.scene.render.resolution_x
        res_y = bpy.context.scene.render.resolution_y

        top_linspace = np.dstack((np.linspace(top_line[0][i], top_line[1][i], res_x) for i in range(3)))[0]
        bot_linspace = np.dstack((np.linspace(bot_line[0][i], bot_line[1][i], res_x) for i in range(3)))[0]

        origin_pt = np.array(matrix.to_translation())

        clip_start, clip_end = cam.data.clip_start, cam.data.clip_end
        deps = bpy.context.evaluated_depsgraph_get()

        is_intersect = np.zeros((res_x, res_y), dtype=bool)
        hit_location = np.zeros((res_x, res_y, 3), dtype=np.float32)
        nearest_light_position = np.zeros((res_x, res_y, 3), dtype=np.float32)
        nearest_light_color_alpha = np.zeros((res_x, res_y, 4), dtype=np.float32)
        nearest_light_indices = np.zeros((res_x, res_y), dtype=int)

        lights = [ob for ob in bpy.context.scene.objects if ob.type == 'LIGHT']
        light_positions = []
        light_falloff = []
        light_energies = []
        for light in lights:
            if isinstance(light.data, bpy.types.PointLight):
                light_positions.append(light.location)
                light_falloff.append((light.data.distance ** 2) / 2)
                light_energies.append(light.data.energy)

        for i in range(top_linspace.shape[0]):
            p1 = top_linspace[i]
            p2 = bot_linspace[i]
            points = np.dstack((np.linspace(p1[k], p2[k], res_y) for k in range(3)))[0]
            for j in range(points.shape[0]):
                p = points[j]
                ray_direction = p - origin_pt
                start = origin_pt + ray_direction * clip_start
                end = origin_pt + ray_direction * clip_end
                result, location, _, _, _, _ = bpy.context.scene.ray_cast(deps, start, end)
                
                is_intersect[i][j] = result
                hit_location[i][j] = location
                
                distances = [np.linalg.norm(ld - location) for ld in light_positions]
                closest_index = np.argmin(distances)
                light_intensity_here = (light_falloff[closest_index] * light_energies[closest_index]) / (distances[closest_index] ** 2)
                
                nearest_light_position[i][j] = light_positions[closest_index]
                nearest_light_color_alpha[i][j] = np.array([*lights[closest_index].data.color, light_intensity_here])
                
                nearest_light_indices = closest_index
        
        return self.custom_function(is_intersect, hit_location, nearest_light_position, nearest_light_color_alpha, nearest_light_indices, lights)

    def render(self, path):
        old_file_path = bpy.context.scene.render.filepath
        bpy.context.scene.render.filepath = os.path.join(os.path.dirname(bpy.data.filepath ), "./renders/" + path.rsplit(".")[0])
        print("Rendering single image to ", bpy.context.scene.render.filepath)
        
        bpy.context.scene.render.image_settings.use_preview = True
        bpy.context.scene.render.image_settings.file_format = "OPEN_EXR_MULTILAYER"
        bpy.ops.render.render(animation=False, layer=self.active_view_layer.name, write_still=True)
        bpy.context.scene.render.image_settings.use_preview = False
        
        if self.custom_function:
            processed_returns = self.custom_function_implementation(self.custom_function)
            for ret_name, ret in processed_returns.items():
                try:
                    if ret.ndim == 3 and ret.shape[-1] == 3:
                        # RGB Image
                        path = os.path.join(os.path.dirname(bpy.data.filepath ), "./renders/" + path.rsplit(".")[0] + f"_{ret_name}" + ".npy")
                        print(f"Stored RGB {ret_name} at {path}")
                    elif ret.ndim == 2:
                        # Single Channel Image
                        path = os.path.join(os.path.dirname(bpy.data.filepath ), "./renders/" + path.rsplit(".")[0] + f"_{ret_name}" + ".npy")
                        print(f"Stored RGB {ret_name} at {path}")
                    elif ret.ndim == 3 and ret.shape[-1] == 4:
                        # RGBA Image
                        path = os.path.join(os.path.dirname(bpy.data.filepath ), "./renders/" + path.rsplit(".")[0] + f"_{ret_name}" + ".npy")
                        print(f"Stored RGB {ret_name} at {path}")
                    else:
                        # Unsupported storage
                        continue
                    with open(path, "wb") as f:
                        np.save(f, ret)
                except Exception as e:
                    # Unsupported storage
                    continue
        
        bpy.context.scene.render.filepath = old_file_path
    
    def render_multiple(self, path):
        old_file_path = bpy.context.scene.render.filepath
        bpy.context.scene.render.filepath = os.path.join(os.path.dirname(bpy.data.filepath ), "./renders/" + path.rsplit(".")[0] + "_")
        print("Rendering multiple images to ", bpy.context.scene.render.filepath + "***.exr")
        
        bpy.context.scene.render.image_settings.file_format = "OPEN_EXR_MULTILAYER"
        bpy.context.scene.render.image_settings.use_preview = True # Stores jpg preview files additionally
        bpy.ops.render.render(animation=True, layer=self.active_view_layer.name)
        
        bpy.context.scene.render.image_settings.use_preview = False
        bpy.context.scene.render.filepath = old_file_path

    def __del__(self):
        try:
            bpy.ops.scene.view_layer_remove()
            bpy.context.view_layer = self.old_view_layer
        except: pass
