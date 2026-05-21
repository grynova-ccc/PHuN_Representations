Extracting Features from Persistent Diagrams
===============================

Features are generated from the persistent diagrams using the ``phun_reps.feature_extraction`` module.

The main function of ``phun_reps.feature_extraction`` is to take a list of persistent diagrams and
return a pandas DataFrame containing feature vectors.

Persistent diagrams can be featurized using either:

- Persistence images, which converts the persistent diagram into a machine-readable image.
- Persistence statistics, which are a set of summary statistics that capture the overall shape of the persistent diagram, such as the number of points, the average birth and death times, and the maximum persistence.

The features are returned as a pandas DataFrame, where each row corresponds to a persistent diagram and each column corresponds to a feature.
This module also has functions for visualizing persistence images.

Functions
---------

.. automodule:: phun_reps.feature_extraction
   :members:
   :undoc-members:
   :show-inheritance: