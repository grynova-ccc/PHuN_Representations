.. PHuN Representations documentation master file, created by
   sphinx-quickstart on Wed May 20 16:15:28 2026.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to the PHuN Representations documentation!
==================================================

PHuN Representations is a fun and computationally efficient Python
package for computing persistent homology using nets (PHuN)
representations of framework materials.

It enables the extraction of topological information for use as machine
learning descriptors.

**PHuN Representations** provides tools to compute persistent homology diagrams for framework materials using either:

* Atomic coordinates

* Topological nets derived from `CrystalNets.jl <https://coudertlab.github.io/CrystalNets.jl/dev/>`_.

It integrates with `Ripser <https://ripser.scikit-tda.org/en/latest/>`_ and `Gudhi <https://gudhi.inria.fr/>`_ to compute persistence diagrams and can extract topological descriptors that can be used in machine learning.

**PHuN Representations** can be used to:

* Generate persistent diagrams/images from CIF files

* Visualize persistence diagrams/images

* Extract vectorized topological descriptors (persistent image features and persistent statistics features)

For a complete example of usage, see the Usage Guide below.

Don't forget to also check out the corresponding `GitHub repository <https://github.com/grynova-ccc/PHuN_Representations.git>`_

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   installation
   usage_guide

.. toctree::
   :maxdepth: 2
   :caption: Documentation

   point_cloud
   persistent_homology
   feature_extraction
   
