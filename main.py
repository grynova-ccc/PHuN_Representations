import rep_codes.create_presistent_diagram as cp
import rep_codes.get_topological_subnet_pd as tp
import rep_codes.feature_extraction as fe
import os
import numpy as np
import pickle

folder="methane-storage-dataset/"
directory = os.fsencode(folder)

export_folder="methane-storage-dataset"

replication_factor=(1,1,1)
wrap_pbc=False
clustering='input'

files=[]
for file in os.listdir(directory):
 filename = os.fsdecode(file)
 if filename.endswith(".cif"):
  files.append(filename)

dataset=[]
for i in files:
 print(f'{folder}{i}')
 filename=f'{folder}{i}'
 coord, _ = tp.get_point_cloud(filename, export_folder, clustering=clustering, supercell=None, wrap_pbc=False, view_structure=False)
 dataset.append(coord)
 
diagrams = cp.get_persistent_diagrams_Rips(dataset, maxdim=2, coeff=2, checkpoint_path="checkpoint.pkl", resume=True, num_workers=4, batch_size=10)

#with open(f'diagrams_{export_folder[:-1]}_{clustering}.pkl', "wb") as file:
 #   pickle.dump(diagrams, file)

#with open(f'checkpoint.pkl', "rb") as file:
 #   checkpoint = pickle.load(file)
 #   diagrams = checkpoint["all_diagrams"]


#print(len(diagrams))

print(f'Saved persistent diagrams to diagrams_{export_folder[:-1]}_{clustering}.pkl')

# Get persistent images features
image_features=fe.get_persistent_image_features(diagrams, files, export_folder, maxdim=2, coeff=2, pixel_size=0.8, savefig=False)
image_features = np.array(image_features)
np.save(f'image_features-{export_folder[:-1]}_{clustering}.npy', image_features)  
print(f'Saved image features to image_features-{export_folder[:-1]}_{clustering}.npy')

# Get persistent entropy features
entropy_features=entropy_features=fe.get_persistent_entropy_features(diagrams)
np.save(f'entropy_features-{export_folder[:-1]}_{clustering}.npy', entropy_features) 
print(f'Saved entropy features to entropy_features-{export_folder[:-1]}_{clustering}.npy')

# Get persistent statistc features
stats_features=fe.extract_features_from_all_diagrams(diagrams)
stats_features.to_pickle(f'stats_features-{export_folder[:-1]}_{clustering}.pkl')

print(f'Saved statistical features to stats_features-{export_folder[:-1]}_{clustering}.pkl')

