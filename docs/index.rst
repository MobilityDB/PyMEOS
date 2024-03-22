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

See the `installation documentation <./src/installation.html>`__
for more details and advanced installation instructions.

Examples
==================
A couple of examples showcasing the capabilities of PyMEOS can be found int the `examples section <./src/examples.html>`__.

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
