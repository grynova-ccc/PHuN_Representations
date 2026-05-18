import os
import pickle
import numpy as np
import matplotlib.pyplot as plt
import gudhi as gd
from ripser import Rips


def get_cif_files(folder, limit=None):
    """
    Retrieve all CIF files from a directory.

    Parameters
    ----------
    folder : str
        Path to directory containing .cif files.

    limit : int or None, optional
        Maximum number of files to return.
        If None, all files are returned.

    Returns
    -------
    list
        List of CIF file paths.
    """
    directory = os.fsencode(folder)
    cif_files = [
        os.path.join(folder, os.fsdecode(f))
        for f in os.listdir(directory)
        if os.fsdecode(f).endswith(".cif")
    ]
    if limit is None:
        return cif_files
    return cif_files[:limit]


def get_persistent_diagrams(dataset, maxdim=2, coeff=2, complex_type="alpha"):
    """
    Compute persistence diagrams from a point cloud.

    Supports:
    - Alpha complexes (via GUDHI)
    - Vietoris-Rips complexes (via ripser)

    Parameters
    ----------
    dataset : np.ndarray
        Point cloud coordinates with shape (N, D).

    maxdim : int, optional
        Maximum homology dimension to compute.
        Default is 2.

    coeff : int, optional
        Coefficient field for homology computations.
        Default is 2.

    complex_type : str, optional
        Type of simplicial complex:
            - "alpha"
            - "rips"

    Returns
    -------
    list
        List containing:
            [D0_diagram, D1_diagram, D2_diagram]
    """

    if complex_type == "alpha":
        ac = gd.AlphaComplex(points=dataset, precision="exact")
        st = ac.create_simplex_tree(max_alpha_square=float("inf"))
        st.persistence(homology_coeff_field=maxdim)

        dgms = [st.persistence_intervals_in_dimension(k) for k in range(st.dimension() + 1)]

        D0_dgm = dgms[0][~np.isinf(dgms[0]).any(1)]
        D1_dgm = dgms[1][~np.isinf(dgms[1]).any(1)]
        D2_dgm = dgms[2][~np.isinf(dgms[2]).any(1)] if len(dgms) > 2 else np.array([[0, 0]])

    elif complex_type == "rips":
        rips = Rips(maxdim=maxdim, coeff=coeff, verbose=False)
        dgms = rips.fit_transform(dataset)

        D0_dgm = dgms[0][~np.isinf(dgms[0]).any(1)]
        D1_dgm = dgms[1][~np.isinf(dgms[1]).any(1)]
        D2_dgm = dgms[2][~np.isinf(dgms[2]).any(1)] if len(dgms) > 2 else np.array([[0, 0]])

    else:
        raise ValueError("Complex type options: 'alpha' or 'rips'")

    print(f"H0: {len(D0_dgm)}, H1: {len(D1_dgm)}, H2: {len(D2_dgm)}")
    return [D0_dgm, D1_dgm, D2_dgm]


def calc_persistent_diagrams(dataset, file=None, top_net=None, maxdim=2, coeff=2, complex_type="alpha"):
    """
    Compute persistence diagrams and attach metadata.

    Parameters
    ----------
    dataset : np.ndarray
        Input point cloud.

    file : str or None, optional
        Associated filename.

    top_net : str or None, optional
        Optional topology label.

    maxdim : int,
        Maximum homology dimension.
        Default is 2.

    coeff : int, 
        Homology coefficient field.
        Default is 2.

    complex_type : str, 
        Persistence complex type:
            - "alpha"
            - "rips"
        Default is "alpha".

    Returns
    -------
    dict
        Dictionary containing:
            {"diagram": persistence diagrams, "filename": source filename, "net": topology label (optional)}
            """
    
    print(f"Processing data with shape {dataset.shape}")

    diagram = get_persistent_diagrams(
        dataset,
        maxdim=maxdim,
        coeff=coeff,
        complex_type=complex_type,
    )

    results = {
        "diagram": diagram,
        "filename": file,
    }

    if top_net is not None:
        results["net"] = top_net

    print("Processing complete.")
    return results


def save_diagrams(save_file, data):
    """
    Save persistence diagrams and metadata to disk.

    Parameters
    ----------
    save_file : str
        Output pickle filename.

    data : object
        Python object to serialize.
    """
    with open(save_file, "wb") as f:
        pickle.dump(data, f)
    print(f"Saved persistent diagrams to {save_file}")


def plot_persistent_diagrams(diagram_dicts, export_folder):
    """
    Plot and export persistence diagrams as PNG images.

    Parameters
    ----------
    diagram_dicts : list of dict
        List of dictionaries containing:
            {
                "diagram": persistence diagrams,
                "filename": source filename
            }

    export_folder : str
        Output directory for exported figures.
    """
    os.makedirs(export_folder, exist_ok=True)

    for item in diagram_dicts:
        diagrams = item.get("diagram", [])
        filename = item.get("filename", "unknown")

        empty = np.empty((0, 2))

        d0 = diagrams[0] if len(diagrams) > 0 and diagrams[0] is not None else empty
        d1 = diagrams[1] if len(diagrams) > 1 and diagrams[1] is not None else empty
        d2 = diagrams[2] if len(diagrams) > 2 and diagrams[2] is not None else empty

        finite_deaths = []

        for d in (d0, d1, d2):
            if isinstance(d, np.ndarray) and d.size > 0:
                deaths = d[:, 1]
                deaths = deaths[np.isfinite(deaths)]
                if deaths.size > 0:
                    finite_deaths.extend(deaths.tolist())

        max_death = max(finite_deaths) if finite_deaths else 1.0

        fig, ax = plt.subplots(figsize=(7, 7))
        ax.set_title("Persistence Diagram", fontsize=28, fontweight="bold")
        ax.set_xlabel("Birth", fontsize=26, fontweight="bold")
        ax.set_ylabel("Death", fontsize=26, fontweight="bold")

        ax.tick_params(axis="both", labelsize=24, width=2)
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_fontweight("bold")

        for spine in ax.spines.values():
            spine.set_linewidth(3)

        lim = max_death * 1.1
        ax.plot([0, lim], [0, lim], "k--", linewidth=3)

        if d0.size > 0:
            ax.scatter(d0[:, 0], d0[:, 1], c="#c00000", s=200, label="0D (Connected Components)")
        if d1.size > 0:
            ax.scatter(d1[:, 0], d1[:, 1], c="#1f497d", s=200, label="1D (Loops)")
        if d2.size > 0:
            ax.scatter(d2[:, 0], d2[:, 1], c="green", s=200, label="2D (Voids)")

        legend = ax.legend(fontsize=14, markerscale=1, frameon=False)
        for text in legend.get_texts():
            text.set_fontweight("bold")

        stem = os.path.basename(filename)
        outpath = os.path.join(export_folder, f"{stem}_persistence_diagram.png")

        plt.tight_layout()
        plt.savefig(outpath, dpi=300)
        plt.close(fig)
    os.makedirs(export_folder, exist_ok=True)
    print(f"Saved persistent diagram plots to {export_folder}")


