# James Vella Cinema 4D Scripts 
My collection of Cinema4d scripts. Currently written for Maxon Cinema 4D R21.207 in Python version 2.7.18

<br />

# How to use
- Download the .py file
- Open your 3D scene in Cinema4D
- Cinema4D -> Main Menu -> Extensions -> User Scripts - > Run Script -> Locate download .py file

<br />

# Script descriptions
### JV_AddSubdivisionAllObjects.py
- Applies Subdivision modifier to all objects at the top of the hirearchy
- Grouped items are given 1 Subdivision for all items in that group
- Non grouped items are each given a Subdivision modifier

<br />

### JV_FBXMaterialsToCorona.py
- Converts imported FBX materials to Corona materials
- Intended for V-Ray Roughness materials that have been converted to Standard materials before exporting to FBX 
- When exporting from 3dsmax use this script to convert and export to FBX first (JV_VrayRoughnessToFBX.ms): https://github.com/jmdvella/3dsmax-scripts
#### Supports:
- Diffuse & Diffuse Color
- Roughness
- Metal
- Normal Bump
- Alpha/Opacity
- Transmissive - any materials using "Transparency" will be converted to Glass.  - Comment out line 63-73 if not required
#### Scripting Note:
Change/Add your own material settings in Function: newCoronaMaterial(current_material, new_corona_mat)

<br />

### JV_FBXMaterialsToPhysical.py
- Converts imported FBX materials to Physical materials
- Intended for V-Ray Roughness materials that have been converted to Standard materials before exporting to FBX
- When exporting from 3dsmax use this script to convert and export to FBX first (JV_VrayRoughnessToFBX.ms): https://github.com/jmdvella/3dsmax-scripts
#### Supports:
- Diffuse & Diffuse Color 
- Roughness - materials without a roughness texture will be set to roughness 100%
- Metal
- Normal Bump
- Transmissive - any materials using "Transparency" will be converted to Glass. Comment out line 158-174 if not required
- Other textures will be kept in the conversion but not color profile corrected (linear/srgb)
#### Scripting Note:
Change/Add your own material settings in Function: convertMaterials(mat)

<br />

### JV_FBXMaterialsToVray.py
- Converts imported FBX materials to V-Ray materials
- Intended for V-Ray Roughness materials that have been converted to Standard materials before exporting to FBX 
- When exporting from 3dsmax use this script to convert and export to FBX first (JV_VrayRoughnessToFBX.ms): https://github.com/jmdvella/3dsmax-scripts
- Warning: Preferences will be permanently changed - Comment out line 208 if not required
#### Supports:
- Diffuse & Diffuse Color
- Roughness
- Metal
- Normal Bump
- Alpha/Opacity
- Transmissive - any materials using "Transparency" will be converted to Glass - Comment out line 68-79 if not required
#### Scripting Note:
Change/Add your own material settings in Function: newVrayMaterial(current_material, new_vray_mat)

<br />

### JV_FlipYZAxis.py
- Flips Y/Z Axis for imported FBX models with inverted axis (such as imported from 3dsmax)
- Works for Nulls, Nested Nulls & Polygon objects
- Make sure you reset transform/xforms on all objects before grouping and exporting to FBX
