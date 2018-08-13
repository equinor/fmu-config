.. highlight:: shell

============
Installation
============


Stable release
--------------

The stable release of the scripts is distributed within Equinor, either through
/project/res or Komodo. *In practice* that will mean that **it is already installed for
you!**. The front-end to run is the ``fmuconfig`` script:

.. code-block:: console

    $ fmuconfig the_master_file.yml

From sources
------------

If you want to install i into your own virtual environment
from sources (rarely needed!)... If your want to contribute, see the `Contributing`
section.

The sources for fmu-config can be downloaded from the `Statoil Git repo`_.

You can either clone the public repository:

.. code-block:: console

    $ git clone git://git.statoil.no/fmu-utilities/fmu-config

Once you have a copy of the source, and you have a `virtual environment`_,
you can install it with:

.. code-block:: console

    $ make install

.. _Statoil Git repo: https://git.statoil.no/fmu-utilities/fmu-config
.. _virtual environment: http://docs.python-guide.org/en/latest/dev/virtualenvs/
