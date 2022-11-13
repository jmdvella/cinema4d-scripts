"""
JV_ResetAxisFrom3dsmax
Author: James Vella
Website: http://www.jamesvella.net/
Name-US: JV_ResetAxisFrom3dsmax
Version: 1.0.0
Written for Maxon Cinema 4D R21.207
Python version 2.7.18
Description-US: Flip Z/Y Axis for Nulls, Nested Nulls and Polygon objects.
"""

import c4d
import math
from c4d import gui
from c4d import GeListNode

# Function - Flip Y/Z axis
def resetAxisFrom3dsmax(obj):
    original_pos = obj.GetMg() # Get objects global matrix
    points = obj.GetAllPoints() # Find all points/vertex of the object
    transform = c4d.utils.MatrixRotX(math.pi * 1.5) # Rotate 90 degrees
    default_matrix = c4d.Matrix() # Default matrix
    
    doc.AddUndo(c4d.UNDOTYPE_CHANGE, obj) # Undo for obj
    obj.SetMg(default_matrix) # Move object to 0,0,0 default co-ordinates
    obj.SetAllPoints([p * transform for p in points]) # Apply new transform to the object points (rotate 90 degrees)
    obj.Message(c4d.MSG_UPDATE) # Refresh changes to object points
    obj.SetMg(original_pos) # Move object back to where it was


# Function - Flip Y/Z axis for Null Parent
def resetNullAxis(null_parent):
    orig_null_parent_matrix = null_parent.GetMg() # Copy current matrix for parent_null to new variable
    transform = c4d.utils.MatrixRotX(math.pi * 1.5) # Rotate 90 degrees

    # Find nested nulls, if found do recurssion of this Function -> resetNullAxis(null_parent)
    null_children = GeListNode.GetChildren(null_parent)
    if null_children != []: # If child is not empty null
        for obj in null_children:
            if obj.GetType() == 5140: # If child is another null
                parent_matrix = obj.GetMg() # Get current null matrix
                resetNullAxis(obj) # Recurssion: Find the nested null with Polygon children
                obj.SetMg(orig_null_parent_matrix * parent_matrix) # Move null back to where it was
            else:
                # If child is Polygon object
                doc.AddUndo(c4d.UNDOTYPE_DELETE, obj) # Undo
                GeListNode.Remove(obj) # Remove objects from null_parent
                resetAxisFrom3dsmax(obj) # run Function to flip axis z/y of object
                doc.InsertObject(obj) # Add objects back into the document without parent
                doc.AddUndo(c4d.UNDOTYPE_NEW, obj) # Undo
                doc.AddUndo(c4d.UNDOTYPE_CHANGE, obj) # Undo
                obj.InsertUnder(null_parent) # Add object back to parent_null
                obj.SetMg(orig_null_parent_matrix * obj.GetMg()) # Set matrix of object to matrix of parent_null

    # Rotate null to 0,0,0 and add children back to the null
    for obj in null_children:
        original_offset = obj.GetMg() # Get objects current matrix
        old_rotation = obj.GetRelRot() # Find rotation from original HPB
        new_rotation = c4d.Vector(-(old_rotation[2]),0,0) # Copy/invert B to H (flip from z axis to y)

        doc.AddUndo(c4d.UNDOTYPE_DELETE, obj) # Undo
        GeListNode.Remove(obj) # Remove objects from null_parent
        doc.AddUndo(c4d.UNDOTYPE_CHANGE, null_parent) # Undo
        null_parent.SetRelRot(c4d.Vector(0,0,0)) # Reset rotation for null

        original_offset.off = obj.GetMg().off - orig_null_parent_matrix.off # Reset offset position to where it was before removing from parent_null
        doc.AddUndo(c4d.UNDOTYPE_CHANGE, obj) # Undo
        obj.SetMg(original_offset) # Assign offset position to object
        obj.SetRelRot(new_rotation) # Apply new rotation from local rotation

        doc.InsertObject(obj) # Insert object back into document
        doc.AddUndo(c4d.UNDOTYPE_NEW, obj) # Undo
        doc.AddUndo(c4d.UNDOTYPE_CHANGE, obj) # Undo
        obj.InsertUnder(null_parent) # Add object back to parent_null
        obj.SetRelRot(new_rotation) # Apply new rotation from local


def main():
    doc = c4d.documents.GetActiveDocument() # Get active C4D document
    doc.StartUndo() # Start recording undos
    all_objs = doc.GetObjects() # Get all scene objects

    # Flip Y/Z axis for objects without Parents/Null
    try:
        for obj in all_objs:
            if obj.GetType() == 5100: # If the object is a PolygonObject
                old_rotation = obj.GetRelRot() # Find rotation from original HPB
                new_rotation = c4d.Vector(-(old_rotation[2]),0,0) # Copy/invert B to H (flip from z axis to y)
                resetAxisFrom3dsmax(obj)
                doc.AddUndo(c4d.UNDOTYPE_CHANGE, obj) # Undo for object changes
                obj.SetRelRot(new_rotation) # Apply new rotation from local rotation
    
            # Flip Y/Z axis for objects with Parents/Null
            if obj.GetType() == 5140: # If item in null/parent object
                resetNullAxis(obj)
            else:
                pass # Skip if object is not Polygon or Null
    except:
        pass # Skip if there is an error

    doc.EndUndo() # Stop recording undos
    c4d.EventAdd() # Refresh Cinema 4D


# Execute main()
if __name__=='__main__':
    main()