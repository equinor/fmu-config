======================
Examples to learn from
======================

.. Notice that YAML files included are also input to testing
   and this secures consistency!

Below is a presentation of Troll config files

-------------
Troll example
-------------

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
