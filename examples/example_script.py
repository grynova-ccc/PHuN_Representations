import phun_reps.calc_presistent_diagram as cp
import phun_reps.feature_extraction as fe
import pandas as pd

# Folder containing .cif files to process
folder = "test-cif"

# Folder where CrystalNets.jl outputs will be saved
# Default folder is /tmp
export_folder = "/tmp"

# Clustering option for CrystalNets.jl
# Determines how topological nets are identified. Default is 'SingleNodes'
clustering = 'SingleNodes'

# Load .cif files from the specified folder
files = cp.get_cif_files(folder)

# Build dataset:
# - Uses CrystalNets.jl to identify topological nets based on clustering option. If ACPH features are wanted, set clustering to 'input'
# - Extracts point cloud coordinates from CrystalNets output
# Returns:
# - dataset: point cloud data for each CIF
# - top_nets: identified topological nets
# - names: file names corresponding to each dataset entry
dataset, top_nets, names = cp.build_dataset(files, export_folder, clustering)

# Compute persistent homology diagrams from the dataset
# - maxdim=2: compute up to 2-dimensional features
# - coeff=2: field coefficient for homology computations
# - save_file: optional pickle file to store computed diagrams
diagrams_tuples = cp.get_persistent_diagrams(
    dataset, names, top_nets,
    maxdim=2, coeff=2,
    save_file=f"diagrams_{folder}_{clustering}.pkl"
)

# Plots persistent diagrams and save plots to folder "test_images"
cp.plot_persistent_diagrams(diagrams_tuples, "test_images")

# Extract persistent image features from diagrams using persim
# - output_image_size: size of the images
# - savefig, if True: save generated images. Default is False
# - export_folder: folder to save images. Default is None
# Returns:
# - Dataframe of persistent image features for 1d and 2d persistent diagrams
# - If savefig=True, persistent images are saved to export_folder

image_features_df = fe.get_persistent_image_features(
    diagrams_tuples,
    output_image_size=(30, 30),
    savefig=True,
    export_folder="test_images"
)

# Save persistent image features to CSV
image_features_df.to_csv(f'image_features_{folder}_{clustering}.csv', index=False)
print(f'Saved image features to image_features_{folder}_{clustering}.csv')

# Extract statistical features from persistent diagrams
# - Calculates the following persistent statsitics features:
#   maximum persistence, minimum persistence, mean persistence, variance, and total number of points for 0d, 1d, and 2d persistence diagrams
stats_features_df = fe.get_persistent_stats_features(diagrams_tuples)

# Save persistent statistics features to CSV
stats_features_df.to_csv(f'stats_features_{folder}_{clustering}.csv', index=False)
print(f'Saved statistical features to stats_features_{folder}_{clustering}.csv')
