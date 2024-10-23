import numpy as np
import dionysus as d
import diode
import matplotlib.pyplot as plt
from ase.io import read, write
from ase import Atoms
from ase.visualize import view
import numpy as np
from ripser import Rips
import matplotlib.pyplot as plt
from persim import plot_diagrams, PersistenceImager
import os

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

# Visulize supercell coordinates using ASE viewer
def create_ase_structure(coordinates, pbc, view_structure=False):
    
    # Uses Zn atom as a "dummy" atom to visulize coordinates
    atoms = Atoms(positions=coordinates, symbols='Zn' * len(coordinates), pbc=True, cell=pbc[:3])
    
    if view_structure== True:
       view(atoms)
    return atoms


def get_persistent_diagrams_Rips(dataset, maxdim=2, coeff=2):

    rips = Rips(maxdim=maxdim, coeff=coeff)
    all_diagrams = []

    for idx, data in enumerate(dataset):
        print(f"Processing array {idx + 1}/{len(dataset)} with shape {data.shape}")
        dgms = rips.fit_transform(data)
        
        H0_dgm = dgms[0]
        H1_dgm = dgms[1]

        # In cases were H2 doesn't exist, a numpy array of zeros is created
        H2_dgm = dgms[2] if len(dgms) > 2 else np.array([[0, 0]])  
        all_diagrams.append((H0_dgm, H1_dgm, H2_dgm))
        print(f"H0: {len(H0_dgm)} points, H1: {len(H1_dgm)} points, H2: {len(H2_dgm)} points")

    return all_diagrams








