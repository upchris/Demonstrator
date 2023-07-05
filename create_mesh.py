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

    voxelSize = 1 / 63.


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
    scale = max([x,y,z])
    mesh.apply_scale((1/scale, 1/scale, 1/scale))
    
    voxel = mesh.voxelized(voxelSize).fill()
    voxel_data = voxel.matrix
    
    ## fill voxel to have an equal grid size in all directions
    desired_shape = (int(1/voxelSize)+1, int(1/voxelSize)+1, int(1/voxelSize)+1)
    new_matrix = np.zeros(desired_shape, dtype=bool)
    original_shape = voxel_data.shape
    new_matrix[:original_shape[0], :original_shape[1], :original_shape[2]] = voxel_data


    np.save(voxelStorageFilePath, new_matrix)

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