.. PyMEOS documentation master file, created by
   sphinx-quickstart on Thu Oct  5 18:26:38 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=======
PyMEOS
=======

`MEOS (Mobility Engine, Open Source) <https://www.libmeos.org/>`__ is a
C library which enables the manipulation of temporal and spatio-temporal
data based on `MobilityDB <https://mobilitydb.com/>`__\ ’s data types
and functions.

PyMEOS is a library built on top of MEOS that provides all of its
functionality wrapped in a set of Python classes.

Requirements
============

PyMEOS 1.1 requires

* Python >=3.7
* MEOS >=1.1

Installing PyMEOS
==================

We recommend installing PyMEOS using one of the available built
distributions using ``pip``:

.. code-block:: console

    $ pip install pymeos

.. warning::
    Versions up to 1.1.2 of PyMEOS (0.0.8 of PyMEOS CFFI) should not be used. Instead,
    use version 1.1.3 (1.1.0 for PyMEOS CFFI) which is currently in pre-release mode.

    To use it, you have to use the ``--pre`` flag of ``pip``. To avoid installing
    pre-release versions of the dependencies, install ``pymeos`` normally and then
    update it using the following command:

    ``pip install --pre --force-reinstall --no-deps pymeos pymeos_cffi``

See the `installation documentation <https://pymeos.readthedocs.io/en/latest/src/installation.html>`__
for more details and advanced installation instructions.

.. toctree::
   :caption: User Guide
   :hidden:

   src/installation
   src/manual
   src/examples


.. toctree::
   :caption: API Reference
   :hidden:

   src/api/pymeos.meos_init
   src/api/pymeos.collections
   src/api/pymeos.temporal
   src/api/pymeos.main
   src/api/pymeos.boxes
   src/api/pymeos.aggregators
   src/api/pymeos.plotters
   src/api/pymeos.db

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
