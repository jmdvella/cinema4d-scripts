"""
JV_AddSubdivisionToObjects
Author: James Vella
Website: http://www.jamesvella.net/
Name-US: JV_AddSubdivisionToObjects
Version: 1.0.0
Written for Maxon Cinema 4D R21.207
Python version 2.7.18
Description-US: Apply subdivision to all scene objects. Naming & Subdivision is the top hirearchy/Group.
"""

# Libraries
import c4d
from c4d import gui


# Main function
def main():
    doc = c4d.documents.GetActiveDocument() # Get active C4D Document
    all_objs = doc.GetObjects() # Get all objects in the scene
    
    doc.StartUndo() # Start recording undos

    for obj in all_objs:
        subd = c4d.BaseObject(1007455) # Create subdivision surface modifier
        doc.AddUndo(c4d.UNDOTYPE_CHANGE, subd) # Change undo
        subd[c4d.SDSOBJECT_SUBDIVIDE_UV] = 2002 # Set subdivision UVs to Boundary
        subd[c4d.SDSOBJECT_SUBEDITOR_CM] = 1 # Set Editor subdivision to 1
        doc.InsertObject(subd) # Insert subdivision surface modifier
        subd.SetName(obj.GetName()) # Set name for subdivision 
        doc.AddUndo(c4d.UNDOTYPE_NEW, subd) # New undo
        doc.AddUndo(c4d.UNDOTYPE_CHANGE, obj) # Change undo
        obj.InsertUnder(subd) # Parent the object to the subdivision surface modifier

    doc.EndUndo() # Stop recording undos
    c4d.EventAdd() # refresh c4d

# Execute main()
if __name__=='__main__':
    main()