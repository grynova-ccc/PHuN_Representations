User Guide
===============================

Our `GitHub repository <https://github.com/grynova-ccc/PHuN_Representations/tree/main/examples>`_, has a full example script with corresponding inputs and outputs, that demonstrate how to use PHuN to generate persistent homology features from .cif files. 

Below is a usage guide that walks through the different steps of the process and includes some background information on the different parameters and options that can be used.

Initial setup 
^^^^^^^^^^^^^
To use PHuN, you will need to have a folder containing .cif files of the structures you want to analyze. You can use the example .cif files in the `examples` folder on the GitHub repository or use your own .cif files.

.. code-block:: python

   # Folder containing .cif files to process
   folder = "test-cif"

Loading .cif files
^^^^^^^^^^^^^^^
.. code-block:: python

   import phun_reps.calc_persistent_diagram as cp
   # Load .cif files from the specified folder
   files = cp.get_cif_files(folder)

Extracting point clouds from .cif files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The point clouds are determined using the ``PointCloudExtractor`` class in the ``phun_reps.topology`` module.
This class handles the conversion of .cif files to point clouds and topological net identification. 

CrystalNets.jl is used to determine the topological net and generate the point cloud representations for persistent homology. 

Options for the CrystalNets.jl topology analysis can be built using the ``build_options`` function of the ``PointCloudExtractor`` class. See the `CrystalNets.jl documentation
<https://coudertlab.github.io/CrystalNets.jl/dev/lib/public/>`_ for more details on the available options.

For both, ACPH and PHuN point cloud generation, the supercell size can be specified to generate larger point clouds. For PHuN point cloud generation, the subnet mode can also be specified to determine how subnets are handled in the point cloud generation.

.. code-block:: python

   import phun_reps.topology as tp

   # Initate point cloud extraction
   extractor = tp.PointCloudExtractor()

   # Build CrystalNets.jl topology analysis options
   options = extractor.build_options(
    structure="MOF",              # Structure type
    clusterings=["SingleNodes"],  # Clustering strategy
    export_input=False,           # Do not export CrystalNets input
    export_net=False,             # Do not export identified net files
    export_subnets=False,         # Do not export subnet files
    detect_organiccycles=True)    # Detect organic cycles/rings
   
   # Generate point cloud representation for topological net
   # CrystalNets.jl is used to determine the topological net
   dataset, name = extractor.get_PHuN_points(file,options=options, supercell=None, subnet_mode="full")

The name of the topological net can also be determined

.. code-block:: python
    top_net = extractor.determine_topology(file, options=options)

The atomic coordinates of the .cif can also be used to generate a point cloud.

..  code-block:: python

   dataset, name = extractor.get_ACPH_points(file, supercell=None)

Computing persistent diagrams
^^^^^^^^^^^^^^^^^^^^^^^^^^^
After generating the point cloud representations, persistent homology diagrams can be computed using the ``calc_persistent_diagrams`` function in the ``phun_reps.calc_persistent_diagram`` module. This function takes a list of point clouds and returns a list of persistent diagrams.

You can specify use either Alpha (``alpha``) or Vietoris-Rips (``rips``) for computing the persistent homology. 

For framework materials, we recommend using alpha complexes as they are more computationally efficient and provide accurate representations for low-dimensional homology. However, Vietoris-Rips complexes can be useful in certain cases where the point cloud is very sparse or has a lot of noise.
If you're interested in learning more about how these are used to compute the persistent diagrams, we suggest reading `A roadmap for the computation of persistent homology <https://arxiv.org/abs/1506.08903>`_ by Otter `et al`. 

You can also specify the number of homology dimension computed and the coefficients field.
We recommend setting maximum homology dimension to compute can be set to 2 (D0, D1, and D2) for most applications in materials science, as higher-dimensional homology is often not as informative for these types of structures.
For a good introduction to these parameters, see the `Gudhi documentation <https://gudhi.inria.fr/doc/latest/topics.html>`_. 

.. code-block:: python

   import phun_reps.calc_persistent_diagram as cp
   # Compute persistent homology diagrams from the dataset
   diagrams = cp.calc_persistent_diagrams(
        dataset,
        file=name,
        top_net=top_net,
        maxdim=2,              # Compute D0, D1, and D2
        coeff=2,               # Z2 coefficients
        complex_type="alpha")  # Alpha complex

The persistent diagrams can be plotted and save

.. code-block:: python

   # Save all persistent diagrams as a pickle file
   cp.save_diagrams("persistent_diagrams.pkl", diagrams_list)

   # Export persistent diagram figures
   cp.plot_persistent_diagrams(diagrams_list, export_folder="diagrams")

Generating persistent image features
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Persistent images provide a way to featurize persistent diagrams by converting them into a machine-readable image. 
Persistent images are computed using the ``get_persistent_image_features`` function in the ``phun_reps.feature_extraction`` module. This function takes a list of persistent diagrams and returns a pandas DataFrame containing the persistent image features for each diagram. The resolution of the persistent images can be specified using the `output_size` parameter.

This module using the `persim` library to compute the persistent images. For more information on how persistent images are computed and how to choose the parameters, see the `persim documentation <https://persim.scikit-tda.org/en/latest/>`_.

.. code-block:: python

   import phun_reps.feature_extraction as fe
   image_features_df = fe.get_persistent_image_features(
    diagrams_list,
    output_size=(30, 30),     # Persistent image resolution
    savefig=True,             # Save persistent image figures
    export_folder="test_images")

Generating statistical features 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Statistical features provide a way to featurize persistent diagrams by computing summary statistics that capture the overall shape of the diagram. Statistical features are computed using the ``get_persistent_stats_features`` function in the ``phun_reps.feature_extraction`` module. This function takes a list of persistent diagrams and returns a pandas DataFrame containing the statistical features for each diagram.
This calculates, the number of points, total persistence, mean persistence, variance of persistence, maximum persistence, minimum persistence

.. code-block:: python

   import phun_reps.feature_extraction as fe
   stats_features_df = fe.get_persistent_stats_features(diagrams_list)

