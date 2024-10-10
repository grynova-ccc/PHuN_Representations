import get_topological_subnet_pd as tp
import os

# Specify the filename of the structure file (CIF format)
# Example .cif
filename = 'hMOF-6.cif'

# Define the folder where the generated subnet persistence diagrams will be exported
export_folder = 'subnets'

# Define the replication factor for the supercell (1,1,1 indicates no replication)
replication_factor = (1, 1, 1)

# Specify whether to wrap the periodic boudary conditions (pbc)
wrap_pbc = False

# Generate and save persistence diagrams for subnets based on different clustering  algorithms:
# The persistence diagrams will be saved as PNGs in the export folder.

tp.get_persistence_diagrams(filename, export_folder, supercell=replication_factor, wrap_pbc=wrap_pbc, view_structure=False, save_png=True)
tp.get_persistence_diagrams(filename, export_folder, 'AllNodes', supercell=replication_factor, wrap_pbc=wrap_pbc, view_structure=False, save_png=True)
tp.get_persistence_diagrams(filename, export_folder, 'SingleNodes', supercell=replication_factor, wrap_pbc=wrap_pbc, view_structure=False, save_png=True)
tp.get_persistence_diagrams(filename, export_folder, 'Standard', supercell=replication_factor, wrap_pbc=wrap_pbc, view_structure=False, save_png=True)
tp.get_persistence_diagrams(filename, export_folder, 'PE', supercell=replication_factor, wrap_pbc=wrap_pbc, view_structure=False, save_png=True)
tp.get_persistence_diagrams(filename, export_folder, 'PEM', supercell=replication_factor, wrap_pbc=wrap_pbc, view_structure=False, save_png=True)
