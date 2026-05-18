import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from persim import PersistenceImager


def get_max_birth_persistence(all_diagrams):
    """
    Compute global minimum and maximum birth/persistence values
    across all H1 and H2 persistence diagrams.

    Parameters
    ----------
    all_diagrams : list
        List of persistence diagram collections.
        Each entry is expected to contain:
            [H0_diagram, H1_diagram, H2_diagram]

    Returns
    -------
    max_birth, min_birth, max_persistence, min_persistence

    Notes
    -----
    Persistence is computed as:
        persistence = death - birth
    """

    max_birth = max_persistence = 0
    min_birth = min_persistence = np.inf

    for diagrams in all_diagrams:

        # Skip H0 and process only H1/H2
        for diagram in diagrams[1:]:

            if len(diagram) > 0:

                # Birth coordinates
                births = diagram[:, 0]

                # Persistence values
                persistences = diagram[:, 1] - diagram[:, 0]

                # Update global extrema
                max_birth = max(max_birth, np.max(births))
                max_persistence = max(max_persistence, np.max(persistences))

                min_birth = min(min_birth, np.min(births))
                min_persistence = min(min_persistence, np.min(persistences))

    return max_birth, min_birth, max_persistence, min_persistence

def create_persistent_images(diagrams, pimgr, save_path=None):
    """
    Convert H1 and H2 persistence diagrams into persistent images.

    Parameters
    ----------
    diagrams : list
        Persistence diagrams in the form:
            [H0_diagram, H1_diagram, H2_diagram]

    pimgr : PersistenceImager
        Configured PersistenceImager object.

    save_path : str or None, optional
        If provided, saves a visualization of the persistent images.

    Returns
    -------
    tuple
        (flattened_feature_vector, H1_feature_length, H2_feature_length)
    """

    # Extract H1 and H2 persistence diagrams
    _, d1_dgm, d2_dgm = diagrams

    # Convert diagrams into persistent image representations
    # skew=True converts (birth, death) -> (birth, persistence)
    d1_img = pimgr.transform(d1_dgm, skew=True)
    d2_img = pimgr.transform(d2_dgm, skew=True)

    if save_path:

        fig, axs = plt.subplots(1, 2, figsize=(12, 4))
        pimgr.plot_image(d1_img, ax=axs[0])
        axs[0].set_title("D1 Persistent Image")

        # Plot H2 persistent image
        pimgr.plot_image(d2_img, ax=axs[1])
        axs[1].set_title("D2 Persistent Image")

        # Improve spacing and save figure
        plt.tight_layout()
        plt.savefig(save_path)
        plt.close()

    # Combine H1 and H2 images into a single feature vector
    img_array = np.vstack([d1_img, d2_img]).ravel()

    return (img_array, len(np.vstack(d1_img).ravel()), len(np.vstack(d2_img).ravel()))

def calc_persistence_statistics(diagrams):
    """
    Compute summary statistics for each persistence diagram.

    Statistics include:
    - Number of points
    - Total persistence
    - Mean persistence
    - Variance of persistence
    - Maximum persistence
    - Minimum persistence

    Parameters
    ----------
    diagrams : list
        List of persistence diagrams.

    Returns
    -------
    dict
        Dictionary containing statistical features.
    """

    feature_dict = {}

    for i, dgm in enumerate(diagrams):

      
        if len(dgm) == 0:
            vals = [0] * 6

        else:
            # Compute persistence values
            persistences = dgm[:, 1] - dgm[:, 0]

            # Compute summary statistics
            vals = [
                len(persistences),          # Number of topological features
                np.sum(persistences),       # Total persistence
                np.mean(persistences),      # Mean persistence
                np.var(persistences),       # Variance
                np.max(persistences),       # Maximum persistence
                np.min(persistences),       # Minimum persistence
            ]

        keys = [f"D{i}_num_points", f"D{i}_total_persistence", f"D{i}_mean_persistence",
            f"D{i}_variance_persistence", f"D{i}_max_persistence", f"D{i}_min_persistence",]

        feature_dict.update(dict(zip(keys, vals)))

    return feature_dict

def get_persistent_stats_features(diagrams_dicts):
    """
    Generate persistence-statistics feature table.

    Parameters
    ----------
    diagrams_dicts : list of dict
        Each dictionary must contain:
            {"diagram": persistence_diagrams}

    Returns
    -------
    pandas.DataFrame
        Tabular persistence statistics features.
    """

    diagrams = [d["diagram"] for d in diagrams_dicts]

    rows = [calc_persistence_statistics(diagram) for diagram in diagrams]

    return pd.DataFrame(rows)

def calc_persistent_image_features(
    all_diagrams,
    filenames,
    export_folder=None,
    output_image_size=(50, 50),
    savefig=False,
):
    """
    Compute persistent-image feature vectors for a dataset.

    Parameters
    ----------
    all_diagrams : list
        Collection of persistence diagrams.

    filenames : list
        Corresponding structure filenames.

    export_folder : str or None, optional
        Folder for saving persistent-image plots.

    output_image_size : tuple, optional
        Persistent image resolution: (width, height)

    savefig : bool, optional
        If True, save persistent-image visualizations.

    Returns
    -------
    image_feature_vectors, H1_feature_length, H2_feature_length
    """

    max_birth, min_birth, max_persistence, min_persistence = get_max_birth_persistence(all_diagrams)

    print(
        f"Max birth: {max_birth}, Min birth: {min_birth}, "
        f"Max persistence: {max_persistence}, "
        f"Min persistence: {min_persistence}"
    )

    width, height = output_image_size

    # Compute pixel size so all images share the same resolution/grid
    pixel_size = min(
        (max_birth - min_birth) / width,
        (max_persistence - min_persistence) / height,
    )

    # Initialize persistence image transformer
    pimgr = PersistenceImager(birth_range=(0, max_birth), pers_range=(0, max_persistence), pixel_size=pixel_size)

    image_features = []

    for idx, diagram in enumerate(all_diagrams):

        basename = os.path.basename(filenames[idx])

        if savefig:
            os.makedirs(export_folder, exist_ok=True)
            save_path = (f"{export_folder}/{basename}_persistent_image.png")
        
        else:
            save_path = None

        features, D1_length, D2_length = create_persistent_images(diagram, pimgr, save_path=save_path)

        image_features.append(features)

    return image_features, D1_length, D2_length


def get_persistent_image_features(diagrams_dicts, output_size=(30, 30), savefig=False, export_folder=None):
    """
    Generate a DataFrame containing persistent-image features.

    Parameters
    ----------
    diagrams_dicts : list of dict
        Each dictionary must contain:
            {"diagram": persistence_diagrams,
             "filename": structure_filename}

    output_size : tuple, 
        Persistent image resolution:
            (width, height)
        Default is (30, 30).

    savefig : bool, optional
        If True, save persistent-image visualizations.

    export_folder : str or None, optional
        Directory used for image export.

    Returns
    -------
    pandas.DataFrame
        Persistent-image feature matrix.
    """

    # Extract diagrams and filenames
    diagrams = [d["diagram"] for d in diagrams_dicts]
    filenames = [d["filename"] for d in diagrams_dicts]

    # Compute persistent-image feature vectors
    image_features, H1_length, H2_length = calc_persistent_image_features( diagrams, filenames, output_image_size=output_size,
                                                                           export_folder=export_folder, savefig=savefig)
    # Convert feature list into NumPy array
    image_features = np.array(image_features)

    # Generate feature names for H1 image pixels
    image_column_names = [ f"D1_image_feature_{i+1}" for i in range(H1_length)]

    image_column_names += [ f"D2_image_feature_{i+1}" for i in range(H2_length)]
  
    return pd.DataFrame(image_features, columns=image_column_names)