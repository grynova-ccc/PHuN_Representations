Determining Point Clouds
===============================

The point clouds are determined using the ``phun_reps.topology`` module.

The main function of ``phun_reps.topology`` is the
``PointCloudExtractor`` class, which takes a list of .cif files and
returns a list of point clouds.

Point clouds can be computed either from:

- atomic coordinates, taken directly from the .cif file, or
- topology-derived node positions identified using CrystalNets.jl

Functions
---------

.. automodule:: phun_reps.topology
   :members:
   :undoc-members:
   :show-inheritance: