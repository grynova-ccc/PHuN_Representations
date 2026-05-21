Computing Persistent Diagrams
===============================

Persistent diagrams are computed using the ``phun_reps.calc_persistent_diagram`` module.

The main function of ``phun_reps.calc_persistent_diagram`` is the
``calc_persistent_diagram`` function, which takes a list of point clouds and
returns a list of persistent diagrams.

Persistent diagrams can be computed using either:

- Alpha complexes, which forms topological spaces based on Delaunay triangulation
- Vietoris-Rips complexes, which forms topological spaces based of the distances between points in the point cloud.

Using Alpha complexes is recommended as they are more computationally efficient than Vietoris-Rips complexes and provide accurate representations for low-dimensional homology. 
However, Vietoris-Rips complexes can be useful in certain cases where the point cloud is very sparse or has a lot of noise.

This module also has functions for visualizing and saving the persistent diagrams.

Functions
---------

.. automodule:: phun_reps.calc_persistent_diagram
   :members:
   :undoc-members:
   :show-inheritance: