import create_presistent_diagram as cp
import get_topological_subnet_pd as tp
import feature_extraction as fe
import os
import numpy as np

folder="dataset-1000-mofs/"
directory = os.fsencode(folder)

export_folder="dataset-1000-mofs/"
replication_factor=(1,1,1)
wrap_pbc=False
clustering='SingleNodes'

files=[]
for file in os.listdir(directory):
 filename = os.fsdecode(file)
 if filename.endswith(".cif"):
  files.append(filename)

dataset=[]
for i in files:
 print(f'{folder}{i}')
 filename=f'{folder}{i}'
 coord, _ =tp.get_point_cloud(filename, export_folder, clustering=clustering, supercell=None, wrap_pbc=False, view_structure=False)
 dataset.append(coord)

print(dataset[0].shape)

diagrams = cp.get_persistent_diagrams_Rips(dataset)

image_features=fe.get_persistent_features(diagrams, files, export_folder, maxdim=2, coeff=2, pixel_size=1)
print(len(image_features), len(image_features[0]))

image_features = np.array(image_features)

np.save(f'image_features-{clustering}.npy', image_features)  
print(image_features)

