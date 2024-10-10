import numpy as np
import dionysus as d
import diode
import matplotlib.pyplot as plt
from ase.io import read, write
from ase import Atoms
from ase.visualize import view

#Extract coordinates and periodic boudary conditions (PBC) from VTF as numpy arrays
def extract_coordinates_from_VTF(filename, supercell=None, wrap_pbc=False):
    with open(filename, 'r') as file:
        lines = file.readlines()

    ordered_start = False
    coordinates = []

    pbc = None

    # Loops through lines to extract coordinates and PBC
    for line in lines:
        line = line.strip()

        if line.startswith('pbc'):
            # Extracts periodic boundary conditions (PBC)
            pbc = list(map(float, line.split()[1:]))
        
        # Extracts coordinates after keyword 'ordered'
        if line == 'ordered':
            ordered_start = True
            continue
        
        if ordered_start:
            try:
                coords = list(map(float, line.split()))
                coordinates.append(coords)
            except ValueError:
                break
    coordinates=np.array(coordinates)
    pbc=np.array(pbc)

    # Remove or wrap coordinates outside of the PBC
    if wrap_pbc == True:
        filtered_coordinates = []
        for coord in coordinates:
            if all(0 <= coord[i] < pbc[i] for i in range(3)):
                filtered_coordinates.append(coord)
        coordinates = np.array(filtered_coordinates)

    if supercell==None:
        return coordinates, pbc
    else:
        return create_supercell(coordinates, pbc, supercell), pbc


# Function to generate a supercell
def create_supercell(coordinates, pbc, replication_factors):
    
    # Unpack the PBC to get the lattice vectors
    lattice_vectors = np.array([
        [pbc[0], 0, 0],  # x-axis
        [0, pbc[1], 0],  # y-axis
        [0, 0, pbc[2]]   # z-axis
    ])

    nx, ny, nz = replication_factors

    # Create the supercell by translating the unit cell
    supercell_coords = []
    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                # Translation vector for this image
                translation = i * lattice_vectors[0] + j * lattice_vectors[1] + k * lattice_vectors[2]

                # Add the translated coordinates
                for coord in coordinates:
                    supercell_coords.append(coord + translation)
    supercell_coordinates=np.array(supercell_coords)
    #Remove any overlapping atoms                
    supercell_coordinates = np.unique(supercell_coordinates, axis=0)
    return supercell_coordinates

# Function to create an ASE Atoms object from the supercell coordinates
def create_ase_structure(coordinates, pbc, view_structure=False):
    
    # Uses Zn atom as a "dummy" atom to visulize coordinates
    atoms = Atoms(positions=coordinates, symbols='Zn' * len(coordinates), pbc=True, cell=pbc[:3])
    
    if view_structure== True:
       view(atoms)
    return atoms

#Get persistance diagrams using dionysus
def get_persistent_homology(coordinates):
 
    alpha_shape= diode.fill_alpha_shapes(coordinates,True)
    f = d.Filtration(alpha_shape)
    m = d.homology_persistence(f)
    dmg=d.init_diagrams(m, f)

    return dmg

#Converts dionysus output to an array
#Taken from moleculatda
def diagrams_to_arrays(dgms):
        
        """Convert persistence diagram objects to persistence diagram arrays."""
        dgm_dtype = np.dtype([("birth", "f4"), ("death", "f4"), ("data", "u4")])
        dgm_arrays = {
                f"dim{dim}": np.array([(np.sqrt(dgm[i].birth), np.sqrt(dgm[i].death), dgm[i].data) for i in range(len(dgm))]
                    if dgm
                    else [],
                     dtype=dgm_dtype,)
                for dim, dgm in enumerate(dgms)}
        return dgm_arrays


#Plots persistance diagrams
#Taken from moleculatda
import os

def plot_pds(dgm_1d, dgm_2d,clustering, file_basename, save_png=None):
    """Plot persistence diagrams here for visualization, example includes 1D and 2D.

    Args:
        dgm_1d, dgm_2d: 1d and 2d persistence diagrams
        save_png: The filename to save the plot (without extension). If None, plot is not saved.
    """

    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(10, 4))
    
    # Set the main title for the entire figure
    fig.suptitle(f'{clustering}_{file_basename}', fontsize=16)

    # 1D persistence diagram
    axes[0].scatter(dgm_1d["birth"], dgm_1d["death"])
    axes[0].plot([0, np.max(dgm_1d["death"])], [0, np.max(dgm_1d["death"])])
    axes[0].set_xlabel("Birth")
    axes[0].set_ylabel("Death")
    axes[0].set_title("1D persistence diagram")
    
    # 2D persistence diagram
    axes[1].scatter(dgm_2d["birth"], dgm_2d["death"])
    axes[1].plot([0, np.max(dgm_2d["death"])], [0, np.max(dgm_2d["death"])])
    axes[1].set_xlabel("Birth")
    axes[1].set_ylabel("Death")
    axes[1].set_title("2D persistence diagram")


    if save_png:
        # Check if the directory exists
        save_dir = os.path.dirname(save_png)
        if save_dir and not os.path.exists(save_dir):
            print(f"Directory {save_dir} does not exist. Creating it...")
            os.makedirs(save_dir)

        # Try saving the plot and handle errors
        try:
            plt.savefig(f'{save_png}.png')
            print(f"Saving plot to {save_png}.png")
            plt.close(fig)  # Close the figure after saving
            return f'Plot saved to {save_png}.png'
        except Exception as e:
            print(f"Error saving plot: {e}")
            return f"Failed to save plot: {e}"
    else:
        plt.show()  # Show plot if save_png is not provided
        return 'Plot displayed, not saved'

