==================================
YAML file and folders conventions
==================================

To summarize:

* YAML file endings is .yml

* Within the YAML master config file, the *small letters* headings are *reserved"* words, while
  *uppercase* letters means som kind of freeform variable.


Folder structure
----------------

This issue is *under discussion*!

Alternative 1, close to compatible with current
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To make it compatible with current FMU setups:

* Place the global_master_config.yml under ``share/config``

* Place shell scripts which runs fmuconfig under tool/bin, e.g. ``rms/bin``

* Output result to current standards, e.g. global_variables.ipl to
  ``rms/input/global_variables/global_variables.ipl`` and
  the templated version to ``ert/input/templates/global_variables.tmpl``


Alternative 2, a proposal for change
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The proposal is that all config files, both input and output,
are stored under ``share/config``

* ``share/config/input`` for user defined global_master_config.yml + include files if any
* ``share/config/bin`` for scripts, reading from input, results to output
* ``share/config/output`` for all outputs; to be machine read.

It would then be a good practice to delete all files on output everytime the
fmuconfig script is ran.

In practice it means that the link in the RMS IPL scripts must be changed to:

  include("../../share/config/output/global_variables.ipl")


File format and nested files
----------------------------

The master config file itself is a YAML formatted file. It follows the standard
YAML spesification, with *one major exception*, and that is that
*file nesting* is allowed. This allows for placing various parts of
the CONFIG into separate subfiles, which improves the overview.

The *derived* YAML files to e.g. be used by RMS Python will not allow nesting;
they will follow the standard.

What will be a good practice regarding nesting of the master config remains to see.

Some conventions
----------------

The examples section (next) should be studied in detail in order to
understand the format.

* The preferred name of the input global config is ``global_master_config.yml``.

* YAML is a indent based file type; which means changing the indentation
  may change the whole meaning of the file!

* The first level indentation is important. Important sections are:

  - ``global``: For general settings
  - ``rms``: For RMS related settings
  - ``eclipse``: For Eclipse related settings

* Notice the difference beteen small letters and uppercase letters
  - The small letters are YAML keywords with a special meaning.
  - Uppercase letters are "client" keywords (free form)

* The dates format shall be `ISO 8601`_ complient, on the form ``YYYY-MM-DD``.
  For file naming and IPL that date will be usually be compressed to
  the ``YYYYMMDD`` form, which is still in accordance with the ISO standard.

* Uncertainties are placed within numbers as these examples show:
  ``1.0 ~ <KH_MULT_MTR>`` or ``1.0~<KH_MULT_MTR>``. Notice that

  - First entry is the number that shall be used when running tests outside ERT,
    i.e. the *work* mode.
  - A tilde ``~`` is used to separate this number with an uncertainty identifier,
    which will be on the form ``<XXX>``, also called the *template* mode.
  - The files generated from this global master config, will either have the
    *work* form (e.g. 1.0 in this example) or the templated form (``<KH_MULT_MTR>``
    in this example). The alternate form may be present as a comment.

RMS related settings
--------------------

Whithin the ``rms`` section there may be 2 significant subheadings:

* horizons
* zones

Both of these may have the horizons list, that will usually (always?) never
contain uncertainties; they are just lists to facilitate looping with RMS
Python or IPL.

The rest of ``rms`` will be on so-called *freeform* format, where one needs to

* Have a identifier or variable name in **UPPERCASE**.
* Then specify (one indent level more) the

  - ``dtype`` (what kind of datatype; int, float, date, datepair, etc.)
  - ``value`` or ``values``: The single form ``value`` for single numbers, and the
    plural ``values`` form for lists.

Example of a freeform type with uncertainty alternative:

.. code-block:: yaml

  KH_MULT_MTR:
    dtype: float
    value: 1.0 ~ <KH_MULT_MTR>


Summary of Reserved words
--------------------------

Here is an ovwerview of reserved words (small letters), and the data values are also described
for some

.. code-block:: yaml

   authors: ['shortname1', 'shortname2']

   version: 1.0   # this is config file version

   global:
     name: Name of ypur field
     coordsys: OW_COORDSYS_ID

   rms:
     horizons:
     zones:

     ANYVARIABLE:
       dtype:  ... float/int/string/date/datepair
       value: a_scalar
       values: [...list...]

   eclipse:

Changes may occur!

.. _ISO 8601: https://en.wikipedia.org/wiki/ISO_8601
