import create_presistent_diagram as cp
import numpy as np
from ase.visualize import view
import juliacall
import os

jl = juliacall.newmodule("TopologyforMOFs") # put whatever name here
jl.seval("using CrystalNets")

def get_persistence_diagrams(filename, export_folder, clustering='input', supercell=None, wrap_pbc=False, view_structure=False, save_png=False):
    
    # Validate inputs
    if not os.path.isfile(filename):
        raise FileNotFoundError(f"File '{filename}' not found.")
    if not os.path.isdir(export_folder):
        os.makedirs(export_folder)
    
    # Construct vtf file path
    file_basename = os.path.basename(filename)[:-4]  

    clustering_options = {
        'SingleNodes': jl.Clustering.SingleNodes,
        'Standard': jl.Clustering.Standard,
        'AllNodes': jl.Clustering.AllNodes,
        'PE': jl.Clustering.PE,
        'PEM': jl.Clustering.PEM
    }

    if clustering=='input':
         
        options = jl.CrystalNets.Options(
        structure=jl.StructureType.MOF,
        export_input=export_folder,
        export_subnets=False)
    
        # Determine topology
        jl.determine_topology(filename, options)

        # Construct vtf file path
        file_basename = os.path.basename(filename)[:-4] 
        vtf_file = f"{export_folder}/{export_folder}/{clustering}_{file_basename}.vtf"

    elif clustering not in clustering_options:
        raise ValueError(
            "Invalid clustering option. Available options are: "
            "'SingleNodes', 'AllNodes', 'Standard', 'PE', 'PEM'."
        )
    else:
        # Set clustering option

        options = jl.CrystalNets.Options(
            structure=jl.StructureType.MOF,
            clusterings=[clustering_options[clustering]],
            export_input=False,
            export_subnets=export_folder
            )
    
         # Determine topology
        jl.determine_topology(filename, options)
        vtf_file = f"{export_folder}/{export_folder}/subnet_{clustering}_{file_basename}_1.vtf"

    
    
    
    # Extract coordinates and periodic boundary conditions (PBC)
    coordinates, pbc = cp.extract_coordinates_from_VTF(vtf_file, supercell, wrap_pbc)
    
    # Create ASE structure
    atoms = cp.create_ase_structure(coordinates, pbc, view_structure)
    
    # Generate persistence homology
    dmg = cp.get_persistent_homology(coordinates)
    
    # Convert diagrams to arrays
    arr_dgms = cp.diagrams_to_arrays(dmg)
    
    # Extract 1D and 2D diagrams
    dgm_1d = arr_dgms.get('dim1', [])
    dgm_2d = arr_dgms.get('dim2', [])
    
    # Prepare the output file path for the diagram
    if save_png==True:
        fig_path = f"{export_folder}/{clustering}_{file_basename}"
        # Plot persistence diagrams and save to file
        return cp.plot_pds(dgm_1d, dgm_2d, clustering, file_basename, save_png=fig_path)
    else:
        return cp.plot_pds(dgm_1d, dgm_2d, clustering, file_basename)
