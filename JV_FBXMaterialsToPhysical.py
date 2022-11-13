"""
JV_FBXMaterialsToPhysical
Author: James Vella
Website: http://www.jamesvella.net/
Name-US: JV_FBXMaterialsToPhysical
Version: 1.0.0
Written for Maxon Cinema 4D R21.207
Python version 2.7.18
Description-US: Convert FBX Standard Roughness Materials to Physical, supports:
                - Diffuse & Diffuse Color - materials without a diffuse texture will copy the diffuse color
                - Roughness - materials without a roughness texture will be set to roughness 100%
                - Metal
                - Normal Bump
                - Transmissive (Glass) note: any materials using "Transparency" will be converted to Glass. Comment out line 158-174 if not required
                - Other textures will be kept in the conversion but not color profile corrected (linear/srgb)
                
                Change/Add your own material settings in Function: convertMaterials(mat):
"""

# Libraries
import c4d


# Function - Convert FBX materials to Physical/PBR
def convertMaterials(mat):
    # General settings for material
    doc.AddUndo(c4d.UNDOTYPE_CHANGE, mat) # Start undo
    mat[c4d.MATERIAL_PREVIEWSIZE] = 10 # Material -> Editor -> Texture Preview Size -> 1024x1024

    # Copy Bump to Normal and apply settings
    if mat[c4d.MATERIAL_BUMP_SHADER] != None: # If there is no texture in bump node skip this block
        try:
            mat[c4d.MATERIAL_USE_BUMP] = 0 # Disable Bump material node
            mat[c4d.MATERIAL_USE_NORMAL] = 1 # Enable Normal material node
            mat[c4d.MATERIAL_NORMAL_SHADER] = mat[c4d.MATERIAL_BUMP_SHADER] # Copy Bump texture -> Normal node
            mat[c4d.MATERIAL_NORMAL_SHADER][c4d.BITMAPSHADER_COLORPROFILE] = 1 # Set Normal texture -> Linear Color Profile
            mat[c4d.MATERIAL_BUMP_SHADER] = None # Disable Bump material node
        except:
            pass # Skip if some textures are not input

    # If material is a 'Conductor/Metal'
    count_layer = mat.GetReflectionLayerCount() # Check if there is more than 1 Reflectance layer (default 'Specular')
    # If material is not using Transparency (Glass)
    if mat[c4d.MATERIAL_USE_TRANSPARENCY] != True:
        if count_layer > 1:
            # Create new 'Diffuse' in Reflectance Layer
            try:
                diffuse_layer = mat.AddReflectionLayer() # Add new layer to Reflectance material node
                diffuse_layer.SetName("Diffuse") # Set Reflectance layer name to "Diffuse"
                main_layer = mat.GetReflectionLayerIndex(0) # Settings for Diffuse layer

                # Set properties for Diffuse/Albedo layer
                mat[main_layer.GetDataID() + c4d.REFLECTION_LAYER_MAIN_DISTRIBUTION] = 7 # Set Type -> 'Lambertian'
                mat[main_layer.GetDataID() + c4d.REFLECTION_LAYER_MAIN_VALUE_SPECULAR] = 1 # Specular strength -> 100%
                if mat[c4d.MATERIAL_COLOR_SHADER] != None: # Check if texture exists
                    mat[main_layer.GetDataID() + c4d.REFLECTION_LAYER_COLOR_TEXTURE] = mat[c4d.MATERIAL_COLOR_SHADER] # Copies Diffuse texture -> Diffuse Reflectance layer
                mat[main_layer.GetDataID() + c4d.REFLECTION_LAYER_COLOR_COLOR] = mat[c4d.MATERIAL_COLOR_COLOR] # Diffuse Color -> Reflectance -> Diffuse -> Layer Color
                mat[c4d.MATERIAL_COLOR_SHADER] = None # Remove Color texture
                mat[c4d.MATERIAL_USE_COLOR] = 0 # Disable Color material node
            except:
                pass # Skip if some textures are not input

            # Create new 'Reflection' in Reflectance Layer (Roughness)
            try:
                roughness_layer = mat.AddReflectionLayer() # Add new layer to Reflectance material node
                roughness_layer.SetName("Reflection") # Set Reflectance layer name to "Reflection"
                main_layer = mat.GetReflectionLayerIndex(0) # Settings for Reflection layer
                specular_layer = mat.GetReflectionLayerIndex(2) # Old 'Specular' layer to copy from
                # Set properties for Reflection layer
                mat[main_layer.GetDataID() + c4d.REFLECTION_LAYER_MAIN_DISTRIBUTION] = 3 # Set type -> 'GGX'
                mat[main_layer.GetDataID() + c4d.REFLECTION_LAYER_MAIN_ADDITIVE] = 0 # Set attenuation -> 'Average'
                mat[main_layer.GetDataID() + c4d.REFLECTION_LAYER_MAIN_VALUE_REFLECTION] = 1.0 # Set reflection strength -> 100%
                mat[main_layer.GetDataID() + c4d.REFLECTION_LAYER_MAIN_VALUE_ROUGHNESS] = 1.0 # Set roughness level -> 100%
                mat[main_layer.GetDataID() + c4d.REFLECTION_LAYER_MAIN_VALUE_SPECULAR] = 1.0 # Set specular level -> 100%
                mat[main_layer.GetDataID() + c4d.REFLECTION_LAYER_FRESNEL_MODE] = 1 # Set fresnel -> dielectric
                mat[main_layer.GetDataID() + c4d.REFLECTION_LAYER_FRESNEL_VALUE_IOR] = 1.5 # Set fresnel value -> 1.5
                # Copy texture from old Specular layer -> new Roughness layer
                if mat[specular_layer.GetDataID() + c4d.REFLECTION_LAYER_MAIN_SHADER_ROUGHNESS] != None: # Check if texture exists
                    mat[main_layer.GetDataID() + c4d.REFLECTION_LAYER_MAIN_SHADER_ROUGHNESS] = mat[specular_layer.GetDataID() + c4d.REFLECTION_LAYER_MAIN_SHADER_ROUGHNESS] # Copy Specular texture -> Reflection/Roughness layer
                    mat[main_layer.GetDataID() + c4d.REFLECTION_LAYER_MAIN_SHADER_ROUGHNESS][c4d.BITMAPSHADER_COLORPROFILE] = 1 # Set Roughness texture -> Linear Color Profile
            except:
                pass # Skip if some textures are not input

            # Create new 'Metal' layer
            try:
                metal_layer = mat.AddReflectionLayer() # Add new layer to Reflectance material node
                metal_layer.SetName("Metal") # Set Reflectance layer name to "Metal"
                main_layer = mat.GetReflectionLayerIndex(0) # Settings for Metal layer
                roughness_layer_id = mat.GetReflectionLayerIndex(1) # New 'Reflection' layer in Reflectance (Roughness)
                diffuse_layer_id = mat.GetReflectionLayerIndex(2) # New 'Diffuse' layer in Reflectance
                specular_layer = mat.GetReflectionLayerIndex(3) # Old 'Specular' (Roughness) layer to copy from
                reflection_layer_id = mat.GetReflectionLayerIndex(4) # Old 'Reflection' (Metal) layer to copy from
                # Set properties for Metal layer
                mat[main_layer.GetDataID() + c4d.REFLECTION_LAYER_MAIN_DISTRIBUTION] = 3 # Set Type -> GGX
                mat[main_layer.GetDataID() + c4d.REFLECTION_LAYER_MAIN_ADDITIVE] = 4 # Set attenuation -> 'Metal'
                mat[main_layer.GetDataID() + c4d.REFLECTION_LAYER_MAIN_VALUE_REFLECTION] = 1.0 # Set reflection strength -> 100%
                mat[main_layer.GetDataID() + c4d.REFLECTION_LAYER_MAIN_VALUE_ROUGHNESS] = 1.0 # Set roughness level -> 100%
                mat[main_layer.GetDataID() + c4d.REFLECTION_LAYER_MAIN_VALUE_SPECULAR] = 1.0 # Set specular level -> 100%
                mat[main_layer.GetDataID() + c4d.REFLECTION_LAYER_FRESNEL_MODE] = 2 # Set fresnel -> 'Conductor'
                mat[main_layer.GetDataID() + c4d.REFLECTION_LAYER_FRESNEL_VALUE_ETA] = 0 # Set fresnel -> 0
                # Copy texture from old Diffuse/Specular layer to new Metal layer
                if mat[specular_layer.GetDataID() + c4d.REFLECTION_LAYER_MAIN_SHADER_ROUGHNESS] != None: # Check if texture exists
                    mat[main_layer.GetDataID() + c4d.REFLECTION_LAYER_MAIN_SHADER_ROUGHNESS] = mat[specular_layer.GetDataID() + c4d.REFLECTION_LAYER_MAIN_SHADER_ROUGHNESS] # Copy Roughness texture -> Reflection/Roughness layer
                    mat[main_layer.GetDataID() + c4d.REFLECTION_LAYER_MAIN_SHADER_ROUGHNESS][c4d.BITMAPSHADER_COLORPROFILE] = 1 # Set Roughness texture -> Linear Color Profile
                if mat[diffuse_layer_id.GetDataID() + c4d.REFLECTION_LAYER_COLOR_TEXTURE] != None: # Check if texture exists
                    mat[main_layer.GetDataID() + c4d.REFLECTION_LAYER_COLOR_TEXTURE] = mat[diffuse_layer_id.GetDataID() + c4d.REFLECTION_LAYER_COLOR_TEXTURE] # Copies diffuse texture -> Layer Color
                if mat[reflection_layer_id.GetDataID() + c4d.REFLECTION_LAYER_COLOR_TEXTURE] != None: # Check if texture exists
                    mat[main_layer.GetDataID() + c4d.REFLECTION_LAYER_TRANS_TEXTURE] = mat[reflection_layer_id.GetDataID() + c4d.REFLECTION_LAYER_COLOR_TEXTURE] # Copies metal texture -> Layer Mask
                    mat[main_layer.GetDataID() + c4d.REFLECTION_LAYER_TRANS_TEXTURE][c4d.BITMAPSHADER_COLORPROFILE] = 1 # Set Metal texture -> Linear Color Profile
                mat[main_layer.GetDataID() + c4d.REFLECTION_LAYER_COLOR_COLOR] = mat[c4d.MATERIAL_COLOR_COLOR] # Copies Diffuse Color -> Reflectance -> Metal -> Layer Color
                # Remove old Reflectance layers
                mat.RemoveReflectionLayerIndex(4) # Remove old 'Reflection' (Metal) layer
                mat.RemoveReflectionLayerIndex(3) # Remove old 'Specular' (Roughness) layer
            except:
                pass # Skip if some textures are not input

        # If material is a 'Dialectric' / not Metal
        else:
            # Create new 'Diffuse' in Reflectance Layer (Albedo)
            try:
                #if mat[c4d.MATERIAL_COLOR_SHADER] != None: # If there is a Diffuse texture
                diffuse_layer = mat.AddReflectionLayer() # Add new layer to Reflectance material node
                diffuse_layer.SetName("Diffuse") # Set Reflectance layer name to "Diffuse"
                main_layer = mat.GetReflectionLayerIndex(0) # Settings for Diffuse layer
                # Set properties for Diffuse/Albedo layer
                mat[main_layer.GetDataID() + c4d.REFLECTION_LAYER_MAIN_DISTRIBUTION] = 7 # Set Type -> 'Lambertian'
                mat[main_layer.GetDataID() + c4d.REFLECTION_LAYER_MAIN_VALUE_SPECULAR] = 1 # Specular strength -> 100%
                if mat[c4d.MATERIAL_COLOR_SHADER] != None: # Check if texture exists
                    mat[main_layer.GetDataID() + c4d.REFLECTION_LAYER_COLOR_TEXTURE] = mat[c4d.MATERIAL_COLOR_SHADER] # Copies Diffuse texture -> Diffuse Reflectance layer
                mat[c4d.MATERIAL_COLOR_SHADER] = None # Remove Color texture from Color material node
                mat[c4d.MATERIAL_USE_COLOR] = 0 # Disable Color material node
            except:
                pass # Skip if some textures are not input

            # Create new 'Reflection' in Reflectance Layer (Roughness)
            try:
                roughness_layer = mat.AddReflectionLayer() # Add new layer to Reflectance material node
                roughness_layer.SetName("Reflection") # Set Reflectance layer name to "Reflection"
                main_layer = mat.GetReflectionLayerIndex(0) # Settings for Reflection layer
                specular_layer = mat.GetReflectionLayerIndex(2) # Old Specular layer to copy from
                # Set properties for Reflection layer
                mat[main_layer.GetDataID() + c4d.REFLECTION_LAYER_MAIN_DISTRIBUTION] = 3 # Set Type -> 'GGX'
                mat[main_layer.GetDataID() + c4d.REFLECTION_LAYER_MAIN_ADDITIVE] = 0 # Set attenuation -> 'Average'
                mat[main_layer.GetDataID() + c4d.REFLECTION_LAYER_MAIN_VALUE_REFLECTION] = 1.0 # Set reflection strength -> 100%
                mat[main_layer.GetDataID() + c4d.REFLECTION_LAYER_MAIN_VALUE_ROUGHNESS] = 1.0 # Set roughness level -> 100%
                mat[main_layer.GetDataID() + c4d.REFLECTION_LAYER_MAIN_VALUE_SPECULAR] = 1.0 # Set specular level -> 100%
                mat[main_layer.GetDataID() + c4d.REFLECTION_LAYER_FRESNEL_MODE] = 1 # Set fresnel -> dielectric
                mat[main_layer.GetDataID() + c4d.REFLECTION_LAYER_FRESNEL_VALUE_IOR] = 1.5 # Set fresnel value -> 1.5
                # Copy texture from old Specular layer to new Roughness layer
                if mat[specular_layer.GetDataID() + c4d.REFLECTION_LAYER_MAIN_SHADER_ROUGHNESS] != None: # Check if texture exists
                    mat[main_layer.GetDataID() + c4d.REFLECTION_LAYER_MAIN_SHADER_ROUGHNESS] = mat[specular_layer.GetDataID() + c4d.REFLECTION_LAYER_MAIN_SHADER_ROUGHNESS] # Copy Roughness texture -> Reflection/Roughness layer
                    mat[main_layer.GetDataID() + c4d.REFLECTION_LAYER_MAIN_SHADER_ROUGHNESS][c4d.BITMAPSHADER_COLORPROFILE] = 1 # Set Roughness texture -> Linear Color Profile
                # Remove old Reflectance layers
                mat.RemoveReflectionLayerIndex(2) # Remove old 'Specular' (Roughness)
            except:
                pass # Skip if some textures are not input


    else: # If material is using Transparency (Glass)
        try:
            mat[c4d.MATERIAL_TRANSPARENCY_BRIGHTNESS] = 1 # Set Transparency -> Brightness -> 100%
            mat[c4d.MATERIAL_TRANSPARENCY_REFRACTION_PRESET] = 5 # Set Transparency -> Refraction Preset -> Glass
            mat[c4d.MATERIAL_TRANSPARENCY_REFRACTION] = 1.517 # Set Fresnel -> 1.517 (Glass)
            mat[c4d.MATERIAL_TRANSPARENCY_COLOR] = c4d.Vector(1,1,1) # Set Transparency color -> White
            transparency_layer = mat.GetReflectionLayerTrans() # Select *Transparency* layer from Reflectance
            mat[transparency_layer.GetDataID() + c4d.REFLECTION_LAYER_MAIN_DISTRIBUTION] = 3 # Set Transparency type -> GGX
            mat[transparency_layer.GetDataID() + c4d.REFLECTION_LAYER_MAIN_VALUE_ROUGHNESS] = 0 # Set Transparency Roughness -> 0%
            mat[c4d.MATERIAL_COLOR_SHADER] = None # Remove Color texture from Color material node
            mat[c4d.MATERIAL_USE_COLOR] = 0 # Disable Color material node
            mat.RemoveReflectionAllLayers() # Remove all Reflectance layers
            mat[c4d.MATERIAL_USE_REFLECTION] = False # Disable Reflectance material node
        except:
            pass # Skip if material not using Translucency


# Function - Convert render engine to Physical
def setupPhysicalEngine():
    try:
        render_data = doc.GetActiveRenderData() # Assign doc.GetActiveRenderData() -> variable render_data (for undo)
        doc.AddUndo(c4d.UNDOTYPE_CHANGE, render_data) # Start undo
        physical_engine_id = 1023342 # Physical render engine ID
        render_data[c4d.RDATA_RENDERENGINE] = physical_engine_id # Assign Physical render engine
        video_post = c4d.documents.BaseVideoPost(physical_engine_id) # Initializes a new base video post (pvp)
        render_data.InsertVideoPost(video_post) # Insert video post into render engine (Physical settings)
    except:
        pass # Skip if cannot detect Physical Render Engine


# Function - Main
def main():
    doc = c4d.documents.GetActiveDocument() # Get active C4D Document
    materials = doc.GetMaterials() # Get all scene materials
    doc.StartUndo() # Start recording undos

    # Convert render engine to Physical
    setupPhysicalEngine()

    # Convert scene materials to Physical
    for mat in materials:
        convertMaterials(mat)

    doc.EndUndo() # Stop recording undos
    c4d.EventAdd() # Refresh c4d

if __name__=='__main__':
    main()