===============================
The script library *fmu.config*
===============================


FMU config is a Python library to facilitate a global configuration in FMU.

The idea is that there is one global config file that will be the "mother"
of all other files, such as:

* global_variables.ipl
* global_variables.tmpl
* various eclipse file stubs (both "working" and template versions)

The global_config file shall be in YAML_ format, with extension ``.yml``

.. _YAML: https://en.wikipedia.org/wiki/YAML
