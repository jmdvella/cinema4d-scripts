"""
JV_FBXMaterialsToVray
Author: James Vella
Website: http://www.jamesvella.net/
Name-US: JV_FBXMaterialsToVray
Version: 1.0.0
Written for Maxon Cinema 4D R21.207
Python version 2.7.18
Description-US: Convert FBX Standard Roughness Materials to Vray 5.0: supports:
                - Diffuse & Diffuse Color
                - Roughness
                - Metal
                - Normal Bump
                - Alpha/Opacity
                - Glass: any materials using "Transparency" will be converted to Glass - Comment out line 68-79 if not required

                Change/Add your own material settings in Function: newVrayMaterial(current_material, new_vray_mat)
                
                Warning: 
                Preferences will be permanently changed - Comment out line 208 if not required. Changes:
                Edit -> Preferences -> Renderer -> V-Ray -> Materials -> Previews -> Enable
                Edit -> Preferences -> Renderer -> V-Ray -> Materials -> Previews -> Editor Map Size: 1024x1024 (4MB)
"""

# Libraries
import c4d
from c4d import gui


# Class - Object iterator
class ObjectIterator :
        def __init__(self, baseObject):
            self.baseObject = baseObject
            self.currentObject = baseObject
            self.objectStack = []
            self.depth = 0
            self.nextDepth = 0

        def __iter__(self):
            return self

        def next(self):
            if self.currentObject == None :
                raise StopIteration

            obj = self.currentObject
            self.depth = self.nextDepth

            child = self.currentObject.GetDown()
            if child :
                self.nextDepth = self.depth + 1
                self.objectStack.append(self.currentObject.GetNext())
                self.currentObject = child
            else :
                self.currentObject = self.currentObject.GetNext()
                while( self.currentObject == None and len(self.objectStack) > 0 ) :
                    self.currentObject = self.objectStack.pop()
                    self.nextDepth = self.nextDepth - 1
            return obj


# Function - Convert current_material Materials to V-Ray Materials
def newVrayMaterial(current_material, new_vray_mat):
    # Set V-Ray Material Settings for both Metal/Dialectric materials
    new_vray_mat[c4d.BRDFVRAYMTL_OPTION_USE_ROUGHNESS] = True # Set Reflection -> "Use Roughness"
    new_vray_mat[c4d.BRDFVRAYMTL_REFLECT_VALUE] = c4d.Vector(255,255,255) # Set Reflection color -> White
    new_vray_mat[c4d.BRDFVRAYMTL_DIFFUSE_VALUE] = current_material[c4d.MATERIAL_COLOR_COLOR] # Copy Diffuse Color -> Vray Diffuse Color

    # Copy texture + paths from current_material to V-Ray Materials
    try:
        # Glass - OVERRIDE materials using Transparency in material with V-Ray Glass Shader Settings
        if current_material[c4d.MATERIAL_USE_TRANSPARENCY] == True: # If using Transparency in material
            new_vray_mat[c4d.BRDFVRAYMTL_REFRACT_VALUE] = c4d.Vector(255,255,255) # Set Refraction color -> White
            new_vray_mat[c4d.BRDFVRAYMTL_REFRACT_IOR_VALUE] = 1.517 # Set Fresnel -> 1.517 (Glass)
            new_vray_mat[c4d.BRDFVRAYMTL_REFLECT_VALUE] = c4d.Vector(255,255,255) # Set Reflection color -> White
            new_vray_mat[c4d.BRDFVRAYMTL_REFLECT_GLOSSINESS_VALUE] = 0 # No Roughness for Glass
    except:
        pass # Skip if material not Glass

    try:
        # Diffuse
        diffuse_shader = c4d.BaseList2D(c4d.Xbitmap) # Create empty bitmap shader

        new_diffuse_path = current_material[c4d.MATERIAL_COLOR_SHADER][c4d.BITMAPSHADER_FILENAME] # Location of current_material Diffuse texture
        new_vray_mat.InsertShader(diffuse_shader) # Insert diffuse shader into V-Ray material
        new_vray_mat[c4d.BRDFVRAYMTL_DIFFUSE_TEXTURE] = diffuse_shader # Set path of bitmap current_material -> bitmap path
        diffuse_shader[c4d.BITMAPSHADER_FILENAME] = new_diffuse_path # Assign texture path for bitmap to current_material -> bitmap path
    except:
        pass # Skip if some textures are not input

    try:
        # Roughness
        roughness_shader = c4d.BaseList2D(c4d.Xbitmap) # Create empty bitmap shader
        roughness_layer_id = current_material.GetReflectionLayerIndex(0) # Reflectance layer texture index location ('Specular')

        new_rough_path = current_material[roughness_layer_id.GetDataID() + c4d.REFLECTION_LAYER_MAIN_SHADER_ROUGHNESS][c4d.BITMAPSHADER_FILENAME] # current_material Reflectance Layers -> Specular -> Width / Texture remap to V-Ray Material -> Reflection -> Roughness
        new_vray_mat[c4d.BRDFVRAYMTL_REFLECT_GLOSSINESS_TEXTURE] = roughness_shader # Assign Specular texture to Reflection -> Roughness
        roughness_shader[c4d.BITMAPSHADER_FILENAME] = new_rough_path # Assign texture path for bitmap to current_material -> bitmap path
        new_vray_mat.InsertShader(roughness_shader) # Insert bitmap shader into V-Ray material
        new_vray_mat[c4d.BRDFVRAYMTL_REFLECT_GLOSSINESS_TEXTURE][c4d.BITMAPSHADER_COLORPROFILE] = 1 # Set Color Profile for bitmap -> linear
    except:
        pass # Skip if some textures are not input

    try:
        # Normal Bump
        if current_material[c4d.MATERIAL_BUMP_SHADER] != None: # If there is no texture in Bump skip this block
            normal_shader = c4d.BaseList2D(c4d.Xbitmap) # Create empty bitmap shader
            normal_vray_bump = c4d.BaseShader(1057881) # Create V-Ray Normal Texture
            new_vray_mat.InsertShader(normal_vray_bump) # Insert V-Ray Normal Texture into V-Ray Material
            new_vray_mat[c4d.BRDFVRAYMTL_BUMP_MAP] = normal_vray_bump # Assign V-Ray Normal Texture to Bump

            new_bump_path = current_material[c4d.MATERIAL_BUMP_SHADER][c4d.BITMAPSHADER_FILENAME] # current_material Normal Bump texture -> V-Ray Material -> Bump -> VrayNormalMap -> Map
            new_vray_mat[c4d.BRDFVRAYMTL_BUMP_MAP][c4d.TEXNORMALBUMP_BUMP_TEX_COLOR] = normal_shader # Create V-Ray material -> Bump Map -> VrayNormalMap bitmap shader
            new_vray_mat[c4d.MATERIAL_BUMP_SHADER] = normal_shader # Create empty bitmap shader
            normal_shader[c4d.BITMAPSHADER_FILENAME] = new_bump_path # Assign texture path for bitmap to current_material -> bitmap path
            new_vray_mat.InsertShader(normal_shader) # Insert bitmap shader into V-Ray material
            new_vray_mat[c4d.BRDFVRAYMTL_BUMP_MAP][c4d.TEXNORMALBUMP_BUMP_TEX_COLOR][c4d.BITMAPSHADER_COLORPROFILE] = 1 # Set Normal texture -> Color Profile -> Linear
            new_vray_mat[c4d.BRDFVRAYMTL_BUMP_MAP][c4d.TEXNORMALBUMP_MAP_TYPE] = 1 # Set Normal Map Type -> Tangent Space
    except:
        pass # Skip if some textures are not input

    try:
        # Opacity
        opacity_shader = c4d.BaseList2D(c4d.Xbitmap) # Create empty bitmap shader

        new_opacity_path = current_material[c4d.MATERIAL_ALPHA_SHADER][c4d.BITMAPSHADER_FILENAME] # Location of current_material Opacity texture
        new_vray_mat.InsertShader(opacity_shader) # Insert opacity shader into V-Ray material
        new_vray_mat[c4d.BRDFVRAYMTL_OPACITY_COLOR_TEXTURE] = opacity_shader # Set path of bitmap -> current_material -> bitmap path
        opacity_shader[c4d.BITMAPSHADER_FILENAME] = new_opacity_path # Assign texture path for bitmap to current_material -> bitmap path
        new_vray_mat[c4d.BRDFVRAYMTL_OPACITY_COLOR_TEXTURE][c4d.BITMAPSHADER_COLORPROFILE] = 1 # Set Opacity texture -> Color Profile -> Linear
    except:
        pass # Skip if some textures are not input

    try:
        # Metalness
        count_layer = current_material.GetReflectionLayerCount() # Check in material if there is more than 1 Reflectance layer (default 'Specular') & Metal Materials have ('Reflection' and 'Specular')
        if count_layer > 1:
            metal_shader = c4d.BaseList2D(c4d.Xbitmap) # Create empty bitmap shader
            metal_layer_id = current_material.GetReflectionLayerIndex(1)  # current_material Metal texture index location for current_material Material ('Reflection')

            new_metal_path = current_material[metal_layer_id.GetDataID() + c4d.REFLECTION_LAYER_COLOR_TEXTURE][c4d.BITMAPSHADER_FILENAME] # current_material Metal texture -> V-Ray Material -> Reflection -> Metalness
            new_vray_mat[c4d.BRDFVRAYMTL_METALNESS_TEXTURE] = metal_shader # Set path of bitmap current_material -> bitmap path
            metal_shader[c4d.BITMAPSHADER_FILENAME] = new_metal_path # Assign texture path for bitmap to current_material -> bitmap path
            new_vray_mat.InsertShader(metal_shader) # Insert bitmap shader into V-Ray material
            new_vray_mat[c4d.BRDFVRAYMTL_METALNESS_VALUE] = 1 # Set V-ray Material -> Reflection > Metalness to 1.0
            new_vray_mat[c4d.BRDFVRAYMTL_METALNESS_TEXTURE][c4d.BITMAPSHADER_COLORPROFILE] = 1 # Set Metal texture -> Color Profile -> Linear
    except:
        pass # Skip if some textures are not input

    return new_vray_mat


# Function - Convert materials from current_material to V-Ray
def convertMaterials(materials, collected_objs):
    for current_material in materials:
        new_vray_mat = c4d.BaseMaterial(1053286) # Create new V-Ray material
        doc.InsertMaterial(new_vray_mat) # Insert V-Ray material into document
        doc.AddUndo(c4d.UNDOTYPE_NEW, new_vray_mat) # New undo
        new_vray_mat.SetName(current_material.GetName()) # Assign V-Ray material name as current_material name
        replace_material = newVrayMaterial(current_material, new_vray_mat) # Run Function to replace current material with V-Ray material

       # Go through Objects -> Tags -> Texture Tags -> Replace Material
        for obj in collected_objs: # Loop through object selection
                tags = obj.GetTags() # Get objects tags

                for tag in tags: # Loop through tags
                    if type(tag).__name__ == "TextureTag": # If Texture tag founded
                        mat = tag.GetMaterial() # Get material from tag
                        doc.AddUndo(c4d.UNDOTYPE_CHANGE, tag) # Change undo
                        if mat.GetName() == replace_material.GetName(): # If the material name matches
                            tag.SetMaterial(replace_material) # Replace current_material with V-Ray material

    c4d.CallCommand(12168, 12168) # Remove unused materials


# Function - Setup Scene Vray Settings
def setupVrayEngine():
    render_data = doc.GetActiveRenderData() # Assign doc.GetActiveRenderData() -> variable render_data (for undo)
    doc.AddUndo(c4d.UNDOTYPE_CHANGE, render_data) # Change undo
    vray_engine_id = 1053272 # Vray render engine ID
    render_data[c4d.RDATA_RENDERENGINE] = vray_engine_id # Assign V-Ray render engine
    video_post = c4d.documents.BaseVideoPost(vray_engine_id) # Initializes a new base video post (pvp)
    render_data.InsertVideoPost(video_post) # Insert video post into render engine (Vray settings)


# Function - Change C4D Preferences
def changePreferences():
    vray_pref_id = 1053273 # Vray preference plugin ID
    plugin_pref = c4d.plugins.FindPlugin(vray_pref_id, c4d.PLUGINTYPE_PREFS) # Assign V-Ray to variable plugin_pref
    plugin_pref[c4d.VRAY_PREFS_MATERIAL_PREVIEW_ENABLE] = True # Set Preferences -> Renderer -> V-Ray > Materials -> Previews -> Enabled = True
    plugin_pref[c4d.VRAY_PREFS_VIEWPORT_PREVIEW_SIZE] = 10 # Set Preferences -> Renderer -> V-Ray > Materials -> Previews -> Editor Map Size -> 1024x1024


# Main function
def main():
    doc = c4d.documents.GetActiveDocument() # Get active C4D document
    materials = doc.GetMaterials() # Get all scene materials
    obj = doc.GetFirstObject() # Get first object in the document
    scene = ObjectIterator(obj) # Iterate through all objects

    doc.StartUndo() # Start recording undos

    # Convert render engine to V-Ray
    setupVrayEngine()

    # Change C4D Preferences
    # Warning: This changes your Edit -> Preferences -> Renderer -> V-Ray -> Materials settings
    #changePreferences()

    # Collect scene Polygon/Base objects
    collected_objs = [] # Empty list to collect all scene objects
    for obj in scene:
        if (obj.GetType() == 5100) or (obj.GetType() == 5159): # If obj is Polygon object or Base object (non editable)
            collected_objs.append(obj) # Append objects to collected_objs

    # Convert scene materials to V-Ray
    convertMaterials(materials, collected_objs)

    doc.EndUndo() # Stop recording undos
    c4d.EventAdd() # Refresh Cinema 4D


# Execute main()
if __name__=='__main__':
    main()
