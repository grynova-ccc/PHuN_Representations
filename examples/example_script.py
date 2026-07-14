import os
import pickle
import phun_reps.calc_persistent_diagram as cp
import phun_reps.feature_extraction as fe
import phun_reps.topology as tp

# LOAD INPUT FILES

# Folder containing .cif crystal structure files to process
folder = "test-cif"

files = cp.get_cif_files(folder)

# Initate point cloud extraction. This class handles the conversion of .cif files to point clouds and topological net identification. 
# This is used to generate the point cloud representations for persistent homology and to determine the topological net labels for each structure.

extractor = tp.PointCloudExtractor()

# Build CrystalNets.jl topology analysis options
options = extractor.build_options(
    structure="MOF",              # Structure type
    clusterings=["SingleNodes"],  # Clustering strategy
    export_input=False,           # Do not export CrystalNets input
    export_net=False,             # Do not export identified net files
    export_subnets=False,         # Do not export subnet files
    detect_organiccycles=True     # Detect organic cycles/rings
)

# Lists for storing persistent diagrams
diagrams_list = []
for file in files:

    # Generate point cloud representation used for persistent homology

    dataset, name = extractor.get_PHuN_points(file,options=options, supercell=None, subnet_mode="full")

    # Determine topological net
    top_net = extractor.determine_topology( file, options=options)

    # Calculate persistent homology diagrams
    diagrams = cp.calc_persistent_diagrams(
        dataset,
        file=name,
        top_net=top_net,
        maxdim=2,              # Compute D0, D1, and D2
        coeff=2,               # Z2 coefficients
        complex_type="alpha",  # Alpha complex
    )

    # Store diagrams for later processing
    diagrams_list.append(diagrams)

# Save all persistent diagrams as a pickle file
cp.save_diagrams("persistent_diagrams.pkl", diagrams_list)

# Export persistent diagram figures
cp.plot_persistent_diagrams(diagrams_list, export_folder="diagrams")

# Extract filenames associated with each diagram
filenames = [d["filename"] for d in diagrams_list]

# Extract topological net labels
nets = [d.get("net") for d in diagrams_list]

# Compute persistent image representations and flatten into features
image_features_df = fe.get_persistent_image_features(
    diagrams_list,
    output_size=(30, 30),     # Persistent image resolution
    savefig=True,             # Save persistent image figures
    export_folder="test_images",
)

# Add column with filenames to image features dataframe
image_features_df["Name"] = filenames

# Add topology labels if available
if any(net is not None for net in nets):
    image_features_df["Topological Net"] = nets

# Export persistent image feature table
image_features_df.to_csv("image_features.csv",index=False)

print("Saved image features to image_features.csv")

# Compute statistical descriptors from persistence diagrams
stats_features_df = fe.get_persistent_stats_features(diagrams_list)

# Add column with filenames to statistical features dataframe
stats_features_df["Name"] = filenames

# Add topology labels if available
if any(net is not None for net in nets):
    stats_features_df["Topological Net"] = nets

# Export statistical feature table
stats_features_df.to_csv( "stats_features.csv", index=False)

print("Saved statistical features to stats_features.csv")