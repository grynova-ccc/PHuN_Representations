# PHuN representations
This is a fun and computationally efficient Python package for computing persistent homology using nets (PHuN) representations of nanoporous materials. It enables the extraction of topological information for use as machine learning descriptors.

## Installation Guide

### Prerequisites

**PHuN** requires the [CrystalNets.jl](https://coudertlab.github.io/CrystalNets.jl/dev/python/) Julia interface, which is used to identify and extract the topological nets of crystalline structures.

### Install phun_reps using pip
```bash
pip install phun_reps
```
This package was built and tested with Python 3.10.13,
and will automatically install its dependencies:
`ase==3.26.0`, `Cython==3.2.0`, `juliacall==0.9.28`, `pandas==2.3.3`, `ripser==0.6.12` and `gudhi==3.11.0`

## Usage

**PHuN** provides tools to compute persistent homology diagrams for nanoporous materials using either:

* Atomic coordinates

* Topological nets derived from CrystalNets.jl.

It integrates with [Ripser](https://ripser.scikit-tda.org/en/latest/) and [Gudhi](https://gudhi.inria.fr/) to compute persistence diagrams and can extract topological descriptors that can be used in machine learning.

**PHuN** can be used to:

* Generate persistent diagrams/images from CIF files

* Visualize persistence diagrams/images

* Extract vectorized topological descriptors (persistent image features and persistent statistics features

For a complete example of usage, see the Example Usage section below.

## Example Usage 

### Initial setup 

```python
# Folder containing .cif files to process
folder = "test-cif"

```

### Load .cif files
```python
import phun_reps.calc_presistent_diagram as cp
# Load .cif files from the specified folder
files = cp.get_cif_files(folder)
```

### Extract point clouds for .cif

```python

import phun_reps.topology as tp

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

# Generate point cloud representation for topological net
# CrystalNets.jl is used to determine the topological net
dataset, name = extractor.get_PHuN_points(file,options=options, supercell=None, subnet_mode="full")

# The name of the topological net can also be determined
top_net = extractor.determine_topology( file, options=options)

```
The atomic coordinates of the .cif can also be used to generate a point cloud.

```python
dataset, name = extractor.get_ACPH_points(file, supercell=None)
```

### Compute persistent diagrams
```python
import phun_reps.calc_presistent_diagram as cp
# Compute persistent homology diagrams from the dataset
 diagrams = cp.calc_persistent_diagrams(
        dataset,
        file=name,
        top_net=top_net,
        maxdim=2,              # Compute H0, H1, and H2
        coeff=2,               # Z2 coefficients
        complex_type="alpha",  # Alpha complex
    )
```
The persistent diagrams can be plotted and save

```python
# Save all persistent diagrams as a pickle file
cp.save_diagrams("persistent_diagrams.pkl", diagrams_list)

# Export persistent diagram figures
cp.plot_persistent_diagrams(diagrams_list, export_folder="diagrams")
```

### Extract persistent image features from diagrams using persim
```python
import phun_reps.feature_extraction as fe
image_features_df = fe.get_persistent_image_features(
    diagrams_list,
    output_size=(30, 30),     # Persistent image resolution
    savefig=True,             # Save persistent image figures
    export_folder="test_images",
)
```
### Extract statistical features from persistent diagrams

```python
import phun_reps.feature_extraction as fe
stats_features_df = fe.get_persistent_stats_features(diagrams_list)
```

The examples folder contains a full example script along with example inputs and outputs.

