Installation
===============================

Prerequisites
^^^^^^^^^^^^^
PHuN requires the `CrystalNets.jl Julia interface
<https://coudertlab.github.io/CrystalNets.jl/dev/python/>`_ Julia interface, which is used to identify and extract the topological nets of crystalline structures.

Installation
^^^^^^^^^^^^
Once you that Julia and CrystalNets.jl are installed, you can install PHuN representations using pip:

.. code-block:: bash

   pip install phun_reps

This package was built and tested with Python 3.10.13.

Dependencies installed automatically include:

- ``ase==3.26.0``
- ``Cython==3.2.0``
- ``juliacall==0.9.28``
- ``pandas==2.3.3``
- ``ripser==0.6.12``
- ``gudhi==3.11.0``

