Installation
============

Built distributions
-------------------

Built distributions don't require compiling PyMEOS, PyMEOS CFFI or MEOS,
and can be installed using ``pip``.

Installation from PyPI
^^^^^^^^^^^^^^^^^^^^^^

PyMEOS and PyMEOS CFFI are available as binary distributions (wheel) for Linux platforms on
`PyPI <https://pypi.org/project/pymeos/>`__. The distributions include the most recent version of MEOS available at the
time of the PyMEOS release. Install the binary wheel with pip as follows:

.. code-block:: console

    $ pip install pymeos

.. warning::
    Versions up to 1.1.2 of PyMEOS (0.0.8 of PyMEOS CFFI) should not be used. Instead,
    use version 1.1.3 (1.1.0 for PyMEOS CFFI) which is currently in pre-release mode.

    To use it, you have to use the ``--pre`` flag of ``pip``. To avoid installing
    pre-release versions of the dependencies, install ``pymeos`` normally and then
    update it using the following command:

    ``pip install --pre --force-reinstall --no-deps pymeos pymeos_cffi``


Installation using conda (incoming, not available yet)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

PyMEOS is available on the conda-forge channel. Install as follows::

    $ conda install pymeos --channel conda-forge


Installation from source with custom MEOS library
-------------------------------------------------

If you want to use a specific MEOS version or a MEOS distribution that is
already present on your system, you can compile the PyMEOS packages from source yourself,
by directing pip to ignore the binary wheels.

Note that only PyMEOS CFFI will need to be compiled from sources,
since PyMEOS is a pure Python package and doesn't interact with MEOS directly.

First, make sure that MEOS is installed in your system. You can install it following the instructions
in the `MEOS documentation <https://github.com/MobilityDB/MobilityDB#building--installation>`__.

Then, install PyMEOS CFFI from source::

    $ pip install pymeos-cffi --no-binary pymeos-cffi
    $ pip install pymeos


Updating the PyMEOS CFFI wrapper for custom MEOS library
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If your MEOS library API doesn't match the one used by the PyMEOS CFFI wrapper, it will crash. You can fix this
by updating the header file used by PyMEOS CFFI to match your MEOS version. To do so, you will need to recompile it
using the builder scripts provided in the ``pymeos_cffi`` package.

First, you will need to get the source code of PyMEOS CFFI. You can do so by downloading the source distribution
from PyPI, or by cloning the repository from GitHub::

    $ git clone git@github.com:MobilityDB/PyMEOS.git
    $ cd PyMEOS/pymeos_cffi

Then, you will need to run the header builder script, which will generate a new header file based on the MEOS
version installed in your system. The script accepts two parameters, a path to the MEOS header file, and a path to your
MEOS library::

    $ python3 ./pymeos_cffi/builder/build_header.py <path-to-header-file> <path-to-meos-library>

If no parameters are passed, the script will use the default header file and library path::

    $ python3 ./pymeos_cffi/builder/build_header.py /usr/local/include/meos.h /usr/local/lib/libmeos.so

The second parameter is optional and is used to remove any function defined in the header file not exposed by the
library. If omitted, this step will not be performed.

Then, you have to generate the PyMEOS CFFI wrapper functions using the functions builder script::

    $ python3 ./pymeos_cffi/builder/build_pymeos_functions.py

This will update the ``functions.py`` file that contains all the python functions exposed by the library.

Finally, you can install the updated PyMEOS CFFI package::

    $ pip install .
