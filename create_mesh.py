import trimesh
import gmsh
import sys
import numpy as np
import trimesh
from pyvirtualdisplay import Display
from PIL import Image


def render(mesh, pngPath):
    # Create a virtual display
    display = Display(visible=0, size=(800, 600))
    display.start()

    # Load your trimesh mesh

    # Set a background color for the scene
    background_color = (255, 255, 255, 255)  # White color, adjust as needed

    # Render the mesh
    image = mesh.to_image(background=background_color)

    # Save the image as PNG
    
    image.save('path_to_save_image.png')


def create_mesh(stepStorageFilePath, stlStorageFilePath, objStorageFilePath, voxelStorageFilePath):
    print('creating mesh')
    print('for step file: ' + stepStorageFilePath)
    print('export obj file: ' + objStorageFilePath)
    print('export stl file: ' + stlStorageFilePath)
    print('export voxel file: ' + voxelStorageFilePath)



    mesh = trimesh.Trimesh(**trimesh.interfaces.gmsh.load_gmsh(stepStorageFilePath))
    
    # center mesh for files which fly around in space
    
    center_of_gravity = mesh.center_mass

    # Compute the translation vector to shift the mesh
    translation = -np.array(center_of_gravity)

    # Apply the translation to each vertex of the mesh
    mesh.vertices += translation

    mesh.export(stlStorageFilePath)
    mesh.export(objStorageFilePath)
    [x,y,z] = mesh.bounding_box_oriented.extents
    mesh.apply_scale((1/x, 1/y, 1/z))
    v = mesh.voxelized(1/63.)
    voxel_data = v.matrix
    np.save(voxelStorageFilePath, voxel_data)

    #render(mesh)
if __name__ == "__main__":
    stepStorageFilePath = sys.argv[1]
    objStorageFilePath = sys.argv[2]
    stlStorageFilePath = sys.argv[3]
    voxelStorageFilePath = sys.argv[4]

    create_mesh(stepStorageFilePath, stlStorageFilePath, objStorageFilePath, voxelStorageFilePath)

# create_mesh('uploads/2ff07e37-2850-4ef8-88fc-2a55e7ae2c0d.stp',
#             'uploads/2ff07e37-2850-4ef8-88fc-2a55e7ae2c0d.stl',
#             'uploads/2ff07e37-2850-4ef8-88fc-2a55e7ae2c0d.obj',
#             'uploads/2ff07e37-2850-4ef8-88fc-2a55e7ae2c0d.npy')