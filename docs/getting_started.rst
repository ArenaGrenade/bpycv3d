Getting Started
===============

Before starting with this, follow the installation guidelines to install the `bpycv3d` package: :doc:`installation`

Hello World Script
------------------

.. code-block :: python
    :caption: Simple script to export diffuse properties of the scene from the scene's default camera
    :linenos:

    import bpy
    from bpycv3d import DataCapture, CameraRandomizer

    dc_config = {
        "engine": "blender_eevee",
        "passes": [
            "diffuse_color", "diffuse_indirect", "diffuse_direct"
        ]
    }
    dc = DataCapture.DataCapture(dc_config)
    dc.render(f"frame")

This would output two images - one MultiLayerEXR and another preview image of the complete render pipeline.

.. _camera-randomization-starter:

Camera Randomization Starter
----------------------------

Now, to run any camera randomization strategy, we need curves to ensure uniformly sampled views around an object.

- Active the Curve Plugin: Edit > Preferences > Add-ons
- Search for Curve and activate the add-on Curve Tools
- In the 3d Viewport add a new curve object and structure it however you would like to within the scene.

Below, in the `follow_path` under `cfp_config` set it to the name of the curve you just created.

The `target` similarly should be set to the name of the object that you want the camera to be focussed on. You could use an empty object here too.

.. code-block :: python
    :caption: Camera Randomization added to our hello world script above

    import bpy
    from bpycv3d import DataCapture, CameraRandomizer

    dc_config = {
        "engine": "cycles",
        "passes": [
            "glossy_color", "glossy_indirect", "glossy_direct"
        ]
    }
    dc = DataCapture.DataCapture(dc_config)

    cfp_config = {
        "follow_path": ________,
        "target": _______,
        "num_samples": 20
    }
    cfp = CameraRandomizer.CameraFollowPath(cfp_config)

    for i in range(cfp_config["num_samples"]):
        dc.render(f"frame_{i}")
        cfp.step()

This script would now render 20 images along the path with the camera looking at the target object both as MultiLayerEXR with all the passes required as well as a preview image.
