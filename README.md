# James Vella Cinema 4D Scripts 
My collection of Cinema4d scripts. Currently written for Maxon Cinema 4D R21.207 in Python version 2.7.18

# How to use
- Download the .py file
- Open your 3D scene in Cinema4D
- In Cinema -> Extensions -> User Scripts - > Run Script -> Locate download .py file

# Script descriptions
JV_AddSubdivisionAllObjects.py

- Applies subdivision modifier to all objects at the top of the hirearchy. Grouped items are given 1 subdivision for all items in that group. Non grouped items are each given a subdivision modifier.

JV_FBXMaterialsToCorona.py
- Converts imported FBX materials to Corona materials.
- Works best with V-Ray Roughness materials that have been converted to Standard materials before exporting to FBX. 
- When exporting from 3dsmax use this script to convert and export to FBX first for most optimal results (JV_VrayRoughnessToFBX.ms): https://github.com/jmdvella/3dsmax-scripts

JV_FBXMaterialsToPhysical.py
- Converts imported FBX materials to Physical materials.
- Works best with V-Ray Roughness materials that have been converted to Standard materials before exporting to FBX. 
- When exporting from 3dsmax use this script to convert and export to FBX first for most optimal results (JV_VrayRoughnessToFBX.ms): https://github.com/jmdvella/3dsmax-scripts

JV_FBXMaterialsToVray.py
- Converts imported FBX materials to V-Ray materials.
- Works best with V-Ray Roughness materials that have been converted to Standard materials before exporting to FBX. 
- When exporting from 3dsmax use this script to convert and export to FBX first for most optimal results (JV_VrayRoughnessToFBX.ms): https://github.com/jmdvella/3dsmax-scripts

JV_ResetAxisFrom3dsmax.py
- Flips Z/Y Axis for FBX models imported from 3dsmax.
- Works for Nulls, Nested Nulls & Polygon objects.
- Make sure you reset transform/xforms on all objects before grouping and exporting from 3dsmax.
