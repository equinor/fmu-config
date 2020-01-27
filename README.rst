===========================================
NB! Repo is now on github!! from 2019-12-17
===========================================

===============================
The script library *fmu.config*
===============================


FMU config is a Python library to facilitate a global configuration in FMU.

The idea is that there is one global config file that will be the "mother"
of all other files, such as:

* global_variables.ipl   (IPL file to run from RMS)
* global_variables.tmpl   (Templated IPL version; ERT will fill
  in <> variables)
* global_variables_work.yml   (working YAML file, with numbers)
* global_variables_tmpl.yml    (templated YAML file, with <...> instead of
  numbers; for ERT to process)
* various eclipse file stubs (both "working" and template versions)
* Working and templated files for other tools/scrips

The global_config file shall be in YAML_ format, with extension ``.yml``

For the FMU users, the front end script to run is ``fmuconfig``


.. _YAML: https://en.wikipedia.org/wiki/YAML
