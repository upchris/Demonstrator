import numpy as np
import trimesh

tri=np.load('testfile/100_100_trimesh_neu.npy')

binv=np.load('testfile/100_100_binvox.npy')

print('bla')


import numpy as np
import matplotlib.pyplot as plt

#plt.imshow(bin[:,10], cmap='binary', aspect='auto')


# stepStorageFilePath='100_100.stp'
# mesh = trimesh.Trimesh(**trimesh.interfaces.gmsh.load_gmsh(stepStorageFilePath))

# center_of_gravity = mesh.center_mass

# # Compute the translation vector to shift the mesh
# translation = -np.array(center_of_gravity)

# # Apply the translation to each vertex of the mesh
# mesh.vertices += translation

# [x,y,z] = mesh.bounding_box_oriented.extents
# scale = max([x,y,z])
# mesh.apply_scale((1/scale, 1/scale, 1/scale))


# v = mesh.voxelized(1/63.)
# x=v.matrix


# desired_shape = (64, 64, 64)
# new_matrix = np.zeros(desired_shape, dtype=bool)
# original_shape = x.shape




# new_matrix[:original_shape[0], :original_shape[1], :original_shape[2]] = x
plt.imshow(tri[:,1], cmap='binary', aspect='auto')
plt.imshow(binv[:,1], cmap='binary', aspect='auto')
