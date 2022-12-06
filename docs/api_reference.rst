API Reference
=============

.. py:class:: bpycv3d.CameraRandomizer.CameraRandomizer(config)

    This class enables camera to move along a path within the scene. Please refer to :ref:`camera-randomization-starter` for information on how to setup this path.

    :param dict config: Configuration dict with valid keys being num_samples, forward_axis, up_axis, track_axis, follow_path, camera. All parameters except num_samples (int) are strings.
        
        Here, follow_path, target are compulsary keys - follow_path is the name of the curve created in the scene that the camera is to attach to, while target is the name of the object that the camera is to look at always.

        num_samples denotes the number of frames in the output and defaults to 10.

        forward_axis and track_axis can be "FORWARD_X", "FORWARD_Y", "FORWARD_Z", "TRACK_NEGATIVE_X", "TRACK_NEGATIVE_Y", "TRACK_NEGATIVE_Z". For further details on these values please refer to `Blender Docs <https://docs.blender.org/api/current/bpy.types.FollowPathConstraint.html#bpy.types.FollowPathConstraint>`_. up_axis can be "UP_X", "UP_Y", "UP_Z".
        
        Note: If this is your first time running the script please do not set camera, allow the module to create its own camera with the right configuration, after which you can refer to that camera here using the name of that camera object in blender.

    .. py:method:: step(self)
        
        This function is used in cases where one wants to export custom data capture parameters, then one would loop through the total number of samples or as many number of samples requried (the frames cycle through), and call step of this and render of DataCapture to attain the required frames. This function essentially steps up to the next frame.

.. py:class:: bpycv3d.DataCapture.DataCapture(config, custom_function=None, camera_randomizer=None)

    This class handles all the data capture work from the active scene camera. This is where the capture of different render passes takes place.

    :param dict config: Configuration dictionary with valid keys being engine and passes. Valid Engine values are CYCLES, BLENDER_WORKBENCH, BLENDER_EEVEE. Valid passes include diffuse_color, diffuse_indirect, diffuse_direct, glossy_color, glossy_indirect, glossy_direct, emit, normal, position, object_index.

    :param function custom_function: This is a custom function following the signature f(is_intersect, hit_location, nearest_light_position, nearest_light_color_alpha, nearest_light_indices, lights) -> dict(). All input parameters to the function are numpy arrays. A complete description of the parameters can be found at :ref:`custom-dc-layer-function-ref`

    :param bpycv3d.CameraRandomizer.CameraRandomizer camera_randomizer: If you are using a camera randomizer, please pass the object here. This is to ensure order of execution and simpler handling of camera objects within a custom data capture pass.

    .. py:method:: custom_function_implementation(self, func)

        :param function func: Please refer to custom_function description above and to :ref:`custom-dc-layer-function-ref`

    .. py:method:: render(self, path)

        Calling this method renders the current camera view onto the location pointed to by path with all the view layers as required. Any custom data retured is stored as `.npy` files. The standard passes provided are stored as `MultiLayer EXR` while previews of these camera views are also stored as `.jpg`.

        :param string path: The default location is a renders directory on the same level directory as your blend file that is currently open. Please provide a relative pathing using this variable. For instance, providing `path=test_img` would create `test_img.jpg`, `test_img.exr`, `test_img_custom_property.npy`, where custom_property is a property returned by the custom data capture pass.
    
    .. py:method:: render_multiple(self, path)

        This is a method that assumes that the camera randomizer has made the camera location change over multiple frames. This method would then save all the frames in the camera randomization similar to the render function. Note: This method does not handle custom data capture passes. Please use the above render functionality with camera randomizer's step functionality to achieve a similar effect.

        :param string path: This method uses path differently to the above. For instance, providing `path=test_img` would create `test_img_0.jpg`, `test_img_0.exr`, `test_img_1.jpg`, and so on.


.. _custom-dc-layer-function-ref:

Custom Data Capture Function
----------------------------

.. py:function:: custom_dc_layer_function(is_intersect, hit_location, nearest_light_position, nearest_light_color_alpha, nearest_light_indices, lights)

    Casts multiple rays from the camera at each pixel and gets data from the hit and scene light data.

    :param hit_location: 3-channel float32 Array representing the location where a ray hit.
    :param is_intersect: Boolean Numpy Array representing if the ray at the pixel had a hit.
    :param nearest_light_position: Calculated nearest light position at hit location.
    :param nearest_light_color_alpha: 4-channel float32 Array. First 3 channels provide the color of the nearest light, while the last channel provides the energy provided by the light at the hit location.
    :param nearest_light_indices: This is related to the lights parameter. This index specifies the index in lights paramater of the closest light at hit location
    :param list lights: Low-level blender API reference to all the lights in the scene. This is provided so one can use the nearest_light_indices and this list to get further details about the light itself.

