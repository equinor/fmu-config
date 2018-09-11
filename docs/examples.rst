======================
Examples to learn from
======================

.. Notice that YAML files included are also input to testing
   and this secures consistency!

Below is a presentation of Troll config files

--------------------
Troll example config
--------------------

Troll has a large number of surfaces, and for convinience these lists
are places into separate files.


The main global config file
"""""""""""""""""""""""""""

.. literalinclude:: ../tests/data/yaml/troll2/global_master_config.yml
   :language: yaml

The include files
"""""""""""""""""
Note that the include files starts on indent level "zero".

rms_horizons.yml

.. literalinclude:: ../tests/data/yaml/troll2/rms_horizons.yml
   :language: yaml

rms_zones.yml

.. literalinclude:: ../tests/data/yaml/troll2/rms_zones.yml
   :language: yaml


------------------------
Sverdrup example config
------------------------
Note that these data are fake data

.. literalinclude:: ../tests/data/yaml/jsverdrup/global_master_config.yml
   :language: yaml

The includeded file:

.. literalinclude:: ../tests/data/yaml/jsverdrup/fwl2.yml
   :language: yaml


----------------------------------------
Using the config in RMS, IPL and Python
----------------------------------------

IPL example
"""""""""""
.. code-block:: bash

   Include("../input/global_variables/global_variables.ipl")

   FOR i FROM 1 TO TOP_LOBE.length DO
       Print("Reading ", TOP_LOBE[i])


Python example
""""""""""""""
.. code-block:: python

   import fmu.config.utilities as utils

   cfg = utils.yaml_load('../input/global_variables/global_variables_rms.yml')

   for toplobe in cfg['horizons']['TOP_LOBE']:
       print('Working with {}'.format(toplobe))