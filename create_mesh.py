import trimesh
import gmsh
import sys
import numpy as np

def create_mesh(stepStorageFilePath, stlStorageFilePath, objStorageFilePath, voxelStorageFilePath):
    print('creating mesh')
    print('for step file: ' + stepStorageFilePath)
    print('export obj file: ' + objStorageFilePath)
    print('export stl file: ' + stlStorageFilePath)
    print('export voxel file: ' + voxelStorageFilePath)



    mesh = trimesh.Trimesh(**trimesh.interfaces.gmsh.load_gmsh(stepStorageFilePath))
    mesh.export(stlStorageFilePath)
    mesh.export(objStorageFilePath)
    [x,y,z] = mesh.bounding_box_oriented.extents
    mesh.apply_scale((1/x, 1/y, 1/z))
    v = mesh.voxelized(1/63.)
    voxel_data = v.matrix
    np.save(voxelStorageFilePath, voxel_data)

    print(v)
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