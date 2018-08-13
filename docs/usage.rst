=====
Usage
=====

Run from script
---------------

The fmu.config module is accessed through a script, which is ran like this::

  fmuconfig global_config.yml

The global config *shall* be placed at rXXX/share/config, where XXX is
the revision number.

File format and nested files
----------------------------

The config file itself is a YAML formatted file. It follows the standard
YAML spesification, with *one major exception*, and that is that
*file nesting* is allowed. This allows for placing various parts of
the CONFIG into separate subfiles.

What will be a good practice regarding this remains to see.

Some conventions
----------------

The examples section (next) should be studied in detail in order to
understand the format.

* YAML is a indent based file type; which means changing the indentation
  may change tha whole meaning of the file!

* The first level indentation is important. It can be

  - ``global``: For general settings
  - ``rms``: For RMS related settings
  - ``eclipse``: For Eclipse related settings

* Notice the difference beteen small letters and upprcase letters
  - The small letters are YAML keyword
  - Uppercase letters are "client" keywords or variables

* The dates format shall be `ISO 8601`_ complient, on the form ``YYYY-MM-DD``.
  For files that date will be usually be compressed to the ``YYYYMMDD`` form,
  which is still in accordance to the ISO standard.

* Uncertainties are placed within numbers as this examples show:
  ``1.0 ~ <KH_MULT_MTR>`` or ``1.0~<KH_MULT_MTR>``. Notice that

  - First entry is th number that shall be used when running tests outside ERT
  - A tilde ``~`` is used to seperate this number with an uncertainty identifier,
    which will be on the form ``<XXX>``.
  - The files generated from this global matser config, will either have the
    normal form (e.g. 1.0 in this example) or the templated form (<KH_MULT_MTR> in
    this example). The alternate form may be present as a comment.

RMS related settings
--------------------

Whithin the ``rms`` section there may be 2 significant subheadings:

* horizons
* zones

Both these may have horizons list, that will usually (always?) never contain uncertainties; they
are just lists to facilitate looping with RMS Python or IPL.

The rest of ``rms`` will be on socalled freeform format, where one need to

* Have a identifier or variable name in **UPPERCASE**.
* Then spesify (one indent level more) the

  - ``dtype`` (what kind of datatype; int, float, date, datepair, etc.)
  - ``value`` or ``values``: The single form ``value`` for single numbers, and the
    ``values`` form for lists.

Example of a freeform type:

.. code-block:: yaml

  KH_MULT_MTR:
    dtype: float
    value: 1.0 ~ <KH_MULT_MTR>



Learn by example!
-----------------

Learn the format by studying the following examples.



.. _ISO 8601: https://en.wikipedia.org/wiki/ISO_8601
