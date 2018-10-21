=====
Usage
=====

Run from script
---------------

The fmu.config module is accessed through a script, which is run like this::

  fmuconfig global_master_config.yml <options...>

The global master config *shall* be placed at ``rNNN/share/config`` or
``rNNN/share/config/input``, where *rNNN* is
the revision number.

Here is an example of a shell script that runs `fmuconfig` from the rms/bin folder:

.. code-block:: bash

   #!/bin/bash
   #
   # Run the global configuration for RMS, both making IPL and YAML versions
   # from a common global config
   #
   source /project/res/SDP_bashrc

   MASTER="../../share/config/input/global_master_config.yml"
   DEST="../input/global_variables"
   TMPL="../../ert/input/templates"
   ROOTIPL="global_variables"
   ROOTYML="global_variables_rms"

   # run command for IPL version
   fmuconfig $MASTER --rootname $ROOTIPL --mode ipl --destination $DEST \
   --template $TMPL --tool rms

   # run command for YAML version
   fmuconfig $MASTER --rootname $ROOTYML --mode yml --destination $DEST \
   --template $TMPL --tool rms


Run from python inside or outside RMS
-------------------------------------

The config can also be ran from a python script, e.g. inside RMS. In that case you
need to initiate the Class instance and run a few methods. Here is an example:

.. code-block:: python

   import fmu.config

   cfg = fmu.config.ConfigParserFMU()

   global_master = '../../share/config/input/global_master_config.yml'
   path_ipl = '../input/global_variables'
   path_ipl_tmpl = '../../ert/input/templates'
   root_ipl = 'global_variables'

   root_yml = 'global_variables_rms'  # to avoid name conflict

   cfg.parse(global_master)

   # make IPL
   cfg.to_ipl(rootname=root_ipl, destination=path_ipl, template=path_ipl_tmpl,
              tool='rms')
   cfg.to_yaml(rootname=root_yml, destination=path_ipl, template=path_ipl_tmpl,
               tool='rms')

   print('\n\nGlobal IPL and YML are updated')




Learn by examples!
------------------

Learn the format by studying the following examples.
