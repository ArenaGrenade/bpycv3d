Installation
============

Blender Installation
--------------------
Please follow instructions from https://www.blender.org/download/ to download blender version **2.8** or above.

The library must work for all operating systems of blender.

Dependencies
------------
The library requires the following exrtra packages to function:

- Numpy

Library Installation
--------------------
Find the blender root path of your OS from here: https://docs.blender.org/manual/en/latest/advanced/blender_directory_layout.html

Linux:

Assuming the version of blender is 3.3, the following are the paths we are interested in.
For linux the root path is `/usr/share/blender/3.3`.
And the Module Install Location is `/usr/share/blender/3.3/scripts/modules`.

.. code-block :: bash
    :caption: Installation Instructions on Linux

    git clone https://github.com/ArenaGrenade/bpycv3d.git
    cd bpycv3d
    cp -rip ./src/bpycv3d /usr/share/blender/3.3/scripts/modules

.. Note::
    The second step might require superuser permissions depending on your system setup.

.. _plugin-installation-ref:

Plugin Installation
-------------------
The plugin comes pre-packaged with the library, so the plugin would work without having to perform the library installation.

Step 1 is important to handle code-duplication and handling different versions of the library. For user purposes, this should not matter, please follow the instructions as specified and there would be no issues.

- Run the following script in any directory on linux. On any other OS, just move the directory as directed and zip the folder specified as below.

.. code-block :: bash
    :caption: Installation for Blender Addon
    
    git clone https://github.com/ArenaGrenade/bpycv3d.git
    cd bpycv3d
    cp -rip src/bpycv3d bpycv3dUI/
    zip -r bpycv3dUI.zip bpycv3dUI/

- Open up blender normally.
- Open AddOn Tab in Preferences using Edit > Preferences > Add-ons
- Press on Install and select the zip file you just created.
- The plugin should load up normally in the 3d viewport towards the right section.
