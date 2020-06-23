![fmu-config](https://github.com/equinor/fmu-config/workflows/fmu-config/badge.svg)

# The script library fmu.config #


FMU config is a small LGPL'ed licensed Python library to facilitate a configuration of global variables in Equinor's FMU setup.

The idea is that there is one global config file that will be the "mother"
of all other files, such as:

* global_variables.ipl   (IPL file to run from RMS)
* global_variables.ipl.tmpl   (Templated IPL version; [ERT](https://github.com/equinor/ert) will fill
  in <> variables)
* global_variables.yml   (working YAML file, with numbers)
* global_variables.yml.tmpl    (templated YAML file, with <...> instead of
  numbers; for ERT to process)
* Various eclipse file stubs (both "working" and template versions)
* Working and templated files for other tools/scrips

The global_config file shall be in YAML format, with extension ``.yml``

For the FMU users, the front end script to run is ``fmuconfig``

This software is released under LGPLv3.

Copyright 2018-2020 Equinor ASA.

