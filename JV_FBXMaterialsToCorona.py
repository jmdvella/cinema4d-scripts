"""
JV_FBXMaterialsToCorona
Author: James Vella
Website: http://www.jamesvella.net/
Name-US: JV_FBXMaterialsToCorona
Version: 1.0.0
Written for Maxon Cinema 4D R21.207
Python version 2.7.18
Description-US: Convert FBX Standard Roughness Materials to Vray 5.0: supports:
                - Diffuse & Diffuse Color
                - Roughness
                - Metal
                - Normal Bump
                - Alpha/Opacity
                - Glass: any materials using "Transparency" will be converted to Glass - Comment out line 63-73 if not required
                
                Change/Add your own material settings in Function: newCoronaMaterial(current_material, new_corona_mat)
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


# Function - Convert current_material Materials to Corona Materials
def newCoronaMaterial(current_material, new_corona_mat):
    # Set Corona Material Settings for both Metal/Dialectric materials
    new_corona_mat[c4d.BRDFVRAYMTL_OPTION_USE_ROUGHNESS] = True # Set Reflection -> "Use Roughness"
    new_corona_mat[c4d.CORONA_PHYSICAL_MATERIAL_BASE_COLOR] = current_material[c4d.MATERIAL_COLOR_COLOR] # Copy Diffuse Color -> Corona Diffuse Color
    new_corona_mat[c4d.CORONA_MATERIAL_PREVIEWSIZE] = 10 # Material -> Editor -> Texture Preview Size -> 1024x1024

    # Copy texture + paths from current_material to Corona Materials
    try:
        # Glass - OVERRIDE materials using Transparency in material with Corona Glass Shader Settings
        if current_material[c4d.MATERIAL_USE_TRANSPARENCY] == True: # If using Transparency in material
            new_corona_mat[c4d.CORONA_PHYSICAL_MATERIAL_REFRACT] = True # Enable Refraction
            new_corona_mat[c4d.CORONA_PHYSICAL_MATERIAL_BASE_IOR_VALUE] = 1.517 # Set Fresnel -> 1.517 (Glass)
            new_corona_mat[c4d.CORONA_PHYSICAL_MATERIAL_BASE_ROUGHNESS_VALUE] = 0 # No Roughness for Glass
    except:
        pass # Skip if material not Glass

    try:
        # Diffuse
        diffuse_shader = c4d.BaseList2D(c4d.Xbitmap) # Create empty bitmap shader

        new_diffuse_path = current_material[c4d.MATERIAL_COLOR_SHADER][c4d.BITMAPSHADER_FILENAME] # Location of current_material Diffuse texture
        new_corona_mat.InsertShader(diffuse_shader) # Insert diffuse shader into Corona material
        new_corona_mat[c4d.CORONA_PHYSICAL_MATERIAL_BASE_COLOR_TEXTURE] = diffuse_shader # Set path of bitmap current_material -> bitmap path
        diffuse_shader[c4d.BITMAPSHADER_FILENAME] = new_diffuse_path # Assign texture path for bitmap to current_material -> bitmap path
    except:
        pass # Skip if some textures are not input

    try:
        # Roughness
        roughness_shader = c4d.BaseList2D(c4d.Xbitmap) # Create empty bitmap shader
        roughness_layer_id = current_material.GetReflectionLayerIndex(0) # Reflectance layer texture index location ('Specular')

        new_rough_path = current_material[roughness_layer_id.GetDataID() + c4d.REFLECTION_LAYER_MAIN_SHADER_ROUGHNESS][c4d.BITMAPSHADER_FILENAME] # current_material Reflectance Layers -> Specular -> Width / Texture remap to Corona Material -> Base Layer -> Roughness
        new_corona_mat[c4d.CORONA_PHYSICAL_MATERIAL_BASE_ROUGHNESS_TEXTURE] = roughness_shader # Assign Specular texture to Base Layer -> Roughness
        roughness_shader[c4d.BITMAPSHADER_FILENAME] = new_rough_path # Assign texture path for bitmap to current_material -> bitmap path
        new_corona_mat.InsertShader(roughness_shader) # Insert bitmap shader into Corona material
        new_corona_mat[c4d.CORONA_PHYSICAL_MATERIAL_BASE_ROUGHNESS_TEXTURE][c4d.BITMAPSHADER_COLORPROFILE] = 1 # Set Color Profile for bitmap -> linear
    except:
        pass # Skip if some textures are not input

    try:
        # Normal Bump
        if current_material[c4d.MATERIAL_BUMP_SHADER] != None: # If there is no texture in Bump skip this block
            normal_shader = c4d.BaseList2D(c4d.Xbitmap) # Create empty bitmap shader
            normal_corona_bump = c4d.BaseShader(1035405) # Create Corona Normal Texture
            new_corona_mat.InsertShader(normal_corona_bump) # Insert Corona Normal Texture into Corona Material
            new_corona_mat[c4d.CORONA_PHYSICAL_MATERIAL_BASE_BUMPMAPPING_TEXTURE] = normal_corona_bump # Assign Corona Normal Texture to Bump

            new_corona_mat[c4d.CORONA_PHYSICAL_MATERIAL_BASE_BUMPMAPPING_ENABLE] = True # Enable Bump Map
            new_bump_path = current_material[c4d.MATERIAL_BUMP_SHADER][c4d.BITMAPSHADER_FILENAME] # current_material Normal Bump texture -> Corona Material -> Base Layer -> Bump -> Normal -> texture
            new_corona_mat[c4d.CORONA_PHYSICAL_MATERIAL_BASE_BUMPMAPPING_TEXTURE][c4d.CORONA_NORMALMAP_TEXTURE] = normal_shader # Create Corona material -> Bump Map -> Normal bitmap shader
            new_corona_mat[c4d.MATERIAL_BUMP_SHADER] = normal_shader # Create empty bitmap shader
            normal_shader[c4d.BITMAPSHADER_FILENAME] = new_bump_path # Assign texture path for bitmap to current_material -> bitmap path
            new_corona_mat.InsertShader(normal_shader) # Insert bitmap shader into Corona material

    except:
        pass # Skip if some textures are not input

    try:
        # Opacity
        if current_material[c4d.MATERIAL_ALPHA_SHADER] != None: # If there is no texture in Alpha skip this block
            opacity_shader = c4d.BaseList2D(c4d.Xbitmap) # Create empty bitmap shader

            new_corona_mat[c4d.CORONA_PHYSICAL_MATERIAL_ALPHA] = True # Enable Opacity
            new_opacity_path = current_material[c4d.MATERIAL_ALPHA_SHADER][c4d.BITMAPSHADER_FILENAME] # Location of current_material Opacity texture
            new_corona_mat.InsertShader(opacity_shader) # Insert Opacity shader into Corona material
            new_corona_mat[c4d.CORONA_PHYSICAL_MATERIAL_ALPHA_TEXTURE] = opacity_shader # Set path of bitmap -> current_material -> bitmap path
            opacity_shader[c4d.BITMAPSHADER_FILENAME] = new_opacity_path # Assign texture path for bitmap to current_material -> bitmap path
            new_corona_mat[c4d.CORONA_PHYSICAL_MATERIAL_ALPHA_TEXTURE][c4d.BITMAPSHADER_COLORPROFILE] = 1 # Set Opacity texture -> Color Profile -> Linear
    except:
        pass # Skip if some textures are not input

    try:
        # Metalness
        count_layer = current_material.GetReflectionLayerCount() # Check in material if there is more than 1 Reflectance layer (default 'Specular') & Metal Materials have ('Reflection' and 'Specular')
        if count_layer > 1:
            metal_shader = c4d.BaseList2D(c4d.Xbitmap) # Create empty bitmap shader
            metal_layer_id = current_material.GetReflectionLayerIndex(1)  # current_material Metal texture index location for current_material Material ('Reflection')

            new_corona_mat[c4d.CORONA_PHYSICAL_MATERIAL_METALLIC_MODE_VALUE] = 0 # Set Corona material -> General -> Mode -> Metal
            new_metal_path = current_material[metal_layer_id.GetDataID() + c4d.REFLECTION_LAYER_COLOR_TEXTURE][c4d.BITMAPSHADER_FILENAME] # current_material Metal texture -> Corona Material -> General -> Mode -> Metal
            new_corona_mat[c4d.CORONA_PHYSICAL_MATERIAL_METALLIC_MODE_TEXTURE] = metal_shader # Set path of bitmap current_material -> bitmap path
            metal_shader[c4d.BITMAPSHADER_FILENAME] = new_metal_path # Assign texture path for bitmap to current_material -> bitmap path
            new_corona_mat.InsertShader(metal_shader) # Insert bitmap shader into Corona material
            new_corona_mat[c4d.CORONA_PHYSICAL_MATERIAL_METALLIC_MODE_TEXTURE][c4d.BITMAPSHADER_COLORPROFILE] = 1 # Set Metal texture -> Color Profile -> Linear
    except:
        pass # Skip if some textures are not input

    return new_corona_mat


# Function - Convert materials from current_material to Corona
def convertMaterials(materials, collected_objs):
    for current_material in materials:
        new_corona_mat = c4d.BaseMaterial(1056306) # Create new Corona material
        doc.InsertMaterial(new_corona_mat) # Insert Corona material into document
        doc.AddUndo(c4d.UNDOTYPE_NEW, new_corona_mat) # New undo
        new_corona_mat.SetName(current_material.GetName()) # Assign Coronamaterial name as current_material name
        replace_material = newCoronaMaterial(current_material, new_corona_mat) # Run Function to replace current material with Corona material

       # Go through Objects -> Tags -> Texture Tags -> Replace Material
        for obj in collected_objs: # Loop through object selection
                tags = obj.GetTags() # Get objects tags

                for tag in tags: # Loop through tags
                    if type(tag).__name__ == "TextureTag": # If Texture tag founded
                        mat = tag.GetMaterial() # Get material from tag
                        doc.AddUndo(c4d.UNDOTYPE_CHANGE, tag) # Change undo
                        if mat.GetName() == replace_material.GetName(): # If the material name matches
                            tag.SetMaterial(replace_material) # Replace current_material with Corona material

    c4d.CallCommand(12168, 12168) # Remove unused materials


# Function - Convert render engine to Physical
def setupCoronaEngine():
    render_data = doc.GetActiveRenderData() # Assign doc.GetActiveRenderData() to variable render_data (for undo)
    doc.AddUndo(c4d.UNDOTYPE_CHANGE, render_data) # Change undo
    corona_engine_id = 1030480 # Corona render engine ID
    render_data[c4d.RDATA_RENDERENGINE] = corona_engine_id # Assign Corona render engine
    video_post = c4d.documents.BaseVideoPost(corona_engine_id) # Initializes a new base video post (pvp)
    render_data.InsertVideoPost(video_post) # Insert video post into render engine (Corona settings)


# Main function
def main():
    doc = c4d.documents.GetActiveDocument() # Get active C4D Document
    materials = doc.GetMaterials() # Get all scene materials
    obj = doc.GetFirstObject() # Get first object in the document
    scene = ObjectIterator(obj) # Iterate through all objects
    
    doc.StartUndo() # Start recording undos

    # Convert render engine to Corona
    setupCoronaEngine()

    # Collect scene Polygon/Base objects
    collected_objs = [] # Empty list to collect all scene objects
    for obj in scene:
        if (obj.GetType() == 5100) or (obj.GetType() == 5159): # If obj is Polygon object or Base object (non editable)
            collected_objs.append(obj) # Append objects to collected_objs

    # Convert scene materials to Corona
    convertMaterials(materials, collected_objs)

    doc.EndUndo() # Stop recording undos
    c4d.EventAdd() # refresh c4d


# Execute main()
if __name__=='__main__':
    main()