Installation
============

Built distributions
-------------------

Built distributions don't require compiling PyMEOS, PyMEOS CFFI or MEOS,
and can be installed using ``pip``.

Installation from PyPI
^^^^^^^^^^^^^^^^^^^^^^

PyMEOS and PyMEOS CFFI are available as binary distributions (wheel) for Linux (x64) and MacOS (x64 and arm64) platforms
on `PyPI <https://pypi.org/project/pymeos/>`__. The distributions include the most recent version of MEOS available at
the time of the PyMEOS release. Install the binary wheel with pip as follows:

.. code-block:: console

    pip install pymeos


Installation using conda
^^^^^^^^^^^^^^^^^^^^^^^^

PyMEOS is also available on the conda-forge channel.
First, set conda-forge as the priority channel:

.. code-block:: console

    conda config --add channels conda-forge
    conda config --set channel_priority strict

Then, install PyMEOS as follows:

.. code-block:: console

    conda install conda-forge::pymeos


Installation from source with custom MEOS library
-------------------------------------------------

If you want to use a specific MEOS version or a MEOS distribution that is
already present on your system, you can compile the PyMEOS packages from source yourself,
by directing pip to ignore the binary wheels.

Note that only PyMEOS CFFI will need to be compiled from sources,
since PyMEOS is a pure Python package and doesn't interact with MEOS directly.

First, make sure that MEOS is installed in your system. You can install it following the instructions
in the `MEOS documentation <https://github.com/MobilityDB/MobilityDB#building--installation>`__.

Then, install PyMEOS CFFI from source:

.. code-block:: console

    pip install pymeos-cffi --no-binary pymeos-cffi
    pip install pymeos


Updating the PyMEOS CFFI wrapper for custom MEOS library
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If your MEOS library API doesn't match the one used by the PyMEOS CFFI wrapper, it will crash. You can fix this
by updating the header file used by PyMEOS CFFI to match your MEOS version. To do so, you will need to recompile it
using the builder scripts provided in the ``pymeos_cffi`` package.

.. warning::
    While you can easily update ``pymeos_cffi``, you won't be able to do it so easily
    with ``pymeos``. If you want to use the ``pymeos`` library with your custom
    ``pymeos_cffi``, you should make sure that the part of the API used by ``pymeos``
    hasn't changed, or you'll get an import error when using ``pymeos``.

First, you will need to get the source code of PyMEOS CFFI. You can do so by downloading the source distribution
from PyPI, or by cloning the repository from GitHub:

.. code-block:: console

    git clone git@github.com:MobilityDB/PyMEOS.git
    cd PyMEOS/pymeos_cffi

Then, you will need to run the header builder script, which will generate a new header file based on the MEOS
version installed in your system. The script accepts two parameters, a path to the MEOS header file, and a path to your
MEOS library:

.. code-block:: console

    python3 ./pymeos_cffi/builder/build_header.py <path-to-header-file> <path-to-meos-library>

If no parameters are passed, the script will use the default header file and library path:

.. code-block:: console

    python3 ./pymeos_cffi/builder/build_header.py /usr/local/include/meos.h /usr/local/lib/libmeos.so

The second parameter is optional and is used to remove any function defined in the header file not exposed by the
library. If omitted, this step will not be performed.

Then, you have to generate the PyMEOS CFFI wrapper functions using the functions builder script:

.. code-block:: console

    python3 ./pymeos_cffi/builder/build_pymeos_functions.py

This will update the ``functions.py`` file that contains all the python functions exposed by the library.

Finally, you can install the updated PyMEOS CFFI package:

.. code-block:: console

    pip install .

