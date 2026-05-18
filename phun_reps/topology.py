import numpy as np
from pathlib import Path
from ase import Atoms
from ase.io import read
import juliacall


def cubic_cutout_from_atoms(positions, cell, size, min_size=-5.0, margin=2):
    """
    Generate a cubic cutout of periodically repeated atomic positions.

    This function tiles a periodic structure in all directions and extracts
    only the atoms that fall inside a cubic region defined by:
        [min_size, size] in x, y, and z.

    Parameters
    ----------
    positions : np.ndarray
        Atomic Cartesian coordinates with shape (N, 3).

    cell : np.ndarray
        3x3 lattice matrix describing the unit cell vectors.

    size : float
        Upper bound of the cubic region.

    min_size : float, optional
        Lower bound of the cubic region.
        Default is -5.0.

    margin : int, optional
        Extra number of unit-cell repetitions added in each direction
        to ensure the cube is fully covered.
        Default is 2.

    Returns
    -------
    np.ndarray
        Cartesian coordinates inside the cubic cutout,
        wrapped back into the range [0, size].
    """

    span = float(size) - float(min_size)

    if span <= 0:
        raise ValueError("`size` must be greater than `min_size`.")

    lengths = np.linalg.norm(cell, axis=1)

    reps = [int(np.ceil(span / L)) + margin for L in lengths]
    nx, ny, nz = reps

    shifts = np.array(
        [(i, j, k)
         for i in range(-nx, nx + 1)
         for j in range(-ny, ny + 1)
         for k in range(-nz, nz + 1)],
        dtype=float
    )

    shift_cart = shifts @ cell

    tiled_positions = (
        positions[:, None, :] + shift_cart[None, :, :]
    ).reshape(-1, 3)

    mask = np.all(
        (tiled_positions >= min_size) &
        (tiled_positions <= size),
        axis=1
    )

    cut_positions = tiled_positions[mask]

    cut_positions -= np.floor(cut_positions / float(size)) * float(size)

    return cut_positions


class PointCloudExtractor:
    """
    Extract point-cloud representations and topological information
    from crystal structures using CrystalNets.jl.

    This class provides:
    - Julia environment initialization
    - CrystalNets configuration handling
    - Point extraction for ACPH and PHuN workflows
    - Topology determination
    - Supercell/cutout generation
    """

    def __init__(self):
        """
        Initialize the Julia runtime and CrystalNets environment.
        """

        # Create isolated Julia module namespace
        self.jl = juliacall.newmodule("TopologyforMOFs")

        # Initialize Julia dependencies
        self._init_julia()

        # Load custom Julia helper functions
        self._load_helper_script()

        # Cache commonly used CrystalNets constants
        self._init_constants()

    def _init_julia(self):
        """
        Configure the Julia environment and import required packages.
        """

        # Activate a preconfigured Julia environment
        self.jl.seval("""
                import Pkg
                Pkg.activate("/rds/projects/k/kirkvocm-topological-reps/julia_cache/environments/v1.10")
                import PeriodicGraphs
                """)

        # Load CrystalNets and related packages
        self.jl.seval("using CrystalNets")
        self.jl.seval("import PeriodicGraphs")
        self.jl.seval("import PeriodicGraphEmbeddings")

        # Disable CrystalNets warnings and export messages
        self.jl.seval("CrystalNets.toggle_warning(false)")
        self.jl.seval("CrystalNets.toggle_export(false)")

    def _load_helper_script(self):
        """
        Load supplementary Julia utilities from a local script.
        """

        # Locate helper script in same directory as this Python file
        helper_path = Path(__file__).with_name("crystalnet_utilities.jl")

        # Include helper functions into Julia session
        self.jl.include(str(helper_path))

    def _init_constants(self):
        """
        Cache commonly used CrystalNets enum-like constants.
        """

        # Available structure types
        self.structure_types = {
            name: self.jl.seval(f"CrystalNets.StructureType.{name}")
            for name in ["MOF", "Zeolite"]
        }

        # Available clustering strategies
        self.clustering_options = {
            name: self.jl.seval(f"CrystalNets.Clustering.{name}")
            for name in ["SingleNodes", "Standard", "AllNodes", "PE", "PEM", "Auto"]
        }

    def build_options(self, **kwargs):
        """
        Build a CrystalNets.Options object from Python-friendly arguments.

        String representations for:
        - structure
        - clusterings

        are automatically converted into CrystalNets constants.

        Parameters
        ----------
        **kwargs
            Keyword arguments passed to CrystalNets.Options.

        Returns
        -------
        CrystalNets.Options
            Configured CrystalNets options object.
        """

        kwargs = dict(kwargs)

        # Convert structure string into CrystalNets enum
        if "structure" in kwargs and isinstance(kwargs["structure"], str):
            kwargs["structure"] = self.structure_types[kwargs["structure"]]

        # Normalize clustering argument into list format
        if "clusterings" in kwargs:
            clusterings = kwargs["clusterings"]

            if not isinstance(clusterings, (list, tuple)):
                clusterings = [clusterings]

            # Convert string clusterings into CrystalNets enums
            kwargs["clusterings"] = [ self.clustering_options[c] if isinstance(c, str) else c for c in clusterings]

        return self.jl.CrystalNets.Options(**kwargs)

    def get_ACPH_points(self, filename, supercell=None):
        """
        Extract atomic coordinates from a CIF file for ACPH processing.

        Parameters
        ----------
        filename : str
            Path to CIF structure file.

        supercell : float or None, optional
            If provided, generate a cubic periodic cutout.

        Returns
        -------
        tuple
            (coordinates, file_basename)
        """
        file_basename = Path(filename).stem
        atoms = read(filename)
        coords = np.asarray(atoms.get_positions(), dtype=float)
        cell = np.asarray(atoms.get_cell().array, dtype=float)

        # Optionally generate supercell cutout
        if supercell is not None:
            coords = self._apply_supercell(coords, cell, supercell)

        return coords, file_basename

    def get_PHuN_points(self, filename, options, supercell=None, subnet_mode="first"):
        """
        Extract topology-derived node coordinates using CrystalNets.

        Parameters
        ----------
        filename : str
            Path to CIF structure file.

        options : CrystalNets.Options
            CrystalNets configuration object.

        supercell : float or None, optional
            If provided, generate periodic cubic cutouts.

        subnet_mode : str, optional
            Controls handling of subnetworks:
            - "first"    : use only first subnet
            - "full"     : merge all subnet coordinates
            - "separate" : return each subnet independently

        Returns
        -------
        tuple
            (coordinates, file_basename)
        """

        file_basename = Path(filename).stem

        # Retrieve subnet coordinates and unit cells from Julia
        coords_list, cell_list = self.jl.get_net_coords(filename, options)

        # Convert Julia arrays into NumPy arrays
        coords_list = [np.asarray(c, dtype=float) for c in coords_list]
        cell_list = [np.asarray(c, dtype=float) for c in cell_list]

        # Select how subnetworks should be handled
        if subnet_mode == "first":
            coords = coords_list[0]
            cell = cell_list[0]

        elif subnet_mode == "full":
            coords = np.vstack(coords_list)
            cell = cell_list[0]

        elif subnet_mode == "separate":
            coords = coords_list
            cell = cell_list

        else:
            raise ValueError(
                "subnet_mode must be 'first', 'full', or 'separate'"
            )

        # Apply periodic supercell expansion if requested
        if supercell is not None:

            if subnet_mode == "separate":
                coords = [
                    self._apply_supercell(c, cell_list[i], supercell)
                    for i, c in enumerate(coords_list)
                ]
            else:
                coords = self._apply_supercell(coords, cell, supercell)

        return coords, file_basename

    def determine_topology(self, filename, options):
        """
        Determine the topology name for a structure.

        Parameters
        ----------
        filename : str
            Path to CIF structure file.

        options : CrystalNets.Options
            CrystalNets configuration object.

        Returns
        -------
        str or None
            Simplified topology name.
        """

        topo = self.jl.determine_topology(filename, options)

        return self._simplify_topology_name(topo)

    @staticmethod
    def _extract_net_name(topo):
        """
        Extract topology name from CrystalNets output string.
        """

        topo_str = str(topo)

        return topo_str.split(": ", 1)[1] if ": " in topo_str else topo_str

    @staticmethod
    def _simplify_topology_name(topo):
        """
        Simplify multiline topology output into a compact identifier.

        Examples
        --------
        Single topology:
            'pcu'

        Multiple distinct topologies:
            'pcu+dia'
        """

        if topo is None:
            return None

        topo_str = str(topo).strip()

        lines = [
            line.strip()
            for line in topo_str.splitlines()
            if ": " in line
        ]

        if not lines:
            return topo_str
        
        names = [line.split(": ", 1)[1].strip() for line in lines]


        unique_names = list(dict.fromkeys(names))

        if len(unique_names) == 1:
            return unique_names[0]

        return "+".join(unique_names)

    def _apply_supercell(self, coords, cell, supercell):
        """
        Generate a cubic periodic cutout from a set of coordinates. This is similar to how MolecularTDA generates supercells

        Parameters
        ----------
        coords : np.ndarray
            Cartesian coordinates.

        cell : np.ndarray
            Unit cell matrix.

        supercell : float
            Size of cubic cutout.

        Returns
        -------
        np.ndarray
            Coordinates inside periodic cubic region.
        """

        atoms = Atoms(
            positions=coords,
            symbols=["Zn"] * len(coords),
            cell=cell,
            pbc=True,
        )

        bounds = atoms.cell.array

        mins = bounds.min(axis=0)
        maxs = bounds.max(axis=0)

        mask = np.all((coords >= mins) & (coords <= maxs), axis=1)
        coords = coords[mask]

        return cubic_cutout_from_atoms(coords, bounds, size=supercell, min_size=-3, margin=2)

